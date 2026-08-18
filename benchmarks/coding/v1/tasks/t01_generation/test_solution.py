import unittest

from solution import normalize_tags


class NormalizeTagsTests(unittest.TestCase):
    def test_basic(self):
        self.assertEqual(normalize_tags(["Alpha", "Beta"]), ["alpha", "beta"])

    def test_strip_case_and_duplicates(self):
        self.assertEqual(
            normalize_tags(["  Alpha ", "ALPHA", " beta", "Beta "]),
            ["alpha", "beta"],
        )

    def test_empty_values_are_ignored(self):
        self.assertEqual(normalize_tags(["", "   ", "A", "\t"]), ["a"])

    def test_preserves_first_normalized_order(self):
        self.assertEqual(normalize_tags(["B", "a", "b", "C", "A"]), ["b", "a", "c"])

    def test_rejects_non_strings(self):
        with self.assertRaises(TypeError):
            normalize_tags(["ok", 3, "later"])

    def test_accepts_generic_iterables(self):
        values = (x for x in [" One ", "TWO", "one"])
        self.assertEqual(normalize_tags(values), ["one", "two"])


if __name__ == "__main__":
    unittest.main()
