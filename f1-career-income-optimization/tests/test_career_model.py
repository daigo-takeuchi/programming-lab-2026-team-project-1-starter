# F1：career_model.py のテスト

import unittest
import warnings

import career_model as cm


class TestIncomeByAge(unittest.TestCase):
    def test_values(self):
        inc = cm.income_by_age(start_age=18, initial_salary=100, annual_growth_rate=0.1, retirement_age=21)
        self.assertEqual(len(inc), 3)                      # 18, 19, 20 歳
        for got, want in zip(inc, [100, 110, 121]):
            self.assertAlmostEqual(got, want)

    def test_formula(self):
        # salary(a) = initial × (1 + g)^(a − start)
        self.assertAlmostEqual(cm.salary_at(30, 20, 280, 0.02), 280 * 1.02 ** 10)

    def test_zero_before_start(self):
        inc = cm.income_by_age(start_age=22, initial_salary=330, annual_growth_rate=0.025)
        self.assertEqual(inc[:4], [0.0, 0.0, 0.0, 0.0])    # 18〜21 歳
        self.assertEqual(inc[cm.index_of_age(22)], 330)

    def test_retirement_age_excluded(self):
        inc = cm.income_by_age(start_age=18, initial_salary=250, annual_growth_rate=0.02, retirement_age=65)
        self.assertEqual(len(inc), 65 - 18)                # 18〜64 歳の 47 年
        self.assertEqual(cm.ages()[-1], 64)
        with self.assertRaises(ValueError):
            cm.salary_at(65, 18, 250, 0.02, retirement_age=65)
        with self.assertRaises(ValueError):
            cm.index_of_age(65)

    def test_zero_growth(self):
        inc = cm.income_by_age(start_age=18, initial_salary=300, annual_growth_rate=0.0, retirement_age=25)
        self.assertEqual(inc, [300] * 7)

    def test_negative_growth_allowed(self):
        inc = cm.income_by_age(18, 100, -0.1, retirement_age=20)
        self.assertAlmostEqual(inc[1], 90)


class TestValidation(unittest.TestCase):
    def test_age_must_be_int(self):
        with self.assertRaises(TypeError):
            cm.income_by_age(18.5, 250, 0.02)
        with self.assertRaises(TypeError):
            cm.income_by_age(True, 250, 0.02)

    def test_start_before_retirement(self):
        with self.assertRaises(ValueError):
            cm.income_by_age(65, 250, 0.02, retirement_age=65)
        with self.assertRaises(ValueError):
            cm.income_by_age(70, 250, 0.02, retirement_age=65)

    def test_start_not_before_base_age(self):
        with self.assertRaises(ValueError):
            cm.income_by_age(16, 250, 0.02)

    def test_negative_salary(self):
        with self.assertRaises(ValueError):
            cm.income_by_age(18, -1, 0.02)

    def test_invalid_growth_rate(self):
        with self.assertRaises(ValueError):
            cm.income_by_age(18, 250, -1.0)
        with self.assertRaises(ValueError):
            cm.income_by_age(18, 250, -1.5)
        with self.assertRaises(TypeError):
            cm.income_by_age(18, 250, "2%")

    def test_extreme_growth_rate_warns(self):
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("always")
            cm.income_by_age(18, 250, 0.5)
        self.assertTrue(any(issubclass(x.category, UserWarning) for x in w))

    def test_invalid_period(self):
        with self.assertRaises(ValueError):
            cm.ages(retirement_age=18, base_age=18)


if __name__ == "__main__":
    unittest.main()
