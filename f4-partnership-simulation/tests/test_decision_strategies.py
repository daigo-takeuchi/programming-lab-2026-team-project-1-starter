import itertools
import unittest

from tests import _helpers  # noqa: F401
import partners as pt
import household_model as hm
import decision_strategies as ds
import relationship_dynamics as rd


class TestDecisionStrategies(unittest.TestCase):
    def setUp(self):
        self.sc = pt.scenario_by_id(pt.load_scenarios(), "A")
        self.p = self.sc["partners"]
        self.params = rd.load_parameters()
        self.cond = dict(self.sc["household"], stress=self.params["base_stress"])
        self.cands = ds.candidate_grid(0.1)

    def _brute_force(self, key):
        """比較用：Python の max で全探索（同点は候補の並び順で最初）"""
        feas = [c for c in self.cands if hm.is_feasible(*c, self.p, self.cond)]
        return max(feas, key=lambda c: (key(*hm.utilities(*c, self.p, self.cond, self.params)), -feas.index(c)))

    def test_grid(self):
        self.assertEqual(ds.share_grid(0.1), [0.0, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0])
        self.assertEqual(len(ds.candidate_grid(0.1)), 121)
        self.assertEqual(len(ds.candidate_grid(0.25)), 25)
        with self.assertRaises(ValueError):
            ds.share_grid(0.3)

    def test_fixed(self):
        self.assertEqual(ds.fixed_allocation((0.8, 0.5)), (0.8, 0.5))
        self.assertEqual(ds.decide("fixed", (0.3, 0.6), self.p, self.cond, self.params, self.cands), (0.3, 0.6))

    def test_greedy(self):
        best = ds.greedy_allocation(self.p, self.cond, self.params, self.cands)
        self.assertEqual(best, self._brute_force(lambda a, b: (a + b) / 2))
        self.assertTrue(hm.is_feasible(*best, self.p, self.cond))
        ua, ub = hm.utilities(*best, self.p, self.cond, self.params)
        for c in self.cands:
            if hm.is_feasible(*c, self.p, self.cond):
                va, vb = hm.utilities(*c, self.p, self.cond, self.params)
                self.assertLessEqual(va + vb, ua + ub + 1e-12)

    def test_fairness_aware(self):
        lam = self.params["fairness_lambda"]
        best = ds.fairness_allocation(self.p, self.cond, self.params, self.cands)
        self.assertEqual(best, self._brute_force(lambda a, b: (a + b) / 2 - lam * abs(a - b)))
        g = ds.greedy_allocation(self.p, self.cond, self.params, self.cands)
        fa, fb = hm.utilities(*best, self.p, self.cond, self.params)
        ga, gb = hm.utilities(*g, self.p, self.cond, self.params)
        self.assertLessEqual(abs(fa - fb), abs(ga - gb) + 1e-12)     # 差は Greedy 以下
        # λ = 0 なら Greedy と同じ
        self.assertEqual(ds.fairness_allocation(self.p, self.cond, self.params, self.cands, lam=0.0), g)
        # λ = 0.5 なら最低満足度の最大化と同じ値
        half = ds.fairness_allocation(self.p, self.cond, self.params, self.cands, lam=0.5)
        self.assertAlmostEqual(min(hm.utilities(*half, self.p, self.cond, self.params)),
                               min(hm.utilities(*self._brute_force(min), self.p, self.cond, self.params)))

    def test_adaptive(self):
        cur = (0.5, 0.5)
        self.assertEqual(ds.adaptive_allocation(cur, self.p, self.cond, self.params, self.cands, False), cur)
        new = ds.adaptive_allocation(cur, self.p, self.cond, self.params, self.cands, True)
        self.assertLessEqual(abs(new[0] - cur[0]), 0.1 + 1e-9)       # 1 目盛りまでしか動かない
        self.assertLessEqual(abs(new[1] - cur[1]), 0.1 + 1e-9)
        near = ds.neighbors(cur, self.cands, 0.1)
        self.assertEqual(len(near), 9)
        lam = self.params["fairness_lambda"]
        obj = lambda c: ds.objective(*hm.utilities(*c, self.p, self.cond, self.params), "fairness", lam)
        self.assertAlmostEqual(obj(new), max(obj(c) for c in near if hm.is_feasible(*c, self.p, self.cond)))

    def test_needs_review(self):
        hist = [{"relationship_satisfaction": v} for v in (0.7, 0.68, 0.66)]
        self.assertTrue(ds.needs_review(2, hist, self.params))            # 下がった
        self.assertFalse(ds.needs_review(3, hist, self.params))           # 見直しの年ではない
        self.assertTrue(ds.needs_review(3, hist, self.params, event_year=True))
        up = [{"relationship_satisfaction": v} for v in (0.7, 0.72, 0.75)]
        self.assertFalse(ds.needs_review(2, up, self.params))             # 上がっていて、しきい値以上

    def test_deterministic(self):
        for s in ds.STRATEGIES:
            a = ds.decide(s, (0.5, 0.5), self.p, self.cond, self.params, self.cands, True)
            b = ds.decide(s, (0.5, 0.5), self.p, self.cond, self.params, self.cands, True)
            self.assertEqual(a, b)

    def test_no_candidates(self):
        tiny = pt.with_partner_changes(self.sc, "A", available_housework_hours=0)
        tiny = pt.with_partner_changes(tiny, "B", available_housework_hours=0)
        self.assertEqual(ds.feasible_candidates(self.cands, tiny["partners"], self.cond), [])
        strict = dict(self.params, infeasible_fallback=False)
        self.assertIsNone(ds.greedy_allocation(tiny["partners"], self.cond, strict, self.cands))
        self.assertIsNone(ds.fairness_allocation(tiny["partners"], self.cond, strict, self.cands))
        self.assertIsNone(ds.adaptive_allocation((0.5, 0.5), tiny["partners"], self.cond, strict,
                                                 self.cands, True))
        # 候補がないとき、シミュレーションは前年の分担を続ける
        out = rd.simulate(tiny, "greedy", rd.with_changes(strict, baseline_hazard=0.0, beta=0.0, gamma=0.0), years=3)
        self.assertTrue(all(r["no_candidate"] for r in out["records"][1:]))
        self.assertEqual({(r["housework_share"], r["financial_share"]) for r in out["records"]}, {(0.5, 0.5)})
        self.assertIsNone(ds.best_candidate([], self.p, self.cond, self.params))
        with self.assertRaises(ValueError):
            ds.decide("unknown", (0.5, 0.5), self.p, self.cond, self.params, self.cands)

    def test_infeasible_fallback(self):
        # 家事の総時間が 2 人の家事に使える時間の合計（37 時間）を超えると、実行可能な候補はない
        cond = dict(self.cond, total_housework_hours=40)
        self.assertEqual(ds.feasible_candidates(self.cands, self.p, cond), [])
        self.assertEqual(ds.choice_set(self.cands, self.p, cond, self.params), self.cands)
        best = ds.greedy_allocation(self.p, cond, self.params, self.cands)
        self.assertIsNotNone(best)
        self.assertEqual(best, ds.best_candidate(self.cands, self.p, cond, self.params, "mean"))

    def test_tie_break_first_candidate(self):
        # すべての候補が同じ値なら最初の候補を選ぶ
        params = {k: (0 if k.startswith("w_") else v) for k, v in self.params.items()}
        # 実行可能なのは x = 0.5〜0.7（B は 15 時間まで、A は 22 時間まで）。並び順で最初は (0.5, 0.0)
        self.assertEqual(ds.greedy_allocation(self.p, self.cond, params, self.cands), (0.5, 0.0))

    def test_rank_strategies(self):
        ranked = ds.rank_strategies({"fixed": 0.4, "greedy": 0.6, "fairness": 0.6, "adaptive": 0.5})
        self.assertEqual([s for s, _ in ranked], ["fairness", "greedy", "adaptive", "fixed"])
        low = ds.rank_strategies({"a": 3, "b": 1, "c": 2}, higher_is_better=False)
        self.assertEqual([s for s, _ in low], ["b", "c", "a"])
        self.assertEqual(ds.rank_strategies({"a": None, "b": 1}), [("b", 1)])


if __name__ == "__main__":
    unittest.main()
