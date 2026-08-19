# LOOM — llama.cpp 8B Q2 Capability 002 — INVALID

Date: 2026-08-19
Run id: `20260819-102747`
Classification: **INVALID — STAGE A EVIDENCE PARSER DEFECT**

## Frozen condition actually executed

- Apple M1, 8 GB unified memory
- pinned llama.cpp commit `60addddf3c567c43ec3caf70fc953fba3572d96f`
- `unsloth/Qwen3-8B-GGUF`
- `Qwen3-8B-Q2_K.gguf`
- observed model size **3.056 GiB**
- SHA256 PASS
- requested context **4096** via `-c 4096`
- requested maximum Metal offload via `-ngl -1`
- Stage A single-turn correction `-st`
- 8 generated tokens
- memory-free abort below 5%
- swap abort above 5600 MB

## Observed runtime behavior

Stage A completed one inference turn and exited automatically.

Observed console timing:
- prompt approximately **43.2 t/s**
- generation approximately **11.4 t/s**

Telemetry:
- wall **7.229 s**
- peak process RSS **2215.203125 MB**
- peak observed swap **2181.12 MB**
- minimum observed free memory **19%**
- no memory/swap guardrail breach
- disk free before **43.686 GiB**
- disk free after **43.674 GiB**

Stage B was skipped because the runner labeled Stage A FAIL.

## Why the printed FAIL is invalid

The inherited Stage A validator does not validate the requested command itself. It requires literal strings in the child stdout/stderr:

```python
smoke_metal = "metal" in smoke_text or "mtl" in smoke_text
context_evidence = "4096" in smoke_text
```

The completed Q2 single-turn output did not print those literal evidence strings, even though:
- the runner constructed the command with `-c 4096` and `-ngl -1`;
- the process loaded the model, generated output, and exited cleanly;
- the immediately preceding device preflight showed `MTL0: Apple M1` and Metal initialization;
- memory headroom remained well above the frozen 5% guardrail.

Therefore the boolean Stage A FAIL is a **harness evidence-parser defect**, not evidence that the Q2 runtime profile failed.

## Valid conclusion

Capability 002 demonstrates strong diagnostic evidence that the Q2 profile can load and complete a single turn with materially more memory headroom than Q4/Q3, but it is **not promoted to PASS after the fact** because the frozen success validator was defective and Stage B never ran.

A new Capability 003 must preserve the exact runtime/model condition and correct only the Stage A evidence validation before a canonical PASS/FAIL classification is allowed.
