# T03 — Code comprehension

Do not modify `source.py` or the tests.

Read `source.py` and create a new file named `answer.json` with exactly these keys:

- `strategy`
- `mutates_inputs`
- `return_on_unassigned`
- `capacity_state`
- `worst_case`

Use these allowed values where applicable:

- `strategy`: `first_fit`, `best_fit`, `round_robin`, or `other`
- `capacity_state`: `internal_copy`, `mutates_original`, or `none`

For `worst_case`, use standard Big-O notation in terms of `len(capacities)` and `len(jobs)`.

The answer must be valid JSON and contain no extra keys.
