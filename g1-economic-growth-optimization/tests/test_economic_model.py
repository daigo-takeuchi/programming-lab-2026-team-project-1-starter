import math
import unittest

from tests import _helpers  # noqa: F401
import economic_model as em


class TestEconomicModel(unittest.TestCase):
    def setUp(self):
        self.p = em.load_economy()

    def test_initial_states(self):
        s = em.initial_states(self.p)
        self.assertEqual(set(s), set(em.STATES))
        self.assertTrue(all(v == 1.0 for v in s.values()))
        pop = em.population_at(self.p, 0)
        self.assertAlmostEqual(em.compute_gdp(s, pop, self.p), self.p["initial_gdp"])     # 初年度 = 初期 GDP
        self.assertAlmostEqual(em.living_standard(s, self.p["initial_gdp"], pop, self.p), 1.0)

    def test_investment_effect(self):
        self.assertAlmostEqual(em.investment_effect(25, 0.02, 0.5), 0.02 * 5)
        self.assertEqual(em.investment_effect(0, 0.02, 0.5), 0.0)                    # 投資 0 でも動く
        self.assertAlmostEqual(em.investment_effect(10, 0.03, 1.0), 0.3)
        with self.assertRaises(ValueError):
            em.investment_effect(-1, 0.02)

    def test_diminishing_returns(self):
        m = [em.marginal_effect(x, 0.02, 0.5, 10) for x in (0, 10, 50, 100)]
        self.assertTrue(all(a > b for a, b in zip(m, m[1:])))                       # 追加効果は小さくなる
        lin = [em.marginal_effect(x, 0.02, 1.0, 10) for x in (0, 50)]
        self.assertAlmostEqual(lin[0], lin[1])                                     # 指数 1 なら逓減なし

    def test_depreciation(self):
        self.assertAlmostEqual(em.update_state(2.0, 0.05, 0.0), 1.9)
        self.assertAlmostEqual(em.update_state(2.0, 0.0, 0.3), 2.3)
        self.assertEqual(em.update_state(1.0, 1.0, 0.0), 0.0)
        x = 1.0
        for _ in range(500):
            x = em.update_state(x, 0.05, 0.1)
        self.assertAlmostEqual(x, 0.1 / 0.05, places=6)                            # 定常状態 = 効果 / 減耗率

    def test_delay(self):
        line = em.DelayLine(3)
        out = [line.push(v) for v in (1.0, 2.0, 3.0, 4.0, 5.0)]
        self.assertEqual(out, [0.0, 0.0, 0.0, 1.0, 2.0])                          # 3 年後に届く
        self.assertAlmostEqual(line.pending(), 3.0 + 4.0 + 5.0)
        self.assertEqual([em.DelayLine(0).push(v) for v in (1.0, 2.0)], [1.0, 2.0])   # 遅延なし
        with self.assertRaises(ValueError):
            em.DelayLine(-1)

    def test_gdp_non_negative(self):
        zero = {s: 0.0 for s in em.STATES}
        self.assertEqual(em.compute_gdp(zero, 100.0, self.p), 0.0)
        for v in (0.0, 0.5, 1.0, 3.0):
            states = {s: v for s in em.STATES}
            self.assertGreaterEqual(em.compute_gdp(states, 100.0, self.p), 0.0)
        bigger = {s: 2.0 for s in em.STATES}
        self.assertGreater(em.compute_gdp(bigger, 100.0, self.p), self.p["initial_gdp"])

    def test_gdp_decomposition(self):
        before = em.initial_states(self.p)
        after = dict(before, technology=2.0)
        d = em.gdp_decomposition(before, after, 100.0, 100.0, self.p)
        g0 = em.compute_gdp(before, 100.0, self.p)
        g1 = em.compute_gdp(after, 100.0, self.p)
        self.assertAlmostEqual(sum(v for v in d.values()), math.log(g1 / g0))      # 分解の合計 = log の変化
        self.assertAlmostEqual(d["technology"], self.p["gdp_elasticity_technology"] * math.log(2))
        self.assertEqual(d["health"], 0.0)

    def test_living_standard(self):
        s = em.initial_states(self.p)
        s["health"] = 2.0
        ls = em.living_standard(s, self.p["initial_gdp"], self.p["population"], self.p)
        self.assertAlmostEqual(ls, 1 + self.p["living_standard_weight_health"])     # 健康指数だけ +1
        p2 = em.with_changes(self.p, living_standard_weight_gdp_per_capita=1.0, living_standard_weight_health=0.0,
                             living_standard_weight_human_capital=0.0)
        self.assertAlmostEqual(em.living_standard(s, 2000.0, 100.0, p2), 2.0)

    def test_invalid_params(self):
        for ch in ({"living_standard_weight_health": 0.9}, {"health_depreciation": 1.5}, {"education_delay": -1},
                   {"education_delay": 1.5}, {"returns_exponent": 0}, {"population": 0}):
            with self.assertRaises(ValueError):
                em.with_changes(self.p, **ch)
        with self.assertRaises(ValueError):
            em.validate_params({"initial_gdp": 1.0})


if __name__ == "__main__":
    unittest.main()
