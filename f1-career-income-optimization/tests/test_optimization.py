# F1：optimization.py のテスト

import copy
import unittest

import income_analysis as ia
import optimization as op
import scenarios as sc


def switching(new_salary=200, cost=0, growth=0.0, retirement_age=25):
    return {"name": "t", "label": "t", "start_age": 18, "initial_salary": 100, "annual_growth_rate": 0.0,
            "retirement_age": retirement_age, "education_cost": 0, "certificate": None,
            "job_change": {"age": 20, "new_salary": new_salary, "growth_rate": growth, "cost": cost}}


class TestCandidates(unittest.TestCase):
    def test_range(self):
        self.assertEqual(op.switch_age_candidates(switching(), 19, 22), [19, 20, 21, 22])

    def test_excludes_invalid_ages(self):
        # 就職開始年齢（18）以前と、退職年齢（25）以降は候補にしない
        self.assertEqual(op.switch_age_candidates(switching(), 15, 30), [19, 20, 21, 22, 23, 24])

    def test_sample_range(self):
        careers, settings = sc.load_scenarios()
        jc = next(s for s in careers if s["name"] == "job_change")
        self.assertEqual(op.switch_age_candidates(jc, 22, 60), list(range(22, 61)))


class TestEvaluate(unittest.TestCase):
    def test_gross_per_candidate(self):
        rows = op.evaluate_switch_ages(switching(), [19, 24])
        # 19 歳で転職：100 + 200 × 6 = 1300、24 歳で転職：100 × 6 + 200 = 800
        self.assertAlmostEqual(rows[0]["gross"], 1300)
        self.assertAlmostEqual(rows[1]["gross"], 800)
        self.assertEqual([r["switch_age"] for r in rows], [19, 24])

    def test_requires_job_change(self):
        s = switching()
        s["job_change"] = None
        with self.assertRaises(ValueError):
            op.evaluate_switch_ages(s, [20])

    def test_original_not_modified(self):
        s = switching()
        before = copy.deepcopy(s)
        op.evaluate_switch_ages(s, op.switch_age_candidates(s, 19, 24))
        self.assertEqual(s, before)


class TestBest(unittest.TestCase):
    def test_max_selected(self):
        rows = op.evaluate_switch_ages(switching(), op.switch_age_candidates(switching(), 19, 24))
        best = op.optimal_switch_ages(rows)
        self.assertEqual(best["gross"]["switch_age"], 19)        # 早く転職するほど年収が高い期間が長い
        self.assertAlmostEqual(best["gross"]["value"], 1300)

    def test_lower_new_salary_prefers_late(self):
        rows = op.evaluate_switch_ages(switching(new_salary=50), op.switch_age_candidates(switching(), 19, 24))
        self.assertEqual(op.optimal_switch_ages(rows)["gross"]["switch_age"], 24)

    def test_npv_optimization(self):
        # 転職直後の年収が下がり、費用もかかる条件：割引しないと早い転職、割引率 3% では遅い転職が NPV 最大になる
        careers, _ = sc.load_scenarios()
        jc = next(s for s in careers if s["name"] == "job_change")
        s = sc.with_changes(jc, **{"job_change.new_salary": 250, "job_change.growth_rate": 0.025,
                                   "job_change.cost": 100})
        ages = op.switch_age_candidates(s, 22, 60)
        best0 = op.optimal_switch_ages(op.evaluate_switch_ages(s, ages, 0.0))
        rows3 = op.evaluate_switch_ages(s, ages, 0.03)
        best3 = op.optimal_switch_ages(rows3)
        self.assertEqual(best0["npv"]["switch_age"], best0["net"]["switch_age"])   # r = 0 なら NPV = 累積純収入
        self.assertEqual(best3["gross"]["switch_age"], 22)
        self.assertEqual(best3["npv"]["switch_age"], 60)
        self.assertEqual(max(r["npv"] for r in rows3), best3["npv"]["value"])

    def test_empty_candidates(self):
        self.assertIsNone(op.best_by([], "gross"))
        self.assertEqual(op.optimal_switch_ages([]), {"gross": None, "net": None, "npv": None})
        self.assertEqual(op.evaluate_switch_ages(switching(), []), [])

    def test_tie_rule_first_candidate(self):
        # new_salary = initial_salary、費用 0、昇給なし → どの年齢で転職しても同じ値。最も若い（最初の）候補を選ぶ
        rows = op.evaluate_switch_ages(switching(new_salary=100), [22, 20, 21])
        self.assertEqual(len({r["gross"] for r in rows}), 1)
        self.assertEqual(op.best_by(rows, "gross")["switch_age"], 22)   # リストで最初に現れるもの
        rows_sorted = op.evaluate_switch_ages(switching(new_salary=100), [20, 21, 22])
        self.assertEqual(op.best_by(rows_sorted, "gross")["switch_age"], 20)


class TestRank(unittest.TestCase):
    def test_descending_and_stable(self):
        results = [{"label": "a", "v": 1}, {"label": "b", "v": 3}, {"label": "c", "v": 3}, {"label": "d", "v": 2}]
        ranked = op.rank(results, "v")
        self.assertEqual([r["label"] for r in ranked], ["b", "c", "d", "a"])
        self.assertEqual([r["label"] for r in results], ["a", "b", "c", "d"])    # 元のリストは変更しない

    def test_sample_ranking(self):
        careers, _ = sc.load_scenarios()
        ranked = op.rank([ia.evaluate(s) for s in careers], "gross")
        self.assertEqual(len(ranked), len(careers))
        self.assertTrue(all(ranked[i]["gross"] >= ranked[i + 1]["gross"] for i in range(len(ranked) - 1)))


if __name__ == "__main__":
    unittest.main()
