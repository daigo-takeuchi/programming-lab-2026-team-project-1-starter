import time
import unittest

from tests import _helpers  # noqa: F401
import economic_model as em
import simulation as sim
import allocation_strategies as al
import evaluation as ev


class TestEvaluation(unittest.TestCase):
    def setUp(self):
        self.p = em.load_economy()
        self.recs = sim.simulate(al.equal_allocation(), self.p, 10)

    def test_growth_rate(self):
        self.assertAlmostEqual(ev.growth_rate(100, 150), 0.5)
        self.assertAlmostEqual(ev.annual_growth_rate(100, 121, 2), 0.1)
        g = ev.gdp_growth(self.recs)
        self.assertAlmostEqual(g["total"], self.recs[-1]["gdp"] / self.recs[0]["gdp"] - 1)
        self.assertAlmostEqual((1 + g["annual"]) ** 10, 1 + g["total"])

    def test_cumulative_gdp(self):
        self.assertAlmostEqual(ev.cumulative_gdp(self.recs), sum(r["gdp"] for r in self.recs[1:]))
        self.assertEqual(ev.cumulative_gdp(self.recs[:1]), 0)

    def test_living_standard(self):
        self.assertEqual(ev.final_living_standard(self.recs), self.recs[-1]["living_standard"])
        avg = sum(r["living_standard"] for r in self.recs[1:]) / 10
        self.assertAlmostEqual(ev.average_living_standard(self.recs), avg)
        self.assertEqual(ev.average_living_standard(self.recs[:1]), self.recs[0]["living_standard"])

    def test_investment_efficiency(self):
        e = ev.investment_efficiency(self.recs, "gdp")
        self.assertAlmostEqual(e, (self.recs[-1]["gdp"] - self.recs[0]["gdp"]) / (100 * 10))
        zero = sim.simulate(al.equal_allocation(), self.p, 3, budget=0)
        self.assertIsNone(ev.investment_efficiency(zero))

    def test_optimization_gap(self):
        self.assertEqual(ev.optimization_gap(10.0, 8.0), {"absolute": 2.0, "relative": 0.2})
        self.assertEqual(ev.optimization_gap(10.0, 10.0)["absolute"], 0.0)
        self.assertIsNone(ev.optimization_gap(0.0, 0.0)["relative"])

    def test_measure_time(self):
        result, t = ev.measure_time(sum, [1, 2, 3])
        self.assertEqual(result, 6)
        self.assertGreaterEqual(t, 0)
        _r, t2 = ev.measure_time(time.sleep, 0.01)
        self.assertGreaterEqual(t2, 0.009)
        cost = ev.computational_cost({"runtime_s": 0.1, "evaluations": 5, "iterations": 2, "other": 1})
        self.assertEqual(cost, {"runtime_s": 0.1, "evaluations": 5, "iterations": 2})

    def test_zero_division(self):
        self.assertIsNone(ev.growth_rate(0, 10))
        self.assertIsNone(ev.growth_rate(None, 10))
        self.assertIsNone(ev.annual_growth_rate(100, 120, 0))
        self.assertIsNone(ev.annual_growth_rate(0, 120, 5))
        self.assertIsNone(ev.annual_growth_rate(100, -1, 5))

    def test_summary_and_table(self):
        s = ev.summarize_run(self.recs)
        self.assertAlmostEqual(s["final_gdp"], self.recs[-1]["gdp"])
        text = ev.format_table([{"a": "x", "b": 1.234}, {"a": "y", "b": None}], [("a", "A", "{}"), ("b", "B", "{:.1f}")])
        self.assertIn("1.2", text)
        self.assertIn("-", text.splitlines()[2])


if __name__ == "__main__":
    unittest.main()
