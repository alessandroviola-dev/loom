import ast
import inspect
import unittest

import solution


class RefactorTests(unittest.TestCase):
    def test_mixed_rows(self):
        rows = [
            {"score": 90},
            {"score": " 80.5 "},
            {"score": True},
            {"score": 101},
            {},
            {"score": "bad"},
        ]
        self.assertEqual(
            solution.summarize_scores(rows),
            {"count": 2, "invalid": 4, "average": 85.25},
        )

    def test_empty(self):
        self.assertEqual(solution.summarize_scores([]), {"count": 0, "invalid": 0, "average": None})

    def test_boundaries(self):
        self.assertEqual(
            solution.summarize_scores([{"score": 0}, {"score": "100"}]),
            {"count": 2, "invalid": 0, "average": 50.0},
        )

    def test_helper_exists(self):
        self.assertTrue(callable(getattr(solution, "_coerce_score", None)))

    def test_helper_contract(self):
        self.assertEqual(solution._coerce_score(" 12.5 "), 12.5)
        self.assertIsNone(solution._coerce_score(True))
        self.assertIsNone(solution._coerce_score("bad"))
        self.assertIsNone(solution._coerce_score(-1))
        self.assertIsNone(solution._coerce_score(101))

    def test_summarize_calls_helper(self):
        tree = ast.parse(inspect.getsource(solution.summarize_scores))
        calls = [
            node for node in ast.walk(tree)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id == "_coerce_score"
        ]
        self.assertGreaterEqual(len(calls), 1)

    def test_no_imports(self):
        tree = ast.parse(inspect.getsource(solution))
        imports = [node for node in ast.walk(tree) if isinstance(node, (ast.Import, ast.ImportFrom))]
        self.assertEqual(imports, [])


if __name__ == "__main__":
    unittest.main()
