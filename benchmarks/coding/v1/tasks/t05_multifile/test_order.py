import ast
import inspect
import unittest
from unittest.mock import patch

import order
import pricing


CATALOG = {"A": 10.0, "B": 7.5, "C": 3.0}


class OrderTotalTests(unittest.TestCase):
    def test_empty_order(self):
        self.assertEqual(order.order_total([], CATALOG, 0.22), 0.0)

    def test_single_line_no_discount(self):
        self.assertEqual(order.order_total([{"sku": "A", "qty": 2}], CATALOG, 0.10), 22.0)

    def test_multiple_lines_with_discount_then_tax(self):
        lines = [
            {"sku": "A", "qty": 5},
            {"sku": "B", "qty": 10},
        ]
        # line subtotals: 47.50 + 67.50 = 115.00; tax 20% => 138.00
        self.assertEqual(order.order_total(lines, CATALOG, 0.20), 138.0)

    def test_invalid_tax_rate(self):
        for rate in (-0.1, 1.1, True, "0.2", None):
            with self.subTest(rate=rate):
                with self.assertRaises(ValueError):
                    order.order_total([], CATALOG, rate)

    def test_pricing_errors_propagate(self):
        with self.assertRaises(KeyError):
            order.order_total([{"sku": "MISSING", "qty": 1}], CATALOG, 0.2)
        with self.assertRaises(ValueError):
            order.order_total([{"sku": "A", "qty": 0}], CATALOG, 0.2)

    def test_calls_pricing_module_for_each_line(self):
        lines = [{"sku": "A", "qty": 1}, {"sku": "B", "qty": 2}]
        with patch("pricing.line_subtotal", wraps=pricing.line_subtotal) as mocked:
            order.order_total(lines, CATALOG, 0.0)
            self.assertEqual(mocked.call_count, 2)

    def test_uses_pricing_line_subtotal_reference(self):
        tree = ast.parse(inspect.getsource(order.order_total))
        calls = [node for node in ast.walk(tree) if isinstance(node, ast.Call)]
        self.assertTrue(
            any(
                isinstance(node.func, ast.Attribute)
                and isinstance(node.func.value, ast.Name)
                and node.func.value.id == "pricing"
                and node.func.attr == "line_subtotal"
                for node in calls
            )
        )


if __name__ == "__main__":
    unittest.main()
