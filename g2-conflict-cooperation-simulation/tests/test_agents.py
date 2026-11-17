import json
import tempfile
import unittest

from tests import _helpers  # noqa: F401
import agents as ag


class TestAgents(unittest.TestCase):
    def test_load(self):
        cs = ag.load_countries()
        self.assertEqual([c["id"] for c in cs], ["A", "B", "C", "D", "E"])
        for c in cs:
            self.assertIsNone(c["last_action"])
            self.assertEqual(c["cumulative_payoff"], 0.0)
            self.assertIn(c["strategy"], ag.STRATEGIES)

    def test_range_validation(self):
        for k in ag.UNIT_FIELDS:
            for bad in (-0.1, 1.1, "0.5", True):
                with self.assertRaises(ValueError):
                    ag.make_country("X", **{k: bad})
        self.assertTrue(ag.validate_country(ag.make_country("X", 0.0, 1.0, 0.5)))

    def test_invalid_strategy(self):
        with self.assertRaises(ValueError):
            ag.make_country("X", strategy="aggressive")
        with self.assertRaises(ValueError):
            ag.with_strategy(ag.load_countries(), "unknown")

    def test_duplicate_and_missing(self):
        data = {"countries": [{"id": "A", "cooperation_preference": 0.5, "trust": 0.5,
                               "economic_interdependence": 0.5, "strategy": "conditional"}] * 2}
        with tempfile.NamedTemporaryFile("w", suffix=".json", delete=False, encoding="utf-8") as f:
            json.dump(data, f)
        with self.assertRaises(ValueError):
            ag.load_countries(f.name)
        with self.assertRaises(ValueError):
            ag.validate_country({"id": "Z", "trust": 0.5})

    def test_relation(self):
        a = ag.make_country("A", trust=0.6)
        b = ag.make_country("B", trust=0.2)
        r = ag.make_relation(a, b)
        self.assertAlmostEqual(r["trust"], 0.4)
        self.assertEqual(r["state"], "Neutral")
        self.assertFalse(r["dialogue"] or r["agreement"])
        self.assertEqual(r["history"], [])

    def test_copies(self):
        cs = ag.load_countries()
        t = ag.with_trust(cs, 0.9)
        self.assertTrue(all(c["trust"] == 0.9 for c in t))
        self.assertEqual(cs[0]["trust"], 0.6)                   # 元は変わらない
        self.assertTrue(all(c["strategy"] == "tit_for_tat" for c in ag.with_strategy(cs, "tit_for_tat")))


if __name__ == "__main__":
    unittest.main()
