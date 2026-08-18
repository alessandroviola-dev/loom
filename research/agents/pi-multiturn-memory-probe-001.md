# Pi Multi-turn Memory Probe 001 — Result

Date: 2026-08-18
Run id: `20260818-224524`
Status: **COMPLETED — INVALID FOR CAUSAL DEPTH INFERENCE**

## Preregistered question

Does Ollama reported allocation increase materially with within-session Pi tool/turn depth at fixed context 4096?

Plan:
- `research/agents/pi-multiturn-memory-probe-001-plan.md`

Runner:
- `scripts/pi_multiturn_memory_probe.py`

## Observed result

```text
cold-1turn: success=False reads=3  size=4.3 GB swap=2073.69 MB usage=1426
cold-4turn: success=True  reads=4  size=4.3 GB swap=1904.88 MB usage=1389
cold-8turn: success=False reads=14 size=4.9 GB swap=2383.56 MB usage=2854
warm-1turn-after-8: SKIPPED
```

### cold-1turn

Expected exactly:

```text
['one-01.txt']
```

Observed:

```text
['001.txt', 'Files', 'one-01.txt']
```

The model issued two speculative/incorrect read calls before the intended file. The condition therefore failed the preregistered exact-path/exact-count criterion.

### cold-4turn

This condition was valid:
- reads: 4/4 in the expected order
- final text: `DONE`
- Ollama SIZE: 4.3 GB
- context: 4096
- swap: 1904.88 MB
- provider usage total: 1389

### cold-8turn

Expected exactly eight chain reads.

Observed fourteen reads, including multiple speculative filename guesses before the valid chain:

```text
8-01.txt
01.txt
eight_01.txt
eight.txt
8_01.txt
001.txt
EIGHT-01.TXT
eight-02.txt
eight-03.txt
eight-04.txt
eight-05.txt
eight-06.txt
eight-07.txt
eight-08.txt
```

Because tool count/order differed materially from the preregistered condition, the 4.9 GB post-session SIZE cannot be interpreted as the memory cost of an eight-round-trip session.

The warm follow-up was correctly skipped because the deepest cold condition was invalid.

## Classification

This run is **not valid evidence for a causal 1-vs-4-vs-8 tool-depth relationship**.

Reason:
> Built-in `read` leaves the model free to emit speculative filenames. The file-chain design hid the intended next filename but did not prevent invalid guesses, so observed tool depth was not experimentally controlled.

The run remains useful as exploratory evidence only:
- a valid 4-read session ended at 4.3 GB;
- a much noisier 14-read session ended at 4.9 GB;
- however the latter also had more provider usage, failed reads and different interaction history, so no clean attribution is possible.

Do not use the 4.3 -> 4.9 GB difference as a causal estimate of tool-depth cost.

## Measurement-design correction

A new probe must remove model-controlled path selection.

Preferred correction:
- use one isolated custom Pi extension tool rather than filesystem paths;
- the tool advances internal state by one step only when given the opaque token returned by the immediately preceding tool result;
- next tokens are generated inside the extension and cannot be known before the prior result;
- built-in tools are disabled;
- exact successful tool-call count must equal the target depth.

This converts the experiment from a filename-following task into a controlled model -> tool -> result -> model round-trip chain.
