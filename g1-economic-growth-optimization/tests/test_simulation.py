import unittest

from tests import _helpers  # noqa: F401
import economic_model as em
import simulation as sim
import allocation_strategies as al


class TestSimulation(unittest.TestCase):
    def setUp(self):
        self.p = em.load_economy()
        self.eq = al.equal_allocation()

    def test_horizons(self):
        for years in sim.HORIZONS:
            recs = sim.simulate(self.eq, self.p, years)
            self.assertEqual(len(recs), years + 1)
            self.assertEqual([r["year"] for r in recs], list(range(years + 1)))

    def test_yearly_update(self):
        p = em.with_changes(self.p, education_delay=0, rd_delay=0)
        recs = sim.simulate(self.eq, p, 2)
        inv = 100 * 0.25
        expected = (1 - p["technology_depreciation"]) * 1.0 + em.investment_effect(inv, p["rd_efficiency"], 0.5)
        self.assertAlmostEqual(recs[1]["technology"], expected)
        self.assertAlmostEqual(recs[2]["technology"],
                               (1 - p["technology_depreciation"]) * expected + em.investment_effect(inv, p["rd_efficiency"]))
        g = em.compute_gdp({s: recs[1][s] for s in em.STATES}, recs[1]["population"], p)
        self.assertAlmostEqual(recs[1]["gdp"], g)
        self.assertAlmostEqual(recs[1]["gdp_growth_rate"], (recs[1]["gdp"] - recs[0]["gdp"]) / recs[0]["gdp"])

    def test_delay_in_simulation(self):
        recs = sim.simulate(self.eq, self.p, 4)                    # 教育の遅延 3 年
        d = 1 - self.p["human_capital_depreciation"]
        self.assertAlmostEqual(recs[3]["human_capital"], d ** 3)    # 3 年目まで効果は届かない（減耗だけ）
        self.assertGreater(recs[4]["human_capital"], d ** 4)

    def test_records(self):
        recs = sim.simulate(self.eq, self.p, 3)
        for key in ("year", "gdp", "gdp_growth_rate", "human_capital", "technology", "infrastructure", "health",
                    "living_standard", "allocation", "investment"):
            self.assertIn(key, recs[1])
        self.assertIsNone(recs[0]["gdp_growth_rate"])
        self.assertEqual(sim.series(recs, "year"), [0, 1, 2, 3])

    def test_reproducible(self):
        self.assertEqual(sim.simulate(self.eq, self.p), sim.simulate(self.eq, self.p))

    def test_budget_consistency(self):
        shares = {"education": 0.1, "rd": 0.2, "infrastructure": 0.3, "healthcare": 0.4}
        recs = sim.simulate(shares, self.p, 2)
        for r in recs[1:]:
            self.assertAlmostEqual(r["total_investment"], self.p["annual_investment_budget"])
            self.assertAlmostEqual(r["investment"]["healthcare"], 40.0)
        self.assertAlmostEqual(sum(sim.annual_investments(shares, 250).values()), 250)

    def test_invalid_allocation(self):
        with self.assertRaises(ValueError):
            sim.simulate({"education": 0.5, "rd": 0.5, "infrastructure": 0.5, "healthcare": 0.0}, self.p)
        with self.assertRaises(ValueError):
            sim.simulate({"education": 1.0}, self.p)

    def test_zero_budget(self):
        recs = sim.simulate(self.eq, self.p, 5, budget=0)
        self.assertLess(recs[-1]["health"], 1.0)                    # 投資なし → 減耗だけ
        self.assertGreaterEqual(recs[-1]["gdp"], 0.0)


if __name__ == "__main__":
    unittest.main()
