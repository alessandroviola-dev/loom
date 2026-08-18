import json
import unittest
from pathlib import Path


EXPECTED = {
    "strategy": "first_fit",
    "mutates_inputs": False,
    "return_on_unassigned": -1,
    "capacity_state": "internal_copy",
}

ACCEPTED_COMPLEXITIES = {
    "O(len(capacities) * len(jobs))",
    "O(len(jobs) * len(capacities))",
}


class ComprehensionTests(unittest.TestCase):
    def test_answer_file_exists(self):
        self.assertTrue(Path("answer.json").exists())

    def test_answer_is_valid_json(self):
        data = json.loads(Path("answer.json").read_text())
        self.assertIsInstance(data, dict)

    def test_exact_keys(self):
        data = json.loads(Path("answer.json").read_text())
        self.assertEqual(set(data), set(EXPECTED) | {"worst_case"})

    def test_strategy(self):
        data = json.loads(Path("answer.json").read_text())
        self.assertEqual(data["strategy"], EXPECTED["strategy"])

    def test_mutation_and_state(self):
        data = json.loads(Path("answer.json").read_text())
        self.assertEqual(data["mutates_inputs"], EXPECTED["mutates_inputs"])
        self.assertEqual(data["capacity_state"], EXPECTED["capacity_state"])

    def test_unassigned_value(self):
        data = json.loads(Path("answer.json").read_text())
        self.assertEqual(data["return_on_unassigned"], EXPECTED["return_on_unassigned"])

    def test_complexity(self):
        data = json.loads(Path("answer.json").read_text())
        self.assertIn(data["worst_case"], ACCEPTED_COMPLEXITIES)


if __name__ == "__main__":
    unittest.main()
