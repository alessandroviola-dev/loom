def line_subtotal(sku, qty, catalog):
    if sku not in catalog:
        raise KeyError(sku)
    if not isinstance(qty, int) or isinstance(qty, bool) or qty <= 0:
        raise ValueError("qty must be a positive integer")

    unit_price = float(catalog[sku])
    subtotal = unit_price * qty

    if qty >= 10:
        subtotal *= 0.90
    elif qty >= 5:
        subtotal *= 0.95

    return round(subtotal, 2)
