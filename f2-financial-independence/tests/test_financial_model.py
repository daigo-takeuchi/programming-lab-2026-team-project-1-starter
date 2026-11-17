# F2：financial_model.py のテスト

import unittest
import warnings

import financial_model as fm


def sim(**kw):
    p = dict(start_age=20, end_age=23, initial_assets=0, annual_income=100, savings_rate=0.5, annual_return=0.1)
    p.update(kw)
    return fm.simulate_accumulation(**p)


class TestSavings(unittest.TestCase):
    def test_annual_savings(self):
        self.assertAlmostEqual(fm.annual_savings(400, 0.2), 80)
        self.assertAlmostEqual(fm.living_expenses(400, 0.2), 320)
        self.assertAlmostEqual(fm.savings_rate_for_expenses(400, 320), 0.2)

    def test_invalid_savings(self):
        with self.assertRaises(ValueError):
            fm.annual_savings(400, 1.5)
        with self.assertRaises(ValueError):
            fm.savings_rate_for_expenses(400, 500)


class TestCompound(unittest.TestCase):
    def test_compound(self):
        rows = sim()
        # 年初 0 → 0×1.1 + 50 = 50 → 50×1.1 + 50 = 105 → 105×1.1 + 50 = 165.5
        self.assertEqual([r["age"] for r in rows], [20, 21, 22])
        for got, want in zip([r["end_assets"] for r in rows], [50, 105, 165.5]):
            self.assertAlmostEqual(got, want)
        self.assertAlmostEqual(rows[2]["investment_return"], 10.5)
        self.assertAlmostEqual(rows[1]["start_assets"], 50)

    def test_closed_form(self):
        # 初期資産 P、毎年末 S を拠出：P(1+r)^n + S((1+r)^n − 1)/r
        P, S, r, n = 1000, 60, 0.05, 30
        rows = fm.simulate_accumulation(30, 30 + n, P, 120, 0.5, r)
        want = P * (1 + r) ** n + S * ((1 + r) ** n - 1) / r
        self.assertAlmostEqual(rows[-1]["end_assets"], want, places=6)

    def test_zero_return(self):
        self.assertAlmostEqual(sim(annual_return=0.0)[-1]["end_assets"], 150)

    def test_zero_initial_assets(self):
        self.assertEqual(sim(initial_assets=0)[0]["start_assets"], 0)

    def test_zero_savings_rate(self):
        rows = sim(initial_assets=100, savings_rate=0.0)
        self.assertAlmostEqual(rows[-1]["end_assets"], 100 * 1.1 ** 3)
        self.assertTrue(all(r["savings"] == 0 for r in rows))

    def test_full_savings_rate(self):
        rows = sim(savings_rate=1.0, annual_return=0.0)
        self.assertAlmostEqual(rows[-1]["end_assets"], 300)
        self.assertEqual(fm.living_expenses(100, 1.0), 0)

    def test_negative_return(self):
        rows = sim(initial_assets=1000, savings_rate=0.0, annual_return=-0.1)
        self.assertAlmostEqual(rows[-1]["end_assets"], 1000 * 0.9 ** 3)
        rows = sim(initial_assets=1000, annual_return=-1.0)        # -100%：資産は失われ、拠出分だけ残る
        self.assertAlmostEqual(rows[0]["end_assets"], 50)

    def test_assets_by_age(self):
        rows = sim()
        ages, assets = fm.assets_by_age(rows)
        self.assertEqual(ages, [20, 21, 22, 23])
        self.assertAlmostEqual(assets[-1], 165.5)
        self.assertAlmostEqual(fm.assets_at(rows, 23), 165.5)
        self.assertAlmostEqual(fm.assets_at(rows, 20), 0)
        with self.assertRaises(ValueError):
            fm.assets_at(rows, 24)

    def test_totals(self):
        rows = sim()
        self.assertAlmostEqual(fm.total_contributions(rows), 150)
        self.assertAlmostEqual(fm.total_investment_return(rows), 15.5)
        self.assertAlmostEqual(fm.total_contributions(rows) + fm.total_investment_return(rows), rows[-1]["end_assets"])


class TestValidation(unittest.TestCase):
    def test_invalid_savings_rate(self):
        for rate in [-0.1, 1.01]:
            with self.assertRaises(ValueError):
                sim(savings_rate=rate)

    def test_invalid_age(self):
        with self.assertRaises(TypeError):
            sim(start_age=20.5)
        with self.assertRaises(TypeError):
            sim(start_age=True)
        with self.assertRaises(ValueError):
            sim(start_age=30, end_age=30)
        with self.assertRaises(ValueError):
            sim(start_age=-1)

    def test_invalid_amounts(self):
        with self.assertRaises(ValueError):
            sim(initial_assets=-1)
        with self.assertRaises(ValueError):
            sim(annual_income=-1)
        with self.assertRaises(ValueError):
            sim(annual_return=-1.01)
        with self.assertRaises(TypeError):
            sim(annual_return="3%")


class TestScenarios(unittest.TestCase):
    def test_load_sample(self):
        with warnings.catch_warnings():
            warnings.simplefilter("error")       # サンプルの生活費は 所得 × (1 − 貯蓄率) と一致している
            scenarios, settings = fm.load_scenarios()
        self.assertEqual([s["name"] for s in scenarios], ["standard", "high_savings", "high_return", "high_income"])
        self.assertEqual(settings["withdrawal_rate"], 0.04)

    def test_with_changes_copies(self):
        scenarios, _ = fm.load_scenarios()
        s = fm.with_changes(scenarios[0], savings_rate=0.5)
        self.assertEqual(s["savings_rate"], 0.5)
        self.assertEqual(scenarios[0]["savings_rate"], 0.2)

    def test_inconsistent_expenses_warns(self):
        scenarios, settings = fm.load_scenarios()
        with self.assertWarns(UserWarning):
            fm.validate_scenario(fm.with_changes(scenarios[0], annual_expenses=250), settings)


if __name__ == "__main__":
    unittest.main()
