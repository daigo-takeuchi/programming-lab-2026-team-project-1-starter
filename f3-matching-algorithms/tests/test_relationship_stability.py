# F3：relationship_stability.py のテスト（教育用の架空モデルの動作確認）

import random
import unittest

import relationship_stability as rs


def params(**kw):
    p = {"baseline_hazard": 0.08, "alpha": 0.04, "beta": 0.02, "gamma": 0.03, "default_annual_stress": 0.3,
         "default_conflict_resolution": 0.5, "simulation_years": 20, "random_seed": 42}
    p.update(kw)
    return p


def pair(a="A1", b="B1", compat=0.7):
    return {"pair_id": f"{a}-{b}", "participant_ids": [a, b], "algorithm": "test",
            "initial_compatibility": compat, "initial_satisfaction": None}


class TestProbability(unittest.TestCase):
    def test_range(self):
        for c in (0, 0.5, 1):
            for s in (0, 0.5, 1):
                for cr in (0, 1):
                    p = rs.annual_dissolution_probability(c, cr, s, params())
                    self.assertTrue(0 <= p <= 1)
        self.assertEqual(rs.annual_dissolution_probability(1, 1, 0, params(baseline_hazard=0.0)), 0.0)  # 負 → 0
        self.assertEqual(rs.annual_dissolution_probability(0, 0, 1, params(baseline_hazard=1.0)), 1.0)  # 1 超 → 1

    def test_formula(self):
        p = rs.annual_dissolution_probability(0.5, 0.5, 0.3, params())
        self.assertAlmostEqual(p, 0.08 - 0.04 * 0.5 - 0.02 * 0.5 + 0.03 * 0.3)

    def test_compatibility_effect(self):
        lo = rs.annual_dissolution_probability(0.2, 0.5, 0.3, params())
        hi = rs.annual_dissolution_probability(0.9, 0.5, 0.3, params())
        self.assertLess(hi, lo)                                   # モデル上、適合度が高いほど解消確率は低い
        ctrl = rs.control_parameters(params())
        self.assertEqual(rs.annual_dissolution_probability(0.2, 0.5, 0.3, ctrl),
                         rs.annual_dissolution_probability(0.9, 0.5, 0.3, ctrl))   # 対照：影響なし

    def test_stress_effect(self):
        self.assertGreater(rs.annual_dissolution_probability(0.7, 0.5, 0.9, params()),
                           rs.annual_dissolution_probability(0.7, 0.5, 0.1, params()))

    def test_invalid(self):
        with self.assertRaises(ValueError):
            rs.annual_dissolution_probability(1.2, 0.5, 0.3, params())
        with self.assertRaises(ValueError):
            rs.with_changes(params(), alpha=-0.1)
        with self.assertRaises(ValueError):
            rs.with_changes(params(), simulation_years=0)

    def test_load_parameters(self):
        p = rs.load_parameters()
        self.assertEqual(p["baseline_hazard"], 0.08)
        self.assertEqual(p["simulation_years"], 20)


class TestSimulation(unittest.TestCase):
    def test_no_restart_and_year(self):
        class FixedRng:                                           # 3 年目に初めて p を下回る乱数列
            def __init__(self):
                self.vals = iter([0.9, 0.9, 0.01, 0.9, 0.9])
            def random(self):
                return next(self.vals)
        r = rs.simulate_pair(0.05, 5, FixedRng())
        self.assertEqual(r, {"dissolved": True, "dissolution_year": 3, "years_continued": 2, "censored": False})
        rec = dict(r, observed_years=5)
        self.assertEqual([rs.status_at(rec, t) for t in range(0, 6)], [True, True, True, False, False, False])

    def test_checkpoints(self):
        rec = {"dissolution_year": 7, "observed_years": 20}
        self.assertTrue(rs.status_at(rec, 5))
        self.assertFalse(rs.status_at(rec, 10))
        self.assertFalse(rs.status_at(rec, 20))
        self.assertTrue(rs.status_at({"dissolution_year": None, "observed_years": 20}, 20))
        self.assertIsNone(rs.status_at({"dissolution_year": None, "observed_years": 8}, 10))   # 観測期間の外

    def test_censoring(self):
        recs = rs.simulate_pairs([pair()], params(baseline_hazard=0.0, gamma=0.0), years=10)
        r = recs[0]
        self.assertFalse(r["dissolved"])
        self.assertTrue(r["censored"])
        self.assertIsNone(r["dissolution_year"])
        self.assertEqual(r["years_continued"], 10)
        self.assertIsNone(r["continuing_20y"])                    # 10 年しか観測していないので 20 年後は不明

    def test_reproducible(self):
        pairs = [pair("A1", "B1", 0.9), pair("A2", "B2", 0.4)]
        self.assertEqual(rs.monte_carlo(pairs, params(), 5), rs.monte_carlo(pairs, params(), 5))
        self.assertNotEqual(rs.simulate_pairs(pairs, params(), seed=1), rs.simulate_pairs(pairs, params(), seed=2))

    def test_common_random_numbers(self):
        # 同じペア・同じ反復なら、アルゴリズム（一緒にいる他のペア）に関係なく同じ結果
        x = rs.simulate_pairs([pair("A1", "B1"), pair("A2", "B2")], params(), replicate=3)[0]
        y = rs.simulate_pairs([pair("A1", "B1"), pair("A3", "B4")], params(), replicate=3)[0]
        self.assertEqual(x["dissolution_year"], y["dissolution_year"])

    def test_zero_and_one(self):
        never = params(baseline_hazard=0.0, alpha=0.0, beta=0.0, gamma=0.0)
        recs = rs.simulate_pairs([pair(a=f"A{i}") for i in range(20)], never)
        self.assertTrue(all(not r["dissolved"] and r["continuing_20y"] for r in recs))
        always = params(baseline_hazard=1.0, alpha=0.0, beta=0.0, gamma=0.0)
        recs = rs.simulate_pairs([pair(a=f"A{i}") for i in range(20)], always)
        self.assertTrue(all(r["dissolution_year"] == 1 and r["years_continued"] == 0 for r in recs))

    def test_theoretical_survival(self):
        self.assertAlmostEqual(rs.theoretical_survival(0.1, 2), 0.81)
        p_target = 0.08 - 0.04 * 0.5 - 0.02 * 0.5 + 0.03 * 0.3   # 0.059
        pairs = [pair(a=f"A{i}", b=f"B{i}", compat=0.5) for i in range(4000)]
        recs = rs.simulate_pairs(pairs, params())
        for t in (5, 10, 20):
            sim = sum(1 for r in recs if rs.status_at(r, t)) / len(recs)
            self.assertAlmostEqual(sim, rs.theoretical_survival(p_target, t), delta=0.03, msg=f"{t} 年")

    def test_export_for_f4(self):
        data = rs.export_pairs_for_f4([dict(pair(), initial_satisfaction=0.8)], params())
        self.assertEqual(data["format"], rs.F4_FORMAT_VERSION)
        p = data["pairs"][0]
        for key in ("pair_id", "participant_ids", "initial_compatibility", "initial_satisfaction", "matching_algorithm"):
            self.assertIn(key, p)
        self.assertEqual(data["relationship_parameters"]["alpha"], 0.04)


if __name__ == "__main__":
    unittest.main()
