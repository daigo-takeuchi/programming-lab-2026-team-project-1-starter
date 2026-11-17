# F2：fire_charts.py のテスト（matplotlib がない環境ではスキップ）
#
# 見た目ではなく、「エラーなく描ける」「未達成を年齢の値と混同しない」ことを確かめる。

import importlib.util
import os
import tempfile
import unittest

HAS_MPL = importlib.util.find_spec("matplotlib") is not None

import financial_model as fm
import fire_charts as fc
import optimization as op
import retirement_model as rm


@unittest.skipUnless(HAS_MPL, "matplotlib が必要です")
class TestCharts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        cls.plt = plt
        cls.scenarios, cls.settings = fm.load_scenarios()
        fc.setup_style()

    def tearDown(self):
        self.plt.close("all")

    def test_assets(self):
        rows = fm.accumulate(self.scenarios[0], 80)
        a, v = fm.assets_by_age(rows)
        fig = fc.plot_assets([("x", a, v, fc.color_of("standard"))], "t", target=8000, fire_ages=[69])
        self.assertEqual(list(fig.axes[0].get_lines()[0].get_ydata()), v)

    def test_fire_age_unreached_not_plotted_as_age(self):
        fig = fc.plot_fire_age([0.1, 0.2], [None, 69], "x", "t", end_age=80)
        ax = fig.axes[0]
        reached_line = ax.get_lines()[0]
        self.assertEqual(list(reached_line.get_ydata()), [69])          # 未達成は年齢の線に含めない
        labels = [t.get_text() for t in ax.get_yticklabels()]
        self.assertTrue(any("not reached" in s for s in labels))

    def test_heatmap_marks_na(self):
        matrix = op.grid_fire_age(self.scenarios[0], [0.1, 0.5], [0.0, 0.08], self.settings)
        fig = fc.plot_heatmap(matrix, [0.1, 0.5], [0.0, 0.08])
        texts = [t.get_text() for t in fig.axes[0].texts]
        self.assertIn("N/A", texts)
        self.assertNotIn("0", texts)

    def test_withdrawal_and_tornado(self):
        rows = rm.simulate_withdrawal(50, 100, 5000, 300, 0.03)
        fc.plot_withdrawal([("a", rows, fc.RAMP[2])], "t")
        fc.plot_tornado([{"label": "a", "low": 70, "high": None}, {"label": "b", "low": 60, "high": 75}], 69, "t")
        fc.plot_contributions_vs_gains(["0%", "3%"], [100, 100], [0, 50], "t")

    def test_ramp_and_save(self):
        self.assertEqual(len(fc.ramp(5)), 5)
        self.assertEqual(fc.ramp(1), [fc.RAMP[2]])
        fig = self.plt.figure()
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(os.path.exists(fc.save(fig, os.path.join(d, "f", "x.png"))))


if __name__ == "__main__":
    unittest.main()
