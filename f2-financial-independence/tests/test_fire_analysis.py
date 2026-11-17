# F2：fire_analysis.py のテスト

import unittest

import financial_model as fm
import fire_analysis as fa


class TestTarget(unittest.TestCase):
    def test_target(self):
        self.assertAlmostEqual(fa.fire_target(300, 0.04), 7500)
        self.assertAlmostEqual(fa.fire_target(320), 8000)
        self.assertEqual(fa.fire_target(0, 0.04), 0)

    def test_zero_withdrawal_rate_rejected(self):
        with self.assertRaises(ValueError):
            fa.fire_target(300, 0)
        with self.assertRaises(ValueError):
            fa.fire_target(300, -0.04)
        with self.assertRaises(ValueError):
            fa.fire_target(-1, 0.04)


class TestFireAge(unittest.TestCase):
    def setUp(self):
        # 資産（年齢時点）：20 歳 0、21 歳 100、22 歳 200、23 歳 300、24 歳 400、25 歳 500
        self.rows = fm.simulate_accumulation(20, 25, 0, 100, 1.0, 0.0)

    def test_fire_age(self):
        self.assertEqual(fa.fire_age(self.rows, 250), 23)
        self.assertEqual(fa.fire_age(self.rows, 300), 23)      # 「以上」なので等しい年齢で達成
        self.assertEqual(fa.fire_age(self.rows, 500), 25)      # 最後（終了年齢の時点）でも達成とみなす
        self.assertEqual(fa.years_to_fire(self.rows, 250), 3)

    def test_not_reached(self):
        self.assertIsNone(fa.fire_age(self.rows, 501))
        self.assertIsNone(fa.years_to_fire(self.rows, 10_000))

    def test_already_reached(self):
        rows = fm.simulate_accumulation(30, 35, 9000, 100, 0.2, 0.03)
        self.assertEqual(fa.fire_age(rows, 8000), 30)

    def test_sample_scenario(self):
        scenarios, settings = fm.load_scenarios()
        s = scenarios[0]
        rows = fm.accumulate(s, settings["accumulation_end_age"])
        age = fa.fire_age(rows, fa.fire_target(s["annual_expenses"]))
        self.assertGreaterEqual(fm.assets_at(rows, age), 8000)
        self.assertLess(fm.assets_at(rows, age - 1), 8000)     # その前の年齢では未達成


class TestBinarySearch(unittest.TestCase):
    def test_matches_linear(self):
        rows = fm.simulate_accumulation(22, 80, 0, 400, 0.3, 0.04)
        for target in [0, 1, 500, 5000, 7000, 20000, 1e9]:
            self.assertEqual(fa.fire_age_binary(rows, target), fa.fire_age(rows, target), target)

    def test_requires_monotonic(self):
        rows = fm.simulate_accumulation(22, 30, 1000, 0, 0.0, -0.1)   # 資産が減り続ける
        self.assertFalse(fa.is_nondecreasing(fm.assets_by_age(rows)[1]))
        with self.assertRaises(ValueError):
            fa.fire_age_binary(rows, 500)
        self.assertEqual(fa.fire_age(rows, 500), 22)                  # 線形探索なら使える


if __name__ == "__main__":
    unittest.main()
