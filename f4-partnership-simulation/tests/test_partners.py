import copy
import json
import tempfile
import unittest

from tests import _helpers  # noqa: F401
import partners as pt


class TestPartners(unittest.TestCase):
    def setUp(self):
        self.scenarios = pt.load_scenarios()
        self.base = copy.deepcopy(pt.load_data()["base_partners"])

    def test_load_scenarios(self):
        self.assertEqual([s["id"] for s in self.scenarios], ["A", "B", "C", "D"])
        for s in self.scenarios:
            self.assertEqual(set(s["partners"]), {"A", "B"})
            for pid in pt.PARTNERS:
                for k in pt.FIELDS:
                    self.assertIn(k, s["partners"][pid])
        self.assertEqual(pt.scenario_by_id(self.scenarios, "C")["partners"]["A"]["communication_score"], 0.2)
        self.assertEqual(pt.scenario_by_id(self.scenarios, "D")["strategy"], "adaptive")

    def test_load_stress_events(self):
        events = pt.load_stress_events()
        for name in ("none", "combined", "income_drop", "work_increase", "housework_increase", "expense_increase"):
            self.assertIn(name, events)
        self.assertEqual([e["year"] for e in events["combined"]], [5, 8])

    def _invalid(self, key, value):
        p = copy.deepcopy(self.base["A"])
        p[key] = value
        with self.assertRaises(ValueError):
            pt.validate_partner(p)

    def test_invalid_income(self):
        self._invalid("annual_income", -1)
        self._invalid("annual_income", "300")

    def test_invalid_work_hours(self):
        self._invalid("weekly_work_hours", -5)
        self._invalid("weekly_work_hours", 200)
        self._invalid("available_housework_hours", -1)

    def test_share_range(self):
        self._invalid("preferred_housework_share", 1.2)
        self._invalid("preferred_financial_share", -0.1)
        self._invalid("communication_score", 1.5)
        with self.assertRaises(ValueError):
            pt.validate_rule(1.3, pt.HOUSEWORK_RULES)
        with self.assertRaises(ValueError):
            pt.validate_rule("unknown", pt.FINANCIAL_RULES)
        self.assertTrue(pt.validate_rule(0.8, pt.HOUSEWORK_RULES))

    def test_satisfaction_range(self):
        self._invalid("satisfaction", 1.01)
        self._invalid("satisfaction", -0.01)
        p = copy.deepcopy(self.base["A"])
        p["satisfaction"] = 0.0
        self.assertTrue(pt.validate_partner(p))

    def test_missing_field_and_wrong_partners(self):
        p = copy.deepcopy(self.base["A"])
        del p["fairness_weight"]
        with self.assertRaises(ValueError):
            pt.validate_partner(p)
        with self.assertRaises(ValueError):
            pt.validate_partners({"A": self.base["A"]})

    def test_copies_do_not_change_original(self):
        sc = self.scenarios[0]
        changed = pt.with_communication(sc, 0.9)
        self.assertEqual(changed["partners"]["A"]["communication_score"], 0.9)
        self.assertEqual(sc["partners"]["A"]["communication_score"], 0.5)
        changed = pt.with_partner_changes(sc, "B", annual_income=100)
        self.assertEqual(sc["partners"]["B"]["annual_income"], 520)
        with self.assertRaises(ValueError):
            pt.with_partner_changes(sc, "B", annual_income=-100)

    def test_f3_sample_pairs(self):
        data = pt.load_f3_pairs(pt.DATA_PATH.parent / "sample_f3_pairs.json")
        self.assertEqual(data["format"], pt.F3_FORMAT_VERSION)
        sc = pt.scenario_from_f3_pair(data["pairs"][0], self.scenarios[0])
        self.assertEqual(sc["partners"]["A"]["satisfaction"], data["pairs"][0]["initial_satisfaction"])
        self.assertTrue(sc["id"].startswith("F3-"))

    def test_f3_invalid_format(self):
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump({"format": "other", "pairs": []}, f)
        with self.assertRaises(ValueError):
            pt.load_f3_pairs(f.name)
        with self.assertRaises(ValueError):
            pt.validate_f3_export({"format": pt.F3_FORMAT_VERSION, "pairs": [{"pair_id": "P1"}]})


if __name__ == "__main__":
    unittest.main()
