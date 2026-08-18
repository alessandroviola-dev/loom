import ast
import inspect
import unittest

import solution


class TopKFrequentTests(unittest.TestCase):
    def test_basic_frequency_order(self):
        self.assertEqual(solution.top_k_frequent([1, 1, 1, 2, 2, 3], 2), [1, 2])

    def test_ties_follow_first_appearance(self):
        self.assertEqual(solution.top_k_frequent(["b", "a", "c", "a", "b", "c"], 3), ["b", "a", "c"])

    def test_k_larger_than_unique_count(self):
        self.assertEqual(solution.top_k_frequent([3, 1, 3, 2], 10), [3, 1, 2])

    def test_single_value(self):
        self.assertEqual(solution.top_k_frequent(["x", "x"], 1), ["x"])

    def test_invalid_k(self):
        for k in (0, -1, 1.5, True, "2", None):
            with self.subTest(k=k):
                with self.assertRaises(ValueError):
                    solution.top_k_frequent([1, 2], k)

    def test_empty_values(self):
        self.assertEqual(solution.top_k_frequent([], 3), [])

    def test_no_forbidden_constructs(self):
        tree = ast.parse(inspect.getsource(solution))
        for node in ast.walk(tree):
            self.assertNotIsInstance(node, (ast.Import, ast.ImportFrom))
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Name):
                    self.assertNotEqual(node.func.id, "sorted")
                if isinstance(node.func, ast.Attribute):
                    self.assertNotEqual(node.func.attr, "sort")


if __name__ == "__main__":
    unittest.main()
