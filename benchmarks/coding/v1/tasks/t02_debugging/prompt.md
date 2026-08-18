# T02 — Debugging existing faulty code

Edit only `buggy.py`.

`window_sum(values, size)` is intended to return the sum of every contiguous window of length `size`, but the current implementation has a bug.

Required behavior:

1. `size` must be a positive integer; otherwise raise `ValueError`.
2. `bool` is not accepted as a valid integer size.
3. If `size > len(values)`, return `[]`.
4. Return one sum for every contiguous window of exactly `size` elements.
5. Preserve normal Python numeric behavior for ints/floats.
6. Keep the rolling-window approach; do not replace it with repeated slicing/summing for every window.

Fix the implementation without editing the tests.
