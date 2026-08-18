# T04 — Constrained refactoring

Edit only `solution.py`.

Refactor the existing implementation without changing its public behavior.

Requirements:

1. Preserve `summarize_scores(rows)` exactly for valid and invalid inputs covered by tests.
2. Extract a helper named `_coerce_score(value)`.
3. `_coerce_score(value)` must return a valid score as `float`, or `None` when the value is invalid.
4. `summarize_scores` must call `_coerce_score` rather than duplicating conversion logic.
5. Do not add imports.
6. Keep the return shape: `{"count": int, "invalid": int, "average": float | None}`.

Do not edit the tests.
