import unittest

from tests import _helpers  # noqa: F401
import partners as pt
import decision_strategies as ds
import relationship_dynamics as rd
import evaluation as ev


def outcome(year, observed=20):
    return {"dissolved": year is not None, "dissolution_year": year,
            "duration": year if year is not None else observed, "censored": year is None, "observed_years": observed}


class TestEvaluation(unittest.TestCase):
    def setUp(self):
        self.sc = pt.scenario_by_id(pt.load_scenarios(), "A")
        self.params = rd.load_parameters()
        # 3 年目に解消・12 年目に解消・解消せず（打ち切り）・解消せず
        self.outcomes = [outcome(3), outcome(12), outcome(None), outcome(None)]

    def test_mean_min_diff(self):
        self.assertAlmostEqual(ev.mean_satisfaction(0.8, 0.4), 0.6)
        self.assertEqual(ev.minimum_satisfaction(0.8, 0.4), 0.4)
        self.assertAlmostEqual(ev.satisfaction_difference(0.4, 0.8), 0.4)
        # 平均が同じでも、最低・差は違う
        self.assertEqual(ev.mean_satisfaction(0.6, 0.6), ev.mean_satisfaction(0.9, 0.3))
        self.assertNotEqual(ev.minimum_satisfaction(0.6, 0.6), ev.minimum_satisfaction(0.9, 0.3))

    def test_fairness(self):
        p, hh = self.sc["partners"], self.sc["household"]
        self.assertEqual(ev.fairness_index(0.5, 0.5, 0.6, 0.6, p, hh, "equal"), 1.0)
        self.assertAlmostEqual(ev.fairness_index(1.0, 1.0, 1.0, 0.0, p, hh, "equal"), 1 - (0.5 + 0.5 + 1) / 3)
        rx, ry = ev.reference_allocation(p, hh, "workload")
        self.assertAlmostEqual(ev.fairness_index(rx, ry, 0.5, 0.5, p, hh, "workload"), 1.0)
        # 同じ分担でも基準によって評価が変わる
        values = {r: ev.fairness_index(0.5, 0.5, 0.6, 0.6, p, hh, r) for r in ev.FAIRNESS_REFERENCES}
        self.assertGreater(len(set(round(v, 6) for v in values.values())), 1)
        with self.assertRaises(ValueError):
            ev.fairness_index(0.5, 0.5, 0.5, 0.5, p, hh, "unknown")
        for x in (0, 0.5, 1):
            v = ev.fairness_index(x, 1 - x, x, 1 - x, p, hh)
            self.assertTrue(0 <= v <= 1)

    def test_continuation_rate(self):
        self.assertEqual(ev.continuation_rate(self.outcomes, 2), 1.0)
        self.assertEqual(ev.continuation_rate(self.outcomes, 5), 0.75)
        self.assertEqual(ev.continuation_rate(self.outcomes, 10), 0.75)
        self.assertEqual(ev.continuation_rate(self.outcomes, 20), 0.5)
        self.assertIsNone(ev.continuation_rate([], 5))
        self.assertEqual(ev.survival_curve(self.outcomes, 3), [1.0, 1.0, 1.0, 0.75])

    def test_dissolution_rate(self):
        self.assertEqual(ev.dissolution_rate(self.outcomes), 0.5)
        self.assertIsNone(ev.dissolution_rate([]))

    def test_duration(self):
        d = ev.duration_summary(self.outcomes)
        self.assertEqual(d["dissolved"], 2)
        self.assertEqual(d["censored"], 2)
        self.assertAlmostEqual(d["mean_duration_dissolved"], 7.5)
        self.assertAlmostEqual(d["mean_observed_duration"], (3 + 12 + 20 + 20) / 4)

    def test_censoring(self):
        short = [outcome(None, observed=5), outcome(None, observed=20)]
        self.assertEqual(ev.continuation_rate(short, 10), 1.0)      # 5 年しか観測していない結果は数えない
        self.assertEqual(ev.continuation_rate([outcome(None, observed=5)], 10), None)
        self.assertEqual(ev.dissolution_rate(short), 0.0)

    def test_dissolution_year_of(self):
        recs = [{"year": y, "continuing": y != 4} for y in range(5)]
        self.assertEqual(ev.dissolution_year_of(recs), 4)
        self.assertIsNone(ev.dissolution_year_of([{"year": 0, "continuing": True}]))

    def test_stress_response(self):
        recs = [{"year": y, "relationship_satisfaction": 0.7 if y < 5 else 0.5} for y in range(10)]
        r = ev.stress_response(recs, 5)
        self.assertAlmostEqual(r["change"], -0.2)
        self.assertIsNone(ev.stress_response(recs, 30))

    def test_compare_strategies(self):
        events = pt.load_stress_events()["combined"]
        res = ev.compare_strategies(self.sc, self.params, events, ds.STRATEGIES, 50, (0, 1))
        self.assertEqual(set(res), set(ds.STRATEGIES))
        for r in res.values():
            for k in ev.SUMMARY_KEYS:
                self.assertIsNotNone(r[k])
            self.assertGreaterEqual(r["continuation_5"], r["continuation_10"])
            self.assertGreaterEqual(r["continuation_10"], r["continuation_20"])
            self.assertEqual(r["duration"]["n"], 100)
        # 同じ条件なら同じ結果（決定的）
        again = ev.compare_strategies(self.sc, self.params, events, ["greedy"], 50, (0, 1))
        self.assertEqual(again["greedy"]["continuation_10"], res["greedy"]["continuation_10"])

    def test_format_table(self):
        text = ev.format_table([{"a": "x", "b": 0.5}, {"a": "yy", "b": None}], [("a", "A", "{}"), ("b", "B", "{:.1f}")])
        self.assertIn("0.5", text)
        self.assertIn("-", text.splitlines()[2])


if __name__ == "__main__":
    unittest.main()
