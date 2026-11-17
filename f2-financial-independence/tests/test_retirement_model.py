# F2：retirement_model.py のテスト

import unittest

import retirement_model as rm


class TestWithdrawal(unittest.TestCase):
    def test_withdrawal_and_return(self):
        rows = rm.simulate_withdrawal(60, 62, 1000, 100, 0.05)
        # 60 歳：収益 50、取り崩し 100、年末 950。61 歳：収益 47.5、年末 897.5
        self.assertAlmostEqual(rows[0]["investment_return"], 50)
        self.assertAlmostEqual(rows[0]["withdrawal"], 100)
        self.assertAlmostEqual(rows[0]["end_assets"], 950)
        self.assertAlmostEqual(rows[1]["investment_return"], 47.5)
        self.assertAlmostEqual(rows[1]["end_assets"], 897.5)
        self.assertIsNone(rm.depletion_age(rows))
        self.assertTrue(rm.is_sustainable(rows))

    def test_depletion_age(self):
        rows = rm.simulate_withdrawal(60, 70, 250, 100, 0.0)
        # 60 歳 150、61 歳 50、62 歳：50 しかないので 50 だけ取り崩して 0 → 枯渇
        self.assertEqual(rm.depletion_age(rows), 62)
        self.assertAlmostEqual(rows[2]["withdrawal"], 50)
        self.assertAlmostEqual(rows[2]["shortfall"], 50)
        self.assertEqual(rm.years_sustained(rows), 2)
        self.assertFalse(rm.is_sustainable(rows))
        self.assertAlmostEqual(rm.total_shortfall(rows), 50 + 100 * 7)

    def test_exact_depletion_counts_as_covered(self):
        rows = rm.simulate_withdrawal(60, 63, 200, 100, 0.0)
        self.assertEqual(rm.depletion_age(rows), 61)       # 61 歳の年末にちょうど 0
        self.assertEqual(rm.years_sustained(rows), 2)      # 60・61 歳は全額まかなえた

    def test_never_negative(self):
        rows = rm.simulate_withdrawal(50, 100, 1000, 300, 0.02)
        self.assertTrue(all(r["end_assets"] >= 0 and r["start_assets"] >= 0 for r in rows))
        self.assertTrue(all(r["end_assets"] == 0 for r in rows if r["age"] > rm.depletion_age(rows)))

    def test_zero_expenses(self):
        rows = rm.simulate_withdrawal(60, 65, 1000, 0, 0.0)
        self.assertIsNone(rm.depletion_age(rows))
        self.assertAlmostEqual(rows[-1]["end_assets"], 1000)
        rows = rm.simulate_withdrawal(60, 65, 0, 0, 0.0)     # 資産 0・生活費 0 は「枯渇」ではない
        self.assertIsNone(rm.depletion_age(rows))

    def test_four_percent_with_three_percent_return_depletes(self):
        # 目標資産に到達しても（7500 = 300 / 4%）、収益率 3% なら資産はいずれ尽きる（RQ5）
        rows = rm.simulate_withdrawal(50, 100, 7500, 300, 0.03)
        self.assertIsNotNone(rm.depletion_age(rows))
        rows = rm.simulate_withdrawal(50, 100, 7500, 300, 0.04)   # 収益率 = 取り崩し率なら資産は一定
        self.assertIsNone(rm.depletion_age(rows))
        self.assertAlmostEqual(rows[-1]["end_assets"], 7500)

    def test_invalid(self):
        with self.assertRaises(ValueError):
            rm.simulate_withdrawal(60, 60, 100, 10, 0.0)
        with self.assertRaises(ValueError):
            rm.simulate_withdrawal(60, 70, -1, 10, 0.0)
        with self.assertRaises(ValueError):
            rm.simulate_withdrawal(60, 70, 100, 10, -2)


if __name__ == "__main__":
    unittest.main()
