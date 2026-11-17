# F3：participants.py のテスト

import copy
import json
import os
import tempfile
import unittest

import participants as pt


def load_raw():
    with open(pt.DATA_FILE, encoding="utf-8") as f:
        return json.load(f)["participants"]


class TestLoad(unittest.TestCase):
    def test_load_sample(self):
        g = pt.load_participants()
        self.assertEqual([p["id"] for p in g["A"]], ["A1", "A2", "A3", "A4", "A5"])
        self.assertEqual([p["id"] for p in g["B"]], ["B1", "B2", "B3", "B4", "B5"])
        self.assertEqual(pt.total_participants(g), 10)
        self.assertEqual(pt.by_id(g)["B3"]["group"], "B")

    def test_load_from_file(self):
        with tempfile.TemporaryDirectory() as d:
            path = os.path.join(d, "p.json")
            with open(path, "w", encoding="utf-8") as f:
                json.dump({"participants": load_raw()}, f)
            self.assertEqual(len(pt.load_participants(path)["A"]), 5)


class TestValidation(unittest.TestCase):
    def setUp(self):
        self.people = load_raw()

    def check_invalid(self, people):
        with self.assertRaises(ValueError):
            pt.validate_participants(people)

    def test_duplicate_id(self):
        people = copy.deepcopy(self.people)
        people[1]["id"] = "A1"
        self.check_invalid(people)

    def test_invalid_group(self):
        people = copy.deepcopy(self.people)
        people[0]["group"] = "C"
        self.check_invalid(people)

    def test_unknown_candidate(self):
        people = copy.deepcopy(self.people)
        people[0]["acceptable_candidates"] = ["B1", "B9"]
        self.check_invalid(people)

    def test_same_group_candidate(self):
        people = copy.deepcopy(self.people)
        people[0]["acceptable_candidates"] = ["B1", "A2"]
        self.check_invalid(people)

    def test_duplicate_candidate(self):
        people = copy.deepcopy(self.people)
        people[0]["acceptable_candidates"] = ["B1", "B2", "B1"]
        self.check_invalid(people)

    def test_weights_must_sum_to_one(self):
        people = copy.deepcopy(self.people)
        people[0]["preferences"]["weights"]["age"] = 0.5
        self.check_invalid(people)

    def test_profile_range(self):
        people = copy.deepcopy(self.people)
        people[0]["values"]["family"] = 1.5
        self.check_invalid(people)

    def test_other_group(self):
        self.assertEqual(pt.other_group("A"), "B")
        self.assertEqual(pt.other_group("B"), "A")


if __name__ == "__main__":
    unittest.main()
