# LOOM standalone: source adapter and offline validation

## Scope and readiness

This package provides the `scripts/loom-deep` shell lifecycle adapter, repository-relative configuration, public UOPT-002 runtime patch/build references, and synthetic offline tests. It is **source-only**, not a binary distribution or a fresh-clone 30B chat installation.

It does not contain models, expert sidecars, patched executables, runtime libraries, private Pi configuration, or a multi-model deployment manager. A public standalone checkout installs only the source adapter and supporting sources, not a complete serving deployment. Do not run this launcher's lifecycle commands in an existing operational checkout just to validate source changes.

Source-only validation uses no model, GPU, listening socket, external service, or private runtime. Real compilation, artifact provisioning, model compatibility, Metal behavior and end-to-end inference remain separate, unverified prerequisites of a deployment. Historical benchmark records are not new acceptance results for this package.

## Environment and requirements

Reference platform: macOS on Apple Silicon. The source-only tests have been checked with the macOS Bash 3.2 interface, Python 3.14 and Node 25; other versions/platforms are not certified. Python 3.9+ is required by the test harness (`Path.readlink`). Node 18+ is the intended gateway/test interface; only the recorded version has been exercised.

- Shell adapter: Bash and standard utilities (`dirname`, `mkdir`, `rmdir`, `rm`, `mv`, `seq`, `sleep`, `env`), plus `ps`, `pgrep`, `lsof`, `curl` and Python 3 for startup preflight.
- Direct serving: the compatible patched UOPT-002 `llama-server`, its corresponding libraries, the exact compatible GGUF and lossless expert-major sidecar described below.
- Gateway serving: Node and `scripts/loom-context-webui-gateway.mjs` in addition to the direct-serving artifacts.
- Optional Context Intelligence: a separately installed, trusted Pi2 core. It is **not a requirement for direct serving or gateway pass-through**.
- Native runtime build, if independently authorized: Git, `patch`, CMake, a C++ toolchain and the fork's Apple Metal build prerequisites. No native build is performed by the offline tests.

Linux, Windows, Intel macOS, arbitrary llama.cpp releases and alternative GGUFs are not qualified by these tests. DYLD handling and the external-volume sidecar restriction are intentional macOS assumptions, not cross-platform portability guarantees.

## Reproducible source-only bootstrap (no provisioning)

Use a new source checkout with no operational `.loom` directory. Obtain only the reviewed sources and the repository's existing MIT license. No pip/npm install, model download, compiler invocation or global Pi setup is needed for this validation:

```bash
bash -n scripts/loom-deep
bash -n config/loom-deep-profiles.env
PYTHONDONTWRITEBYTECODE=1 python3 scripts/test_loom_deep_profiles.py -v
```

The test module imports Python standard-library modules only. It copies selected public sources into disposable paths and generates **empty** model-named fixtures. Its `llama-server` is a short-lived argument recorder, never a native model runtime. Its process table, signals, HTTP health checks and gateway process are synthetic. A restricted command path and a test-owned Bash environment prevent probes or signals from reaching real processes. The optional gateway's unchanged source is also evaluated with in-memory HTTP/filesystem mocks: `listen`, `request` and stream piping never open sockets.

Tests cover 4K/S32/8K flags, selection versus running state, explicit switching, missing/invalid configuration, dependencies, foreign processes, occupied ports, stale/malformed PID ownership, failed health, failed shutdown and gateway pass-through without the optional core. Node must be installed to run the gateway validation; absence is a failure, not a skipped PASS. Synthetic health and process tests do not prove real HTTP interoperability or GPU safety.

The harness has bounded subprocess timeouts, an isolated HOME/TMPDIR and no fallback executable search path for launcher commands. Temporary fixture cleanup does not delete project assets. It does not use the active ports or call an inference endpoint. The old context-memory utility tests are a separate subsystem and are not prerequisites for direct standalone serving.

## Profiles and configuration resolution

The launcher resolves its repository root from its own script path and sources **trusted shell code** in `config/loom-deep-profiles.env`. Missing values, invalid numeric settings, non-loopback host and invalid ports fail closed. This is not a parser for untrusted configuration.

| Selection | Context | Expert slots | KV / attention | Gateway |
| --- | ---: | ---: | --- | --- |
| `unlocked` (standalone default) | 4096 | 40 | original runtime defaults | default on, can be disabled |
| `unlocked-s32` | 4096 | 32 | original runtime defaults | default on, can be disabled |
| `unlocked-8k` (explicit opt-in) | 8192 | 40 | K `q8_0`, V `f16`, Flash Attention off | always bypassed |

All profiles retain one parallel sequence, 48 MoE layers, logical batch 4096, ubatch 4, cache RAM 512 MiB, CPU-MoE/no-mmap, offline/no-warmup and loopback binding. Capacity 8192 is an argument contract, not proof that every 8K prompt is practical on an 8 GiB Mac. Long 30B prefill can be very slow. Do not extrapolate historic speed/quality numbers to a new build or change ubatch to claim improved performance.

The default stays 4K for the standalone adapter; 8K requires explicit selection. A new selection is stored in `.loom/loom-deep-profile`. Status, PID files and logs live under `.loom/runtime/loom-deep/`. Even `current` initializes directories; use the synthetic tests, not production lifecycle commands, for read-only source review.

Configuration contains fixed repository-relative model/runtime paths, not private absolute paths. The supported environment controls are:

- `LOOM_CONTEXT_WEBUI_GATEWAY=0`: direct 4K/S32 serving; 8K forces this mode regardless of the environment.
- `LOOM_CONTEXT_WEBUI_CI=0`: gateway without the optional Pi2 packer.
- `LOOM_CONTEXT_WEBUI_ACCOUNTING=0`: disable gateway accounting.
- `LOOM_PI2_CONTEXT_CORE`: optional trusted module path if you deliberately enable a separately installed core.
- `DYLD_LIBRARY_PATH`: the adapter prepends its runtime library directory; do not inherit untrusted library paths.

Model/runtime paths and numeric profile values are sourced from the repository config, not arbitrary environment overrides. Keep that file trusted. Configuration from a different deployment is not a supported substitute for this package's configuration.

## Optional gateway and Pi2 core

The historical default 4K route uses a public Node gateway on `127.0.0.1:18080` and a backend on `127.0.0.1:18081`. It attempts to import the optional Pi2 core from the configured path or the user's Pi extension directory. If unavailable, it **fails open to pass-through**; it does not provide Context Intelligence. That mode and an explicit CI-disabled mode are covered by in-memory tests, not real HTTP or model acceptance.

For an independently provisioned standalone deployment, a genuinely independent path is:

```bash
# FUTURE operator actions only, in an independently provisioned installation.
LOOM_CONTEXT_WEBUI_GATEWAY=0 scripts/loom-deep start
```

The direct path needs no Node or Pi2 module. Alternatively, with the gateway dependencies provisioned:

```bash
LOOM_CONTEXT_WEBUI_CI=0 scripts/loom-deep start
```

The external core's implementation, redaction and generated recovery artifacts are outside this source package's qualification. A missing core is not silently reported as functioning CI. No Pi model registry, global extension or home-directory configuration is installed by the source tests.

## Real-runtime prerequisites: separate, authorized provisioning

**Not executed or certified by source-only validation.** A clean source checkout intentionally lacks the following artifacts:

| Required artifact | Repository-relative path | Historical registered SHA256 (not rehashed by source validation) |
| --- | --- | --- |
| Compatible unlocked 30B GGUF | `models/loom-deep-30b-unlocked.gguf` | `734fbb6b24922d7cbb81c2d439892cdd613574b48ff90775bbd6834075744b7c` |
| Lossless expert-major sidecar | `models/unlocked-expert-major-v1.bin` | `4df9602bd09c74afe2df6a721ac8d74834564c95831dd488b19873f45034451e` |
| Historical patched executable | `.loom/runtime/loom-uopt002/llama-server` | `088c9faaa6d7532bca1b9fd95d14e29fa9eafd2392eecb77a553be852179231b` |

An independently compiled executable is not promised to be bit-identical to the historical binary. Its matching build libraries must accompany it in `.loom/runtime/loom-uopt002/`. Presence of that directory is not a library ABI or integrity certificate.

The public reference source is `https://github.com/kisasexypantera94/llama.cpp.git` at commit `41ec4c4e94fd5ff6c258691f35f2fcd0d3dde892`, plus `patches/loom-uopt002-expert-major-sidecar.patch`. The custom MoE options and `LOOM_EXPERT_MAJOR_SIDECAR` require this compatible fork/patch, not an arbitrary upstream executable.

The existing `scripts/loom-uopt002-build-runtime` is the reference build recipe. It clones/fetches source, force-checks out the pin, cleans its source tree, applies the patch, builds with Metal and **replaces its destination runtime directory**. Its default source/build/destination are `.loom/src/llama.cpp-uopt002`, `.loom/build/llama.cpp-uopt002` and `.loom/runtime/loom-uopt002`. Do not run it in an operational checkout or point `LOOM_UOPT002_SOURCE_DIR` at a shared/retained tree. It is not a validation command and is not executed by the offline tests.

A future, separately authorized native provisioning procedure is:

1. Create a dedicated disposable source checkout with no active services, retained runtime, assets or shared source-directory override. Check toolchain, free storage, fork pin, patch provenance and upstream licenses.
2. Review the reference builder's destructive operations before using it **only in that disposable checkout**. Record source/patch/compiler/build-library provenance; retain upstream notices. Native compilation, patch applicability and ABI must then be validated separately, without inferring success from the synthetic tests.
3. Obtain the exact compatible model through a separately qualified, lawful provenance/derivation procedure. A filename/hash is an identity reference, not a download location or redistribution permission. The source package does not acquire, generate, unlock or qualify a substitute model automatically.
4. If constructing a sidecar from that authorized input, review `scripts/loom_uopt002_build_expert_major_sidecar.py`. It requires `--model`, `--out`, and `--gguf-py` pointing to the pinned source's GGUF Python library and its dependencies. It assumes 48 layers, 128 experts, compatible tensor layout and sufficient disk headroom. It refuses to overwrite an existing bank. Both construction and `--verify-only` read/hash large weights and write a local manifest; do not treat them as metadata-only checks. Nothing in source validation invokes them or duplicates weights.
5. Confirm model/runtime/library/sidecar compatibility, licensing and resource safety under a separate real-runtime acceptance plan before deploying. Do not reuse private local assets as evidence of clean public bootstrap.

A user who cannot establish model provenance or compatible native build prerequisites can still reproduce the source-only tests, but cannot claim a deployable 30B installation. This documentation does not qualify new model acquisition or binary redistribution.

## Operator lifecycle after independent acceptance only

The following commands are for a separately authorized, provisioned standalone installation with no conflicting model service:

```bash
scripts/loom-deep current
scripts/loom-deep use unlocked-8k  # selection only; existing process unchanged
scripts/loom-deep stop            # explicit operator action
scripts/loom-deep start
scripts/loom-deep status
scripts/loom-deep health
```

`use` never stops or starts a model. `start` refuses a different running profile, partial service, foreign detected model process, missing dependencies or occupied required port. Backend process detection covers `llama-server`, `llama-cli` and `ollama`, not every possible loader. Do not run competing launchers concurrently; the lock serializes this adapter's mutations only, not unrelated applications.

PID files are checked for valid positive PIDs and the expected executable/gateway command path before lifecycle actions. A reused/foreign PID or unverifiable ownership refuses the operation rather than signalling it. This reduces accidental stale-PID damage; it is not an adversarial process-isolation boundary or a guarantee against OS PID reuse between checks. Do not edit PID files to force ownership.

Health requests have a bounded socket timeout. A failed health request returns failure, not a success banner. Startup health failure attempts to stop the owned processes, never reloads automatically, and shutdown refuses to escalate to SIGKILL. A stop failure prevents switching; resolve it deliberately without killing unrelated processes. The startup wait is bounded polling, not a total generation watchdog. This standalone adapter does not provide a per-request cancellation policy.

Lifecycle mutations use `.loom/runtime/loom-deep/lifecycle.lock`. After an interrupted operation, retain a stale lock until the operator verifies no lifecycle operation is active; do not delete it reflexively. Keep runtime state and config local and trusted. The adapter performs local directory/state/log writes; it is not a service supervisor or a security boundary.

## Rollback and privacy

After independently approving a profile change, explicitly stop before selecting the older standalone profile:

```bash
scripts/loom-deep stop
scripts/loom-deep use unlocked       # original standalone 4K S40
# Or: scripts/loom-deep use unlocked-s32
LOOM_CONTEXT_WEBUI_GATEWAY=0 scripts/loom-deep start
```

Rollback changes selection/launch arguments, not weights. Keeping a source revision does not back up ignored runtime assets, logs or model files. Preserve the validated runtime/library set before any separately authorized native rebuild. Do not apply rollback procedures from a different deployment to this standalone installation.

Runtime stdout/stderr and backend logs may contain prompts, replies or local paths. The gateway buffers request bodies in memory and can write accounting; a separately installed core can generate additional recovery artifacts. Source validation does not certify redaction or confidentiality of live runtime logs. Do not commit logs, local manifests with resolved absolute paths, model files, sidecars, `.loom/`, personal configuration or raw benchmark answers. Configure access/retention locally before real use; `LOOM_CONTEXT_WEBUI_ACCOUNTING=0` does not disable backend logging.

## Licensing and limitations

Original LOOM source is MIT-licensed: retain [LICENSE](../LICENSE) and its attribution. The pinned llama.cpp fork is separately MIT-licensed by the ggml authors; preserve upstream notices for copied source/binaries. Third-party bundled components, toolchains and models retain their own licenses. A sidecar contains model bytes and is not relicensed as LOOM MIT source. No model or binary distribution is authorized by this source package.

SOURCE_ONLY readiness means coherent source, documented prerequisites and passing synthetic/static checks. It does **not** mean native runtime build reproducibility, lawful availability of a particular model, numerical parity, Metal correctness, 8K performance, long-prompt usability or real deployment acceptance. Those limitations remain explicit until separately verified.
