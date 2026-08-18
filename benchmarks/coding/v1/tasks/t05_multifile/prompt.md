# T05 — Multi-file reasoning

Edit only `order.py`.

Inspect both `order.py` and `pricing.py` before implementing the task.

Implement `order_total(lines, catalog, tax_rate)` with these rules:

1. `lines` is an iterable of dictionaries containing `sku` and `qty`.
2. For every line, obtain the pre-tax line amount by calling `pricing.line_subtotal(sku, qty, catalog)`.
3. Do not duplicate the pricing or quantity-validation logic from `pricing.py` inside `order.py`.
4. Sum all line subtotals first, then apply tax once to the complete subtotal.
5. `tax_rate` must be an int or float from 0 through 1 inclusive; `bool` is invalid. Invalid values raise `ValueError`.
6. Return the final total rounded to two decimal places.
7. An empty order returns `0.0`.
8. Errors raised by `pricing.line_subtotal` must propagate unchanged.

Do not edit `pricing.py` or the tests.
