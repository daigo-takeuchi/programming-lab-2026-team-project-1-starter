import unittest

from tests import _helpers  # noqa: F401
import partners as pt
import decision_strategies as ds
import relationship_dynamics as rd


class TestRelationshipDynamics(unittest.TestCase):
    def setUp(self):
        self.sc = pt.scenario_by_id(pt.load_scenarios(), "A")
        self.params = rd.load_parameters()
        self.events = pt.load_stress_events()

    def test_update_satisfaction(self):
        self.assertAlmostEqual(rd.update_satisfaction(0.6, 0.9, 0.3), 0.7 * 0.6 + 0.3 * 0.9)
        self.assertEqual(rd.update_satisfaction(0.6, 0.9, 0.0), 0.6)    # alpha = 0：変わらない
        self.assertEqual(rd.update_satisfaction(0.6, 0.9, 1.0), 0.9)    # alpha = 1：今年の値

    def test_satisfaction_in_range(self):
        self.assertEqual(rd.update_satisfaction(1.0, 5.0, 0.5), 1.0)
        self.assertEqual(rd.update_satisfaction(0.0, -3.0, 0.5), 0.0)
        for s in ds.STRATEGIES:
            for r in rd.trajectory(self.sc, s, self.params, self.events["combined"]):
                for k in ("satisfaction_A", "satisfaction_B", "relationship_satisfaction"):
                    self.assertTrue(0 <= r[k] <= 1)

    def test_relationship_satisfaction(self):
        p0 = rd.with_changes(self.params, relationship_min_weight=0.0)
        p1 = rd.with_changes(self.params, relationship_min_weight=1.0)
        self.assertAlmostEqual(rd.relationship_satisfaction(0.8, 0.4, p0), 0.6)
        self.assertAlmostEqual(rd.relationship_satisfaction(0.8, 0.4, p1), 0.4)

    def test_stress_events(self):
        ev = [{"year": 5, "type": "income_change", "partner": "A", "change": -0.2, "stress": 0.2},
              {"year": 8, "type": "housework_change", "change": 10, "stress": 0.2},
              {"year": 3, "type": "expense_change", "change": 0.5, "duration": 2, "stress": 0.0},
              {"year": 2, "type": "work_hours_change", "partner": "B", "change": 5}]
        p4, c4 = rd.conditions_at(self.sc, ev, 4, self.params)
        self.assertEqual(p4["A"]["annual_income"], 330)
        self.assertAlmostEqual(c4["annual_expenses"], 540)             # Year 3〜4 だけ +50%
        self.assertEqual(p4["B"]["weekly_work_hours"], 50)
        self.assertEqual(p4["B"]["available_housework_hours"], 10)
        p5, c5 = rd.conditions_at(self.sc, ev, 5, self.params)
        self.assertAlmostEqual(p5["A"]["annual_income"], 264)
        self.assertAlmostEqual(c5["annual_expenses"], 360)
        self.assertAlmostEqual(c5["stress"], self.params["base_stress"] + 0.2)
        _p, c7 = rd.conditions_at(self.sc, ev, 7, self.params)
        self.assertAlmostEqual(c7["stress"], self.params["base_stress"])     # ストレスは 2 年で終わる
        p9, c9 = rd.conditions_at(self.sc, ev, 9, self.params)
        self.assertEqual(c9["total_housework_hours"], 40)
        self.assertAlmostEqual(p9["A"]["annual_income"], 264)               # 所得の変化は続く
        self.assertEqual(self.sc["partners"]["A"]["annual_income"], 330)    # 元のシナリオは変わらない
        with self.assertRaises(ValueError):
            rd.conditions_at(self.sc, [{"year": 1, "type": "lottery", "change": 1}], 1, self.params)
        with self.assertRaises(ValueError):
            rd.conditions_at(self.sc, [{"year": 1, "type": "income_change", "change": 1}], 1, self.params)

    def test_strategy_reacts_to_event(self):
        recs = rd.trajectory(self.sc, "adaptive", self.params, self.events["combined"])
        self.assertTrue(recs[5]["event"] and recs[5]["reviewed"])
        self.assertTrue(recs[8]["event"] and recs[8]["reviewed"])

    def test_dissolution_probability_range(self):
        self.assertEqual(rd.dissolution_probability(-5, 10, self.params), 1.0)
        p = rd.with_changes(self.params, baseline_hazard=0.0, beta=0.0, gamma=-1.0)
        self.assertEqual(rd.dissolution_probability(0.5, 1.0, p), 0.0)
        self.assertAlmostEqual(rd.dissolution_probability(0.6, 0.1, self.params),
                               self.params["baseline_hazard"] + self.params["beta"] * 0.4 + self.params["gamma"] * 0.1)

    def test_zero_probability_continues(self):
        p = rd.with_changes(self.params, baseline_hazard=0.0, beta=0.0, gamma=0.0)
        for rep in range(20):
            out = rd.simulate(self.sc, "fixed", p, self.events["combined"], replicate=rep)
            self.assertFalse(out["dissolved"])
            self.assertEqual(len(out["records"]), p["simulation_years"] + 1)

    def test_probability_one_dissolves_first_year(self):
        p = rd.with_changes(self.params, baseline_hazard=1.0)
        out = rd.simulate(self.sc, "greedy", p)
        self.assertTrue(out["dissolved"])
        self.assertEqual(out["dissolution_year"], 1)
        self.assertEqual(out["duration"], 1)
        self.assertEqual(len(out["records"]), 2)                    # 0 年目 + 1 年目だけ
        self.assertFalse(out["records"][-1]["continuing"])

    def test_no_update_after_dissolution(self):
        p = rd.with_changes(self.params, baseline_hazard=0.2)
        out = next(o for o in (rd.simulate(self.sc, "adaptive", p, replicate=r) for r in range(50))
                   if o["dissolved"] and o["dissolution_year"] < p["simulation_years"])
        self.assertEqual(out["records"][-1]["year"], out["dissolution_year"])
        self.assertEqual(sum(1 for r in out["records"] if not r["continuing"]), 1)

    def test_reproducible_with_seed(self):
        a = rd.simulate(self.sc, "fixed", self.params, self.events["combined"], seed=7, replicate=3)
        b = rd.simulate(self.sc, "fixed", self.params, self.events["combined"], seed=7, replicate=3)
        self.assertEqual(a, b)
        m1 = rd.monte_carlo(self.sc, "greedy", self.params, (), 50, seed=11)
        m2 = rd.monte_carlo(self.sc, "greedy", self.params, (), 50, seed=11)
        self.assertEqual(m1["outcomes"], m2["outcomes"])

    def test_monte_carlo_matches_simulate(self):
        mc = rd.monte_carlo(self.sc, "adaptive", self.params, self.events["combined"], 40, seed=3)
        for rep, o in enumerate(mc["outcomes"]):
            s = rd.simulate(self.sc, "adaptive", self.params, self.events["combined"], seed=3, replicate=rep)
            self.assertEqual(o["dissolution_year"], s["dissolution_year"])

    def test_common_random_numbers(self):
        # 解消確率が戦略によらず同じなら、解消年も同じになる（乱数が戦略によらない）
        p = rd.with_changes(self.params, beta=0.0, gamma=0.0, baseline_hazard=0.1)
        years = [rd.simulate(self.sc, s, p, seed=5, replicate=2)["dissolution_year"] for s in ds.STRATEGIES]
        self.assertEqual(len(set(years)), 1)

    def test_censoring(self):
        p = rd.with_changes(self.params, baseline_hazard=0.0, beta=0.0, gamma=0.0)
        out = rd.simulate(self.sc, "fixed", p, years=5)
        self.assertTrue(out["censored"])
        self.assertIsNone(out["dissolution_year"])
        self.assertEqual(out["duration"], 5)
        self.assertIsNone(rd.continued_at(out, 10))        # 観測期間外は分からない
        self.assertTrue(rd.continued_at(out, 5))

    def test_theoretical_survival_close_to_simulation(self):
        mc = rd.monte_carlo(self.sc, "fixed", self.params, self.events["combined"], 4000, seed=1)
        theory = rd.theoretical_survival(mc["trajectory"])
        for t in rd.CHECKPOINTS:
            rate = sum(rd.continued_at(o, t) for o in mc["outcomes"]) / 4000
            self.assertAlmostEqual(rate, theory[t], delta=0.03)


if __name__ == "__main__":
    unittest.main()
