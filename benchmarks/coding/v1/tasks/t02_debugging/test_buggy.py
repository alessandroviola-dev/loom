import ast
import inspect
import unittest

import buggy


class WindowSumTests(unittest.TestCase):
    def test_exact_window(self):
        self.assertEqual(buggy.window_sum([1, 2, 3], 3), [6])

    def test_multiple_windows(self):
        self.assertEqual(buggy.window_sum([1, 2, 3, 4], 2), [3, 5, 7])

    def test_size_one(self):
        self.assertEqual(buggy.window_sum([2, -1, 4], 1), [2, -1, 4])

    def test_oversized_window(self):
        self.assertEqual(buggy.window_sum([1, 2], 3), [])

    def test_invalid_sizes(self):
        for size in (0, -1, 1.5, True):
            with self.subTest(size=size):
                with self.assertRaises(ValueError):
                    buggy.window_sum([1, 2, 3], size)

    def test_floats(self):
        self.assertEqual(buggy.window_sum([1.5, 2.0, -0.5], 2), [3.5, 1.5])

    def test_keeps_rolling_approach(self):
        tree = ast.parse(inspect.getsource(buggy.window_sum))
        sum_calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "sum"
        ]
        self.assertLessEqual(len(sum_calls), 1)


if __name__ == "__main__":
    unittest.main()
