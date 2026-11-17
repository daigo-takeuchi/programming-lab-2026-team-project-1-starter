import itertools
import unittest

from tests import _helpers  # noqa: F401
import economic_model as em
import simulation as sim
import allocation_strategies as al
import optimization as op


class TestOptimization(unittest.TestCase):
    def setUp(self):
        self.p = em.load_economy()

    def test_enumeration(self):
        for m in (1, 4, 10):
            cands = op.enumerate_allocations(m)
            self.assertEqual(len(cands), op.count_allocations(m))
            self.assertEqual(len(set(cands)), len(cands))
            self.assertTrue(all(sum(c) == m and min(c) >= 0 for c in cands))
        self.assertEqual(op.count_allocations(10), 286)
        self.assertEqual(op.count_allocations(20), 1771)
        self.assertEqual(op.enumerate_allocations(2)[0], (2, 0, 0, 0))

    def test_exhaustive_is_correct(self):
        ev_ = op.Evaluator(self.p, "final_gdp", 10)
        r = op.exhaustive(ev_, 5)
        # 比較用：itertools で 4 分野の組をすべて作り、合計 5 のものだけを評価する（別の方法の全探索）
        best = max(op.objective_value(sim.simulate(al.shares_from_units(c, 5), self.p, 10), self.p)
                   for c in itertools.product(range(6), repeat=4) if sum(c) == 5)
        self.assertAlmostEqual(r["objective"], best)
        self.assertEqual(r["evaluations"], 56)

    def test_greedy(self):
        ev_ = op.Evaluator(self.p, "final_gdp", 10)
        r = op.greedy(ev_, 10)
        self.assertEqual(sum(r["units"]), 10)
        self.assertEqual(r["evaluations"], 10 * 4)
        self.assertEqual(len(r["path"]), 10)
        values = [v for _u, v in r["path"]]
        self.assertTrue(all(a <= b + 1e-12 for a, b in zip(values, values[1:])))   # 予算を足すたびに良くなる

    def test_local_search(self):
        ev_ = op.Evaluator(self.p, "final_gdp", 10)
        r = op.local_search(ev_, 10, (10, 0, 0, 0))
        self.assertEqual(sum(r["units"]), 10)
        values = [v for _u, v in r["path"]]
        self.assertTrue(all(a < b for a, b in zip(values, values[1:])))           # 改善するときだけ移る
        best_neighbor = max(ev_(n, 10) for n in op.neighbors(r["units"]))
        self.assertLessEqual(best_neighbor, r["objective"] + 1e-12)               # 終了時は局所最適
        self.assertEqual(len(op.neighbors((10, 0, 0, 0))), 3)
        self.assertEqual(len(op.neighbors((3, 3, 2, 2))), 12)
        with self.assertRaises(ValueError):
            op.local_search(ev_, 10, (5, 0, 0, 0))

    def test_budget_constraint(self):
        res = op.compare_algorithms(self.p, "final_living_standard", 0.2, 10)
        for r in res.values():
            self.assertEqual(sum(r["units"]), r["m"])
            self.assertAlmostEqual(sum(r["shares"].values()), 1.0)
            self.assertTrue(all(0 <= v <= 1 for v in r["shares"].values()))
        with self.assertRaises(ValueError):
            op.Evaluator(self.p)((6, 6, 0, 0), 10)

    def test_exhaustive_is_upper_bound(self):
        for objective in op.OBJECTIVES:
            for expo in (0.5, 0.8):
                p = em.with_changes(self.p, returns_exponent=expo)
                for start in (None, {"education": 1.0, "rd": 0.0, "infrastructure": 0.0, "healthcare": 0.0}):
                    res = op.compare_algorithms(p, objective, 0.2, 10, start)
                    best = res["exhaustive"]["objective"]
                    self.assertGreaterEqual(best + 1e-12, res["greedy"]["objective"])
                    self.assertGreaterEqual(best + 1e-12, res["local_search"]["objective"])
                    self.assertGreaterEqual(res["greedy"]["gap"]["absolute"], -1e-12)

    def test_deterministic_ties(self):
        # 投資効果が 0（効率 0）なら、すべての候補が同点 → 列挙の最初の候補・分野の順で選ぶ
        p = em.with_changes(self.p, education_efficiency=0, rd_efficiency=0, infrastructure_efficiency=0,
                            healthcare_efficiency=0)
        self.assertEqual(op.exhaustive(op.Evaluator(p), 10)["units"], (10, 0, 0, 0))
        self.assertEqual(op.greedy(op.Evaluator(p), 10)["units"], (10, 0, 0, 0))
        self.assertEqual(op.local_search(op.Evaluator(p), 10, (3, 3, 2, 2))["units"], (3, 3, 2, 2))
        self.assertEqual(op.best_index([1, 3, 3, 2]), 1)
        a = op.compare_algorithms(self.p, "weighted", 0.2)
        b = op.compare_algorithms(self.p, "weighted", 0.2)
        self.assertEqual({k: v["units"] for k, v in a.items()}, {k: v["units"] for k, v in b.items()})

    def test_evaluation_count(self):
        e = op.Evaluator(self.p, "final_gdp", 5)
        e((10, 0, 0, 0), 10)
        e((0, 10, 0, 0), 10)
        self.assertEqual(e.evaluations, 2)
        e.records((10, 0, 0, 0), 10)
        self.assertEqual(e.evaluations, 2)                         # records は数えない
        res = op.compare_algorithms(self.p, "final_gdp", 0.25, 5)
        self.assertEqual(res["exhaustive"]["evaluations"], op.count_allocations(4))
        self.assertEqual(res["greedy"]["evaluations"], 4 * 4)
        self.assertGreater(res["local_search"]["evaluations"], 0)
        for r in res.values():
            self.assertGreaterEqual(r["runtime_s"], 0)

    def test_objectives(self):
        recs = sim.simulate(al.equal_allocation(), self.p, 5)
        self.assertEqual(op.objective_value(recs, self.p, "final_gdp"), recs[-1]["gdp"])
        self.assertAlmostEqual(op.objective_value(recs, self.p, "cumulative_gdp"), sum(r["gdp"] for r in recs[1:]))
        self.assertAlmostEqual(op.objective_value(recs, self.p, "weighted", 1.0), recs[-1]["gdp"] / 1000.0)
        self.assertAlmostEqual(op.objective_value(recs, self.p, "weighted", 0.0), recs[-1]["living_standard"])
        with self.assertRaises(ValueError):
            op.objective_value(recs, self.p, "happiness")
        with self.assertRaises(ValueError):
            op.Evaluator(self.p, "happiness")

    def test_ranking(self):
        ranked = op.rank_candidates(["a", "b", "c", "d"], [2.0, 5.0, 2.0, 1.0])
        self.assertEqual([c for c, _ in ranked], ["b", "a", "c", "d"])            # 同点は元の順
        self.assertEqual(op.rank_candidates(["a", "b"], [1, 2], top=1), [("b", 2)])


if __name__ == "__main__":
    unittest.main()
