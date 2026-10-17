#!/usr/bin/env python3
"""Offline standalone contracts: disposable sources, synthetic PIDs, no sockets/models.

All launcher process probes/signals and HTTP commands are stubbed. The fake runtime
records arguments and exits; it is never a llama.cpp binary. No real PID is signalled.
"""
import ast
import importlib.util
import json
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

# This dispatcher deliberately has no socket/http/subprocess imports. Its process
# table is synthetic, including PIDs of short-lived recorder scripts already gone.
DISPATCH = r'''
import json, os, sys, time
from pathlib import Path
root = Path(os.environ['FAKE_ROOT']).resolve()
assert (root / '.synthetic-only').is_file()
name = Path(sys.argv[0]).name
args = sys.argv[1:]
table = root / 'processes.json'
def load():
    return json.loads(table.read_text())
def save(data):
    tmp = root / ('table-' + str(os.getpid()))
    tmp.write_text(json.dumps(data))
    tmp.replace(table)
def record(kind, **data):
    with (root / 'calls.jsonl').open('a') as f:
        f.write(json.dumps(dict(kind=kind, **data)) + '\n')
if name in ('llama-server', 'node'):
    if (root / 'exit-at-load').exists(): sys.exit(1)
    port = args[args.index('--port') + 1]
    command = str(root / '.loom/runtime/loom-uopt002/llama-server')
    if name == 'node': command = 'node ' + args[0]
    data = load()
    data[str(os.getpid())] = dict(command=command, port=port, role=name)
    save(data)
    record('launch', role=name, args=args, pid=os.getpid(),
           sidecar=os.environ.get('LOOM_EXPERT_MAJOR_SIDECAR'),
           ci=os.environ.get('LOOM_CONTEXT_WEBUI_CI'))
    sys.exit(0)
if name == 'kill-stub':
    assert len(args) == 2 if args[0] == '-0' else len(args) == 1
    pid = args[-1]
    data = load()
    if args[0] == '-0': sys.exit(0 if pid in data else 1)
    record('signal', pid=pid)
    if pid not in data: sys.exit(1)
    if (root / 'refuse-stop').exists(): sys.exit(1)
    del data[pid]
    save(data)
    sys.exit(0)
if name == 'ps':
    if (root / 'probe-unavailable').exists(): sys.exit(1)
    pid = args[args.index('-p') + 1]
    data = load()
    if pid not in data: sys.exit(1)
    print(data[pid]['command'])
    sys.exit(0)
if name == 'pgrep': sys.exit(0 if (root / 'foreign-model').exists() else 1)
if name == 'lsof':
    marker = root / 'occupied-port'
    occupied = marker.read_text().strip() if marker.exists() else None
    sys.exit(0 if occupied is not None and (not occupied or '-iTCP:' + occupied in args) else 1)
if name == 'curl':
    url = args[-1]
    assert url.startswith('http://127.0.0.1:') and url.endswith('/health')
    port = url.split(':')[-1].split('/')[0]
    record('health', port=port)
    if (root / 'unhealthy').exists(): sys.exit(22)
    sys.exit(0 if any(p['port'] == port for p in load().values()) else 7)
if name == 'sleep': time.sleep(.01); sys.exit(0)
if name == 'seq':
    print('\n'.join(str(n) for n in range(1, min(int(args[-1]), 12) + 1)))
    sys.exit(0)
raise AssertionError('unstubbed command ' + name)
'''

# Execute the unchanged public gateway with in-memory HTTP/filesystem mocks. The
# listen/request/pipe calls never reach node:http or any active localhost port.
GATEWAY_VM = r'''
const fs = require('node:fs'), vm = require('node:vm');
const {EventEmitter} = require('node:events');
const source = fs.readFileSync(process.argv[1], 'utf8')
  .replace(/^#!.*\n/, '').replace(/^import .*;\n/gm, '');
(async () => {
  for (const ci of ['0', '1']) {
    let handler, listened = false, sent, piped = false;
    const writes = [];
    const http = {
      createServer(fn) { handler = fn; return {
        on() {}, listen(options, cb) {
          if (options.host !== '127.0.0.1' || options.port !== 36400) throw Error('bind contract');
          listened = true; cb();
        }
      }; },
      request(options, cb) {
        if (options.port !== 36401) throw Error('backend contract');
        return {on() {}, end(body) {
          sent = body.toString();
          cb({statusCode: 200, headers: {}, pipe(response) {piped = true; response.end('synthetic');}});
        }};
      }
    };
    const context = {
      http, Buffer, URL, performance, console: {log() {}, error() {}},
      process: {argv: ['node', 'gateway', '--host', '127.0.0.1', '--port', '36400',
        '--backend-host', '127.0.0.1', '--backend-port', '36401'],
        env: {HOME: '/synthetic-home', LOOM_CONTEXT_WEBUI_CI: ci,
          LOOM_CONTEXT_WEBUI_RUNTIME_DIR: '/synthetic-state'}},
      homedir: () => '/synthetic-home', join: (...parts) => parts.join('/'),
      pathToFileURL() {throw Error('synthetic unavailable optional core');},
      mkdirSync() {}, appendFileSync(path, row) {writes.push(JSON.parse(row));}
    };
    await vm.runInNewContext('(async () => {\n' + source + '\n})()', context);
    const req = new EventEmitter();
    Object.assign(req, {method: 'POST', url: '/v1/chat/completions', headers: {}});
    const response = {writeHead() {}, end(value) {this.value = value;}};
    const body = JSON.stringify({messages: [{role: 'user', content: 'synthetic'}]});
    const done = handler(req, response);
    req.emit('data', Buffer.from(body)); req.emit('end'); await done;
    if (!listened || sent !== body || !piped || response.value !== 'synthetic') throw Error('proxy contract');
    const row = writes[0];
    if (row.coreStatus !== (ci === '0' ? 'disabled' : 'unavailable')) throw Error('core status');
    if (row.reason !== (ci === '0' ? 'ci-disabled' : 'canonical-core-unavailable')) throw Error('bypass');
    if (JSON.stringify(row).includes('synthetic"')) throw Error('raw body in accounting');
  }
  console.log('PASS gateway disabled/missing-core fail-open and synthetic stream piping');
})().catch(e => {console.error(e); process.exitCode = 1;});
'''


class ProfilesTest(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='loom-source-only-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name).resolve()
        self.bin = self.root / 'mocks'
        self.bin.mkdir()
        (self.root / '.synthetic-only').touch()
        (self.root / 'processes.json').write_text('{}')
        for rel in ('scripts/loom-deep', 'config/loom-deep-profiles.env',
                    'scripts/loom-context-webui-gateway.mjs'):
            dest = self.root / rel
            dest.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(ROOT / rel, dest)
        dispatcher = self.bin / 'dispatch'
        dispatcher.write_text('#!' + sys.executable + '\n' + DISPATCH)
        dispatcher.chmod(0o755)
        for name in ('kill-stub', 'ps', 'pgrep', 'lsof', 'curl', 'node', 'sleep', 'seq'):
            (self.bin / name).symlink_to(dispatcher)
        # No fallback PATH: only these required, non-network utility executables.
        for name in ('bash', 'dirname', 'mkdir', 'rmdir', 'rm', 'mv', 'env'):
            executable = shutil.which(name)
            self.assertIsNotNone(executable, name)
            (self.bin / name).symlink_to(executable)
        (self.bin / 'python3').symlink_to(sys.executable)
        home = self.root / 'home'
        home.mkdir()
        bash_env = self.root / 'bash-env'
        bash_env.write_text('kill() { "$FAKE_ROOT/mocks/kill-stub" "$@"; }\n')
        self.env = dict(PATH=str(self.bin), HOME=str(home), TMPDIR=str(self.root),
                        FAKE_ROOT=str(self.root), BASH_ENV=str(bash_env),
                        LC_ALL='C', PYTHONDONTWRITEBYTECODE='1',
                        LOOM_CONTEXT_WEBUI_GATEWAY='0')
        self.state = self.root / '.loom/runtime/loom-deep'
        self.runtime = self.root / '.loom/runtime/loom-uopt002'
        self.model = self.root / 'models/loom-deep-30b-unlocked.gguf'
        self.sidecar = self.root / 'models/unlocked-expert-major-v1.bin'

    def provision_fake(self):
        self.runtime.mkdir(parents=True)
        self.model.parent.mkdir()
        self.model.touch()
        self.sidecar.touch()
        (self.runtime / 'llama-server').symlink_to(self.bin / 'dispatch')
        # argv[0] remains the fixture path, basename llama-server, not real binary.

    def run_launcher(self, *args, ok=True, contains=None):
        result = subprocess.run([str(self.root / 'scripts/loom-deep'), *args],
                                cwd=self.root, env=self.env, capture_output=True,
                                text=True, timeout=15)
        self.assertEqual(result.returncode == 0, ok, result.stdout + result.stderr)
        output = result.stdout + result.stderr
        if contains is not None:
            self.assertIn(contains, output)
        return output

    def calls(self, kind):
        p = self.root / 'calls.jsonl'
        return [r for r in map(json.loads, p.read_text().splitlines()) if r['kind'] == kind] if p.exists() else []

    def processes(self):
        return json.loads((self.root / 'processes.json').read_text())

    def add_process(self, pid='900001', command='foreign-command'):
        (self.root / 'processes.json').write_text(json.dumps({pid: dict(command=command, port='36400')}))
        return pid

    def test_profiles_and_explicit_lifecycle(self):
        self.provision_fake()
        self.env.pop('LOOM_CONTEXT_WEBUI_GATEWAY')
        self.run_launcher('current', contains='context-webui-gateway: 1')
        self.env['LOOM_CONTEXT_WEBUI_GATEWAY'] = '0'
        self.run_launcher('current', contains='context: 4096')
        self.run_launcher('use', 'unlocked-s32', contains='selected: unlocked-s32')
        self.run_launcher('current', contains='moe-slots: 32')
        self.run_launcher('use', 'unlocked-8k')
        current = self.run_launcher('current')
        for field in ('context: 8192', 'batch: 4096', 'ubatch: 4', 'moe-slots: 40',
                      'moe-layers: 48', 'cache-ram: 512', 'kv-k: q8_0', 'kv-v: f16',
                      'flash-attention: off', 'context-webui-gateway: 0', 'parallel: 1'):
            self.assertIn(field, current)
        self.env['LOOM_CONTEXT_WEBUI_GATEWAY'] = '1'
        self.run_launcher('start')
        launch = self.calls('launch')[-1]
        args = launch['args']
        for flag, value in (('--ctx-size', '8192'), ('-b', '4096'), ('-ub', '4'),
                            ('--cache-type-k', 'q8_0'), ('--cache-type-v', 'f16'),
                            ('--flash-attn', 'off'), ('--host', '127.0.0.1'), ('--port', '18080')):
            self.assertEqual(args[args.index(flag) + 1], value)
        for flag in ('--offline', '--cpu-moe', '--no-mmap'):
            self.assertIn(flag, args)
        self.assertEqual(launch['sidecar'], str(self.sidecar))
        pid = (self.state / 'llama-server.pid').read_text()
        self.run_launcher('start', contains='already running')
        self.run_launcher('use', 'unlocked')
        self.assertEqual((self.state / 'llama-server.pid').read_text(), pid)
        self.run_launcher('current', contains='running-profile: unlocked-8k')
        self.run_launcher('status', contains='unlocked-8k')
        self.run_launcher('health')
        self.run_launcher('start', ok=False, contains='differs')
        self.run_launcher('stop')
        self.assertEqual(self.processes(), {})
        self.env['LOOM_CONTEXT_WEBUI_GATEWAY'] = '0'
        for profile, slots in (('unlocked', '40'), ('unlocked-s32', '32')):
            self.run_launcher('use', profile)
            self.run_launcher('start')
            args = self.calls('launch')[-1]['args']
            for flag, expected in (('--ctx-size', '4096'), ('-b', '4096'), ('--moe-n-slots', slots)):
                self.assertEqual(args[args.index(flag) + 1], expected)
            self.assertNotIn('--cache-type-k', args)
            self.assertNotIn('--flash-attn', args)
            self.run_launcher('stop')
        self.run_launcher('status', ok=False, contains='not running')

    def test_clean_source_bootstrap_without_assets(self):
        self.assertFalse((self.root / '.loom').exists())
        self.assertFalse(self.model.exists())
        self.run_launcher('current', contains='selected: unlocked ')
        self.run_launcher('use', 'unlocked-8k')
        self.run_launcher('start', ok=False, contains='missing model')
        self.assertEqual(self.calls('launch'), [])
        self.assertFalse((self.state / 'lifecycle.lock').exists())
        self.assertFalse((self.root / '.loom/runtime/llama.cpp').exists())

    def test_missing_config_and_invalid_configuration(self):
        config = self.root / 'config/loom-deep-profiles.env'
        original = config.read_text()
        config.unlink()
        self.run_launcher('start', ok=False, contains='missing standalone configuration')
        for suffix, message in (('\nLOOM_DEEP_CTX=""\n', 'missing configuration value'),
                                ('\nLOOM_DEEP_PORT="invalid"\n', 'invalid numeric configuration'),
                                ('\nLOOM_DEEP_PORT="99999"\n', 'invalid standalone ports'),
                                ('\nLOOM_DEEP_HOST="0.0.0.0"\n', 'requires loopback')):
            config.write_text(original + suffix)
            self.run_launcher('start', ok=False, contains=message)
        self.assertEqual(self.calls('launch'), [])

    def test_invalid_selection_does_not_mutate_profile(self):
        self.run_launcher('use', 'unlocked')
        profile = self.root / '.loom/loom-deep-profile'
        original = profile.read_text()
        self.run_launcher('use', 'invalid', ok=False, contains='usage:')
        self.assertEqual(profile.read_text(), original)
        profile.write_text('invalid\n')
        self.run_launcher('start', ok=False, contains='only unlocked')
        self.assertEqual(self.calls('launch'), [])

    def test_missing_artifact_and_executable_fail_closed(self):
        self.provision_fake()
        self.sidecar.unlink()
        self.run_launcher('start', ok=False, contains='missing UOPT-002 sidecar')
        self.sidecar.touch()
        (self.runtime / 'llama-server').unlink()
        self.run_launcher('start', ok=False, contains='missing executable UOPT-002 runtime')
        self.runtime.rmdir()
        self.run_launcher('start', ok=False, contains='missing UOPT-002 runtime libraries')
        self.assertEqual(self.calls('launch'), [])

    def test_missing_commands_and_gateway_fail_before_launch(self):
        self.provision_fake()
        for name in ('curl', 'lsof', 'pgrep', 'python3', 'ps'):
            p = self.bin / name
            dest = p.readlink()
            p.unlink()
            self.run_launcher('start', ok=False, contains='missing standalone dependency: ' + name)
            p.symlink_to(dest)
        self.env['LOOM_CONTEXT_WEBUI_GATEWAY'] = '1'
        (self.bin / 'node').unlink()
        self.run_launcher('start', ok=False, contains='missing standalone dependency: node')
        (self.bin / 'node').symlink_to(self.bin / 'dispatch')
        (self.root / 'scripts/loom-context-webui-gateway.mjs').unlink()
        self.run_launcher('start', ok=False, contains='missing Context WebUI gateway')
        self.assertEqual(self.calls('launch'), [])

    def test_foreign_process_occupied_port_and_lock(self):
        self.provision_fake()
        for marker, message in (('foreign-model', 'another model process'), ('occupied-port', 'already occupied')):
            p = self.root / marker
            p.touch()
            self.run_launcher('start', ok=False, contains=message)
            p.unlink()
        (self.state / 'lifecycle.lock').mkdir()
        self.run_launcher('start', ok=False, contains='another lifecycle operation')
        self.assertEqual(self.calls('launch'), [])
        self.assertEqual(self.calls('signal'), [])

    def test_stale_reused_and_malformed_pid_never_signalled(self):
        self.provision_fake()
        self.run_launcher('current')
        pid_file = self.state / 'llama-server.pid'
        for pid in ('-1', '0', '1', 'not-a-pid'):
            pid_file.write_text(pid)
            self.run_launcher('stop', ok=False, contains='invalid managed PID')
        pid_file.write_text(self.add_process())
        self.run_launcher('start', ok=False, contains='not the expected standalone process')
        self.run_launcher('stop', ok=False, contains='not the expected standalone process')
        self.assertEqual(self.calls('signal'), [])
        # A dead numeric PID is harmless; no signal, stale metadata may be pruned.
        (self.root / 'processes.json').write_text('{}')
        self.run_launcher('stop')
        self.assertEqual(self.calls('signal'), [])

    def test_failed_health_cleanup_and_no_retry(self):
        self.provision_fake()
        (self.root / 'unhealthy').touch()
        self.run_launcher('start', ok=False, contains='did not become healthy')
        self.assertEqual(len(self.calls('launch')), 1)
        self.assertEqual(self.processes(), {})
        self.assertFalse((self.state / 'lifecycle.lock').exists())

    def test_child_exit_at_load_does_not_report_ready(self):
        self.provision_fake()
        (self.root / 'exit-at-load').touch()
        self.run_launcher('start', ok=False, contains='did not become healthy')
        self.assertFalse((self.state / 'profile').exists())
        self.assertEqual(self.processes(), {})
        self.assertEqual(self.calls('signal'), [])

    def test_missing_running_metadata_refuses_start(self):
        self.provision_fake()
        self.run_launcher('start')
        (self.state / 'profile').unlink()
        self.run_launcher('start', ok=False, contains='missing running profile')
        self.assertEqual(len(self.calls('launch')), 1)
        self.run_launcher('stop')

    def test_unavailable_ownership_probe_never_signals(self):
        self.provision_fake()
        self.run_launcher('start')
        (self.root / 'probe-unavailable').touch()
        self.run_launcher('stop', ok=False, contains='cannot verify managed PID ownership')
        self.assertEqual(self.calls('signal'), [])
        (self.root / 'probe-unavailable').unlink()
        self.run_launcher('stop')

    def test_occupied_backend_port_blocks_gateway_before_load(self):
        self.provision_fake()
        self.env['LOOM_CONTEXT_WEBUI_GATEWAY'] = '1'
        (self.root / 'occupied-port').write_text('18081')
        self.run_launcher('start', ok=False, contains='port 18081 is already occupied')
        self.assertEqual(self.calls('launch'), [])
        self.assertEqual(self.calls('signal'), [])

    def test_status_health_failure_is_not_pass(self):
        self.provision_fake()
        self.run_launcher('start')
        (self.root / 'unhealthy').touch()
        self.run_launcher('health', ok=False)
        self.run_launcher('stop')

    def test_stop_failure_blocks_new_load_without_sigkill(self):
        self.provision_fake()
        self.run_launcher('start')
        (self.root / 'refuse-stop').touch()
        self.run_launcher('stop', ok=False, contains='refusing to SIGKILL')
        self.run_launcher('use', 'unlocked-s32')
        self.run_launcher('start', ok=False, contains='differs')
        self.assertEqual(len(self.calls('launch')), 1)
        (self.root / 'refuse-stop').unlink()
        self.run_launcher('stop')
        self.assertEqual(self.processes(), {})

    def test_partial_service_refuses_start(self):
        self.provision_fake()
        self.run_launcher('current')
        pid = self.add_process(command=str(self.runtime / 'llama-server'))
        (self.state / 'llama-server-backend.pid').write_text(pid)
        self.run_launcher('start', ok=False, contains='partial service')
        self.assertEqual(self.calls('launch'), [])
        self.run_launcher('stop')

    def test_gateway_launch_and_shutdown_contract(self):
        self.provision_fake()
        self.env['LOOM_CONTEXT_WEBUI_GATEWAY'] = '1'
        self.env['LOOM_CONTEXT_WEBUI_CI'] = '0'
        self.run_launcher('start')
        launches = self.calls('launch')
        self.assertEqual([r['role'] for r in launches], ['llama-server', 'node'])
        self.assertEqual(launches[0]['args'][launches[0]['args'].index('--port') + 1], '18081')
        self.assertEqual(launches[1]['ci'], '0')
        self.run_launcher('health')
        self.run_launcher('stop')
        self.assertEqual([r['pid'] for r in self.calls('signal')],
                         [str(launches[1]['pid']), str(launches[0]['pid'])])
        self.assertEqual(self.processes(), {})

    def test_gateway_optional_core_in_memory(self):
        node = shutil.which('node')
        self.assertIsNotNone(node, 'Node is required for this optional-gateway validation; not a skipped PASS')
        result = subprocess.run([node, '-e', GATEWAY_VM,
                                 str(ROOT / 'scripts/loom-context-webui-gateway.mjs')],
                                cwd=self.root, env={'PATH': str(self.bin), 'HOME': str(self.root / 'home')},
                                capture_output=True, text=True, timeout=15)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn('PASS gateway', result.stdout)

    def test_syntax_and_import_without_running_tests(self):
        source = Path(__file__).read_text()
        ast.parse(source)
        module = importlib.util.module_from_spec(importlib.util.spec_from_loader('loom_test_import', loader=None))
        module.__file__ = str(Path(__file__))
        exec(compile(source, str(Path(__file__)), 'exec'), module.__dict__)
        self.assertTrue(hasattr(module, 'ProfilesTest'))
        result = subprocess.run([str(self.bin / 'bash'), '-n', str(self.root / 'scripts/loom-deep')],
                                env=self.env, capture_output=True, text=True, timeout=5)
        self.assertEqual(result.returncode, 0, result.stderr)


if __name__ == '__main__':
    unittest.main()
