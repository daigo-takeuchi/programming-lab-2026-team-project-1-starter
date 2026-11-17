# F2：optimization.py のテスト

import copy
import unittest

import financial_model as fm
import optimization as op


class TestCandidates(unittest.TestCase):
    def test_savings_rates(self):
        self.assertEqual(op.savings_rate_candidates(), [0.1, 0.2, 0.3, 0.4, 0.5])
        self.assertEqual(op.savings_rate_candidates([0.05, 0.15]), [0.05, 0.15])
        with self.assertRaises(ValueError):
            op.savings_rate_candidates([0.2, 1.2])

    def test_returns(self):
        self.assertEqual(op.return_candidates(), [0.0, 0.02, 0.04, 0.06, 0.08])
        with self.assertRaises(ValueError):
            op.return_candidates([-1.5])

    def test_candidates_are_copies(self):
        c = op.savings_rate_candidates()
        c.append(0.9)
        self.assertEqual(op.DEFAULT_SAVINGS_RATES, [0.1, 0.2, 0.3, 0.4, 0.5])


class TestSweep(unittest.TestCase):
    def setUp(self):
        self.scenarios, self.settings = fm.load_scenarios()
        self.std = self.scenarios[0]

    def test_savings_sweep_and_best(self):
        rows = op.sweep_savings_rate(self.std, [0.1, 0.2, 0.3], self.settings)
        self.assertEqual([r["param"] for r in rows], [0.1, 0.2, 0.3])
        self.assertIsNone(rows[0]["fire_age"])                          # 10% では 80 歳までに未達成
        self.assertAlmostEqual(rows[1]["annual_expenses"], 320)         # 所得固定：生活費も変わる
        b = op.best(rows, "fire_age", minimize=True)
        self.assertEqual(b["param"], 0.3)
        self.assertEqual(b["fire_age"], min(r["fire_age"] for r in rows if r["fire_age"] is not None))
        self.assertEqual(op.best(rows, "assets_at_report")["param"], 0.3)

    def test_keep_expenses(self):
        rows = op.sweep_savings_rate(self.std, [0.2, 0.4], self.settings, keep="expenses")
        self.assertTrue(all(abs(r["annual_expenses"] - 320) < 1e-9 for r in rows))
        self.assertAlmostEqual(rows[1]["annual_income"], 320 / 0.6)
        with self.assertRaises(ValueError):
            op.sweep_savings_rate(self.std, [1.0], self.settings, keep="expenses")

    def test_return_sweep(self):
        rows = op.sweep_return(self.std, [0.0, 0.04, 0.08], self.settings)
        ages = [r["fire_age"] for r in rows]
        self.assertIsNone(ages[0])
        self.assertGreater(ages[1], ages[2])

    def test_unreached_all(self):
        rows = op.sweep_return(self.std, [0.0], self.settings)
        self.assertIsNone(op.best(rows, "fire_age", minimize=True))

    def test_grid(self):
        m = op.grid_fire_age(self.std, [0.1, 0.5], [0.0, 0.08], self.settings)
        self.assertEqual(len(m), 2)
        self.assertEqual(len(m[0]), 2)
        self.assertIsNone(m[0][0])
        self.assertEqual(m[1][1], op.sweep_savings_rate(fm.with_changes(self.std, annual_return=0.08), [0.5],
                                                         self.settings)[0]["fire_age"])

    def test_original_not_modified(self):
        before = copy.deepcopy(self.std)
        op.sweep_savings_rate(self.std, op.DEFAULT_SAVINGS_RATES, self.settings)
        op.sweep_expenses(self.std, [200, 300], self.settings)
        self.assertEqual(self.std, before)


class TestBestAndRank(unittest.TestCase):
    def test_empty(self):
        self.assertIsNone(op.best([], "fire_age"))
        self.assertEqual(op.rank([], "fire_age"), [])

    def test_tie_rule_first(self):
        rows = [{"id": "a", "v": 50}, {"id": "b", "v": 40}, {"id": "c", "v": 40}, {"id": "d", "v": None}]
        self.assertEqual(op.best(rows, "v", minimize=True)["id"], "b")    # 同順位は候補リストで最初
        self.assertEqual(op.best(rows, "v")["id"], "a")

    def test_rank_none_last_and_stable(self):
        rows = [{"id": "a", "v": None}, {"id": "b", "v": 40}, {"id": "c", "v": 30}, {"id": "d", "v": 40}]
        self.assertEqual([r["id"] for r in op.rank(rows, "v", minimize=True)], ["c", "b", "d", "a"])
        self.assertEqual([r["id"] for r in op.rank(rows, "v")], ["b", "d", "c", "a"])
        self.assertEqual([r["id"] for r in rows], ["a", "b", "c", "d"])     # 元のリストは変更しない


class TestEvaluate(unittest.TestCase):
    def test_sample_values(self):
        scenarios, settings = fm.load_scenarios()
        r = op.evaluate_scenario(scenarios[0], settings)
        self.assertAlmostEqual(r["target"], 8000)
        self.assertIsNotNone(r["fire_age"])
        self.assertGreaterEqual(r["retire_assets"], r["target"])

    def test_unreached_has_no_retirement(self):
        scenarios, settings = fm.load_scenarios()
        r = op.evaluate_scenario(fm.with_changes(scenarios[0], annual_return=0.0), settings)
        self.assertIsNone(r["fire_age"])
        self.assertIsNone(r["depletion_age"])
        self.assertIsNone(r["sustainable"])


if __name__ == "__main__":
    unittest.main()
