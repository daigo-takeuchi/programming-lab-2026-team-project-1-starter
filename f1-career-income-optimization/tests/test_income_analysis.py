# F1：income_analysis.py と scenarios.py のテスト（小さな数値で手計算と照合する）

import unittest

import career_model as cm
import income_analysis as ia
import scenarios as sc

R = 25   # テスト用の退職年齢（18〜24 歳の 7 年間）


def simple(start_age=18, salary=100, growth=0.0, **extra):
    s = {"name": "t", "label": "t", "start_age": start_age, "initial_salary": salary,
         "annual_growth_rate": growth, "retirement_age": R, "education_cost": 0,
         "certificate": None, "job_change": None}
    s.update(extra)
    return s


class TestTotals(unittest.TestCase):
    def test_lifetime_gross(self):
        self.assertAlmostEqual(ia.lifetime_gross_income(simple()), 700)          # 100 × 7 年
        self.assertAlmostEqual(ia.lifetime_gross_income(simple(start_age=20)), 500)

    def test_total_and_cumulative(self):
        self.assertEqual(ia.total([]), 0)
        self.assertEqual(ia.cumulative([1, 2, 3]), [1, 3, 6])

    def test_education_cost_deducted(self):
        s = simple(start_age=20, education_cost=60)
        self.assertEqual(sc.costs(s)[:3], [30, 30, 0])                           # 18・19 歳に均等
        self.assertAlmostEqual(ia.cumulative_net_income(s), 500 - 60)

    def test_education_cost_needs_study_period(self):
        with self.assertRaises(ValueError):
            sc.costs(simple(start_age=18, education_cost=10))

    def test_certificate_cost_deducted(self):
        s = simple(certificate={"age": 20, "cost": 50, "salary_increase": 10,
                                "study_years": 0, "study_income_ratio": 1.0})
        inc = sc.incomes(s)
        self.assertEqual(inc[cm.index_of_age(20)], 100)                          # 取得した年はまだ増えない
        self.assertEqual(inc[cm.index_of_age(21)], 110)                          # 翌年から +10
        self.assertAlmostEqual(ia.lifetime_gross_income(s), 700 + 10 * 4)        # 21〜24 歳
        self.assertAlmostEqual(ia.career_costs(s), 50)
        self.assertAlmostEqual(ia.cumulative_net_income(s), 740 - 50)

    def test_certificate_study_income(self):
        s = simple(certificate={"age": 21, "cost": 0, "salary_increase": 0,
                                "study_years": 2, "study_income_ratio": 0.5})
        self.assertEqual(sc.incomes(s)[:4], [100, 50, 50, 100])                  # 19・20 歳は学習で半分

    def test_job_change_cost_deducted(self):
        s = simple(job_change={"age": 22, "new_salary": 200, "growth_rate": 0.0, "cost": 30})
        self.assertEqual(sc.incomes(s), [100, 100, 100, 100, 200, 200, 200])
        self.assertAlmostEqual(ia.cumulative_net_income(s), 1000 - 30)

    def test_invalid_job_change_age(self):
        with self.assertRaises(ValueError):
            sc.incomes(simple(start_age=20, job_change={"age": 20, "new_salary": 1, "growth_rate": 0, "cost": 0}))


class TestNPV(unittest.TestCase):
    def test_zero_rate_equals_net(self):
        for s in sc.load_scenarios()[0]:
            self.assertAlmostEqual(ia.scenario_npv(s, 0.0), ia.cumulative_net_income(s))

    def test_known_value(self):
        self.assertAlmostEqual(ia.npv([100, 110], 0.1), 100 + 110 / 1.1)

    def test_rate_changes_npv(self):
        s = simple()
        self.assertGreater(ia.scenario_npv(s, 0.0), ia.scenario_npv(s, 0.03))
        self.assertGreater(ia.scenario_npv(s, 0.03), ia.scenario_npv(s, 0.05))

    def test_invalid_rate(self):
        with self.assertRaises(ValueError):
            ia.npv([1], -1)
        with self.assertRaises(TypeError):
            ia.npv([1], "3%")


class TestPayback(unittest.TestCase):
    def test_recovered(self):
        base = simple()                                                           # 100 × 7
        edu = simple(start_age=20, salary=200, education_cost=0)                  # 0, 0, 200, ...
        # 累積差：-100, -200, -100, 0 → 21 歳で追いつく
        p = ia.payback_age(edu, base)
        self.assertEqual(p["status"], "recovered")
        self.assertEqual(p["payback_age"], 21)
        self.assertEqual(p["behind_from"], 18)

    def test_not_recovered(self):
        p = ia.payback_age(simple(start_age=20, salary=110), simple())
        self.assertEqual(p["status"], "not_recovered")
        self.assertIsNone(p["payback_age"])
        self.assertLess(p["final_gap"], 0)

    def test_never_behind(self):
        p = ia.payback_age(simple(salary=120), simple())
        self.assertEqual(p["status"], "never_behind")
        self.assertIsNone(p["payback_age"])

    def test_period_mismatch(self):
        with self.assertRaises(ValueError):
            ia.payback_age(simple(), simple(retirement_age=30))


class TestSampleData(unittest.TestCase):
    def test_load_and_units(self):
        careers, settings = sc.load_scenarios()
        self.assertEqual({s["name"] for s in careers} >= {"early_job", "university", "certificate", "job_change"}, True)
        self.assertEqual(settings["retirement_age"], 65)
        for s in careers:
            self.assertEqual(len(sc.incomes(s)), 65 - 18)


if __name__ == "__main__":
    unittest.main()
