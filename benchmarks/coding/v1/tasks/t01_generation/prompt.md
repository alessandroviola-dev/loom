# T01 — Code generation from specification

Edit only `solution.py`.

Implement `normalize_tags(items)` with these exact rules:

1. `items` is an iterable of strings.
2. Strip leading/trailing whitespace from each string.
3. Convert each remaining string to lowercase.
4. Ignore strings that become empty after stripping.
5. Remove duplicates after normalization while preserving the order of first appearance.
6. If any element is not a string, raise `TypeError`.
7. Return a list of normalized strings.
8. Use only the Python standard language features; no third-party packages.

Do not edit the tests.
