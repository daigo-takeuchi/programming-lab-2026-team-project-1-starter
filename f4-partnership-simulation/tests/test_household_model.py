import copy
import unittest

from tests import _helpers  # noqa: F401
import partners as pt
import household_model as hm
import relationship_dynamics as rd


class TestHouseholdModel(unittest.TestCase):
    def setUp(self):
        self.sc = pt.scenario_by_id(pt.load_scenarios(), "A")
        self.p = self.sc["partners"]
        self.hh = self.sc["household"]
        self.params = rd.load_parameters()
        self.cond = dict(self.hh, stress=self.params["base_stress"])

    def test_housework_total(self):
        for x in (0, 0.3, 0.5, 0.8, 1):
            a, b = hm.housework_hours(x, 30)
            self.assertAlmostEqual(a + b, 30)
            self.assertAlmostEqual(a, 30 * x)
        with self.assertRaises(ValueError):
            hm.housework_hours(1.2, 30)

    def test_financial_total(self):
        for y in (0, 0.25, 0.5, 1):
            a, b = hm.financial_amounts(y, 360)
            self.assertAlmostEqual(a + b, 360)
        with self.assertRaises(ValueError):
            hm.financial_amounts(-0.1, 360)

    def test_income_share(self):
        self.assertAlmostEqual(hm.income_share(self.p), 330 / 850)
        a, b = hm.financial_amounts(hm.income_share(self.p), 360)
        self.assertAlmostEqual(a / b, 330 / 520)
        zero = copy.deepcopy(self.p)
        zero["A"]["annual_income"] = zero["B"]["annual_income"] = 0
        self.assertEqual(hm.income_share(zero), 0.5)

    def test_equal_share(self):
        self.assertEqual(hm.equal_share(), 0.5)
        self.assertEqual(hm.initial_allocation(self.sc), (0.5, 0.5))
        self.assertEqual(hm.housework_hours(hm.equal_share(), 30), (15.0, 15.0))

    def test_other_rules(self):
        self.assertAlmostEqual(hm.work_hours_housework_share(self.p), 45 / 80)
        self.assertAlmostEqual(hm.income_housework_share(self.p), 520 / 850)
        self.assertAlmostEqual(hm.preference_housework_share(self.p), (0.5 + 1 - 0.3) / 2)
        x = hm.equal_workload_housework_share(self.p, 30)
        ha, hb = hm.housework_hours(x, 30)
        self.assertAlmostEqual(35 + ha, 45 + hb)          # 労働 + 家事 が等しい
        self.assertEqual(hm.apply_rule(0.8, self.p, "housework"), 0.8)

    def test_infeasible_allocation(self):
        self.assertTrue(hm.is_feasible(0.5, 0.5, self.p, self.hh))
        self.assertFalse(hm.is_feasible(0.8, 0.5, self.p, self.hh))      # A：24 時間 > 22 時間
        self.assertFalse(hm.is_feasible(0.2, 0.5, self.p, self.hh))      # B：24 時間 > 15 時間
        ov = hm.overloads(0.8, 0.5, self.p, self.hh)
        self.assertAlmostEqual(ov["A"]["housework_hours"], 2.0)
        self.assertEqual(len(hm.feasibility_report(0.8, 0.5, self.p, self.hh)), 1)
        poor = copy.deepcopy(self.p)
        poor["A"]["annual_income"] = 100
        self.assertFalse(hm.is_feasible(0.5, 0.5, poor, self.hh))        # 生活費 180 > 所得 100

    def test_utility_range_and_penalty(self):
        for x in (0, 0.5, 1):
            for y in (0, 0.5, 1):
                ua, ub = hm.utilities(x, y, self.p, self.cond, self.params)
                self.assertTrue(0 <= ua <= 1 and 0 <= ub <= 1)
        ok = hm.utility("A", 0.7, 0.5, self.p, self.cond, self.params)
        over = hm.utility("A", 0.8, 0.5, self.p, self.cond, self.params)
        self.assertLess(over, ok)                                        # 超過は減点

    def test_utility_formula(self):
        # 家事・生活費が希望どおり、ストレス・超過・不公平感・家計の圧迫がないときの値を手計算と比べる
        params = dict(self.params, w_free_time=0.0)
        p = copy.deepcopy(self.p)
        cond = dict(self.hh, stress=0.0)
        c = hm.utility_components("A", 0.5, 0.4, p, cond, params)
        self.assertEqual(c["housework_mismatch"], 0.0)
        self.assertAlmostEqual(c["financial_mismatch"], 0.0)
        self.assertEqual(c["unfairness"], 0.0)
        expected = params["base_satisfaction"] + params["w_communication"] * 0.5
        self.assertAlmostEqual(hm.utility("A", 0.5, 0.4, p, cond, params), expected)

    def test_communication_and_stress_effects(self):
        low = copy.deepcopy(self.p)
        high = copy.deepcopy(self.p)
        for pid in pt.PARTNERS:
            low[pid]["communication_score"] = 0.1
            high[pid]["communication_score"] = 0.9
        self.assertGreater(hm.utility("B", 0.5, 0.5, high, self.cond, self.params),
                           hm.utility("B", 0.5, 0.5, low, self.cond, self.params))
        calm = dict(self.hh, stress=0.0)
        hard = dict(self.hh, stress=0.5)
        self.assertGreater(hm.utility("A", 0.5, 0.5, self.p, calm, self.params),
                           hm.utility("A", 0.5, 0.5, self.p, hard, self.params))

    def test_satisfaction_summary(self):
        s = hm.satisfaction_summary(0.8, 0.5)
        self.assertAlmostEqual(s["mean"], 0.65)
        self.assertEqual(s["min"], 0.5)
        self.assertAlmostEqual(s["diff"], 0.3)


if __name__ == "__main__":
    unittest.main()
