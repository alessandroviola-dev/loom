# LOOM 8B Practical Bake-off Runner 001 — Result

Date: 2026-08-28
Classification: **LOOM_8B_BAKEOFF_RUNNER_PASS**
Task completion: **INCOMPLETE**
Stop reason: **MAX_GENERATED_TOKENS_384**

## Frozen condition

The run preserved the preregistered historical LOOM REALGEN 8B runtime:

- model: `mlx-community/Qwen3-8B-3bit@619ded3`;
- local model: `results-local/mlx/models/Qwen3-8B-3bit`;
- verified main weight SHA-256: `b9694bdb1f737223836235c0427b424ace11d566eeab0ac91ff8050143bd20a1`;
- 3-bit affine / group size 64;
- MLX `0.31.2`, mlx-lm `0.31.3`, transformers `5.12.1`;
- real autoregressive M1;
- built-in MLX `qmv_fast`;
- BF16 KV;
- greedy argmax;
- Qwen3 non-thinking chat template;
- no S1_R8, oracle, speculative decoding, Ollama, llama.cpp, skills, memory, tools, RAG, prompt optimization or behavioral editing.

One new local runner was created:
`scripts/loom_8b_practical_bakeoff_runner_001.py`.

The runner source was not Git-persisted by Pi. This result records the bounded evidence; source persistence is not required to interpret this one-shot benchmark result, but the local runner must not be treated as canonical production code without review/persistence.

## Frozen task

The exact single-line LRUCache prompt used manually on LOOM 30B was used with a maximum of 384 generated tokens.

## Output quality / completion

The 8B selected the correct high-level O(1) strategy: dictionary + doubly-linked list, with recency updates on access and insertion. `get()` visibly returned `-1` for a missing key and moved hits to the most-recent position.

However, the requested executable program was not completed within 384 generated tokens. The output stopped inside `put()` while deleting an evicted key. The visible partial code also contains a suspicious unnecessary assignment (`node = self.key_to = self.key_to_node[key]`), though that line alone is syntactically valid. Because the implementation and requested test were unfinished, task status is **INCOMPLETE** regardless of the valid runner classification.

This result must therefore not be described as an 8B coding-quality PASS.

## Performance

- output tokens: `384`;
- TTFT: `2.992 s`;
- generation: `13.357 tok/s`;
- end-to-end output: `12.275 tok/s`;
- end-to-end wall: `31.284 s`;
- full runner wall: `35.975 s`;
- token-forward p50: `68.932 ms`;
- token-forward p95: `71.667 ms`.

## Resources

- MLX active: `3,583,928,328 B`;
- MLX peak: `3,912,428,412 B`;
- MLX cache after: `115,927,764 B`;
- free memory before/after generation: `23% / 23%`;
- swap: `2363.69 MB -> 2498.62 MB`;
- observed peak swap: `2498.62 MB`;
- cleanup count: `38`;
- cleanup wall: `2.140 s`.

## Comparison to historical REALGEN 001

Historical REALGEN 001 measured `13.184615 tok/s` generation and `12.046861 tok/s` end-to-end over 722 genuine autoregressive output tokens. This matched LRUCache run measured `13.357` and `12.275 tok/s`, respectively: approximately `+1.3%` generation and `+1.9%` end-to-end. The longer prompt raised TTFT to `2.992 s` versus roughly `0.94 s` on the shorter historical prompt set; this is not by itself a runtime regression claim.

Peak MLX and swap were higher in the current host/run condition. No cross-run causal attribution is made.

## Practical comparison to LOOM 30B manual task

Both 8B and 30B exhausted the same 384-token output budget before completing the requested LRUCache program.

The 30B partial response had selected the same correct O(1) architecture and reached `put()` before truncation. The 8B likewise selected the correct architecture and reached `put()` before truncation. Thus this single task does **not** establish equivalent coding quality.

The decisive difference is latency: the matched 8B condition generated 384 tokens in about 31.3 s end-to-end at 13.357 tok/s, whereas the canonical 30B runtime is around 1.1 tok/s and the manual user observed minutes of waiting. This is strong evidence that 8B is materially more usable for ordinary interactive work, but role selection must wait for a broader matched task set including the 4B tier.

## Evidence

`results-local/research/8b-practical-bakeoff-runner-001/20260828T144423Z/summary.json`

## Decision

Accept the runner/evidence as **LOOM_8B_BAKEOFF_RUNNER_PASS**, with task status **INCOMPLETE**.

Do not tune the 8B based on this single prompt. Next recover/port the LOOM 4B tier and run the same frozen LRUCache condition before broader 4B/8B/30B task comparison.