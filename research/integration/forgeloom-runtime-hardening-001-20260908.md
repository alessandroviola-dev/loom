# ForgeLoom Runtime Hardening 001

Date: 2026-09-08
Branch: `research/forgeloom-runtime-hardening-001`
Status: **IMPLEMENTED / OFFLINE-CI PASS / MANUAL SMOKE PENDING**

## Trigger

A real ForgeLoom coding session on `wifi_hacker.py` exposed two operational issues after CE-001/CE-002 closure:

1. exiting ForgeLoom left the retained 30B backend running and holding unified memory;
2. a large `edit` tool call repeatedly hit the 800-token output ceiling, Pi correctly rejected the truncated tool arguments, and the retained model retried the same oversized edit multiple times.

Neither issue is a CE-001/CE-002 archive/retrieval regression.

## Changes

### Private runtime-hardening extension

Added:

- `src/forgeloom-runtime-hardening/index.ts`
- `src/forgeloom-runtime-hardening/policy.mjs`

It is installed under the private ForgeLoom root and loaded explicitly only by the `ForgeLoom` launcher. Normal `pi` and normal `Forge` remain unchanged.

Policy:

- prefer small targeted edits;
- split large file changes across multiple edit calls;
- keep edit/write payloads compact;
- after a truncation, never retry the identical payload;
- do not create helper verification files unless explicitly requested;
- allow one recovery attempt after an assistant `stopReason=length`;
- abort the active operation after the second consecutive length stop, preventing unbounded repeated truncated tool calls.

The CE-001 output budget remains 800 tokens. No 4096-context envelope limit was changed.

### Automatic backend lifecycle

`scripts/install-forge-loom.sh` now generates a `ForgeLoom` launcher that keeps a lightweight per-process client lease.

Default behavior:

```text
last ForgeLoom process exits
        -> client lease removed
        -> no remaining ForgeLoom clients
        -> scripts/loom-deep stop
        -> backend + gateway released
```

Multiple simultaneous ForgeLoom sessions do not cause the first exiting session to stop the backend for the remaining session.

Opt-out for intentionally warm backend:

```bash
LOOM_FORGE_AUTO_STOP=0 ForgeLoom
```

Emergency/manual stop installed globally on the user PATH:

```bash
ForgeLoomStop
```

This clears stale ForgeLoom client leases and invokes the canonical `scripts/loom-deep stop` lifecycle manager.

## Validation

CI run `34269615870`:

- syntax: PASS
- CE-001 governor tests: PASS
- CE-002 archive tests: PASS
- CE-002 retrieval tests: PASS
- ForgeLoom runtime-hardening tests: PASS
- repository/Forge isolation invariants: PASS

New unit tests prove:

```text
first consecutive length stop   -> one recovery attempt allowed
second consecutive length stop  -> abort guard trips
normal/toolUse stop              -> counter resets
system policy contains split-edit/no-identical-retry rules
```

## Frozen components

No changes were made to:

- retained 30B model/runtime;
- CE-001 core governor;
- CE-002 archive/retrieval modules;
- physical context 4096;
- safe total 3600;
- safe input 2800;
- maximum output 800;
- high-water 1600;
- target 1200;
- normal Forge behavior.

## Remaining acceptance

One manual smoke on the target Mac is still required to verify installation/runtime behavior:

1. install from this branch;
2. confirm normal Forge does not load the two private ForgeLoom extensions;
3. run a short ForgeLoom session;
4. exit it and confirm `ForgeLoomStop`/`loom-deep status` reports the backend not running;
5. optionally retry the previous real coding task once and verify that a large edit either splits successfully or stops after at most two truncations rather than looping.

No endurance or multi-run 30B benchmark is required.
