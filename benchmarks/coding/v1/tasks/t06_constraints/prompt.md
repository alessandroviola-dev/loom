# T06 — Instruction following under implementation constraints

Edit only `solution.py`.

Implement `top_k_frequent(values, k)`.

Required behavior:

1. Return at most `k` unique values ordered by decreasing frequency.
2. Break frequency ties by the value's first appearance in the original input.
3. `k` must be a positive integer; `bool` is invalid. Invalid `k` raises `ValueError`.
4. If `k` is larger than the number of unique values, return all unique values in the required order.
5. The tested values are hashable.

Implementation constraints:

- no imports;
- do not call `sorted`;
- do not call `.sort()`;
- do not use `collections.Counter` or `heapq`;
- dictionaries, lists, loops and basic built-ins are allowed.

Do not edit the tests.
