# F1：presentation_charts.py のテスト（matplotlib がない環境ではスキップ）
#
# グラフの見た目ではなく、「エラーなく描ける」「計算結果と同じ値を描いている」ことを確かめる。

import importlib.util
import os
import tempfile
import unittest

HAS_MPL = importlib.util.find_spec("matplotlib") is not None

import income_analysis as ia
import optimization as op
import presentation_charts as pc
import scenarios as sc


@unittest.skipUnless(HAS_MPL, "matplotlib が必要です")
class TestCharts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import matplotlib
        matplotlib.use("Agg")      # 画面のない環境でも描けるようにする
        cls.plt = __import__("matplotlib.pyplot", fromlist=["pyplot"])
        cls.careers, cls.settings = sc.load_scenarios()
        pc.setup_style()

    def tearDown(self):
        self.plt.close("all")

    def test_import_without_matplotlib_use(self):
        # import しただけでは matplotlib を読み込まない設計（関数の中で import）
        self.assertTrue(callable(pc.plot_income_by_age))

    def test_income_by_age_plots_model_values(self):
        fig = pc.plot_income_by_age(self.careers)
        lines = fig.axes[0].get_lines()
        self.assertEqual(len(lines), len(self.careers))
        self.assertEqual(list(lines[0].get_ydata()), sc.incomes(self.careers[0]))

    def test_cumulative_and_gap(self):
        base = self.careers[0]
        pc.plot_cumulative_net(self.careers, baseline=base)
        pc.plot_gap_vs_baseline(self.careers[2], base)

    def test_metric_bars_sorted(self):
        results = [ia.evaluate(s) for s in self.careers]
        fig = pc.plot_metric_bars(results, "npv", "NPV")
        widths = [b.get_width() for b in fig.axes[0].patches]
        self.assertEqual(widths, sorted(widths))           # 下から小さい順（上が 1 位）

    def test_switch_age_search(self):
        jc = next(s for s in self.careers if s["name"] == "job_change")
        rows = op.evaluate_switch_ages(jc, op.switch_age_candidates(jc))
        fig = pc.plot_switch_age_search(rows, op.optimal_switch_ages(rows), stay=ia.evaluate(sc.with_changes(jc, job_change=None)))
        self.assertEqual(len(fig.axes), 2)                  # 生涯所得と NPV を別の図に分ける

    def test_rate_charts_and_tornado(self):
        pc.plot_npv_vs_rate(self.careers, [0.0, 0.01, 0.03, 0.05])
        pc.plot_rank_by_rate(self.careers, [0.0, 0.01, 0.03, 0.05])
        pc.plot_tornado([{"label": "a", "low": 1, "high": 3}, {"label": "b", "low": 0, "high": 5}], 2)

    def test_save(self):
        fig = pc.plot_income_by_age(self.careers)
        with tempfile.TemporaryDirectory() as d:
            path = pc.save(fig, os.path.join(d, "figs", "x.png"))
            self.assertTrue(os.path.getsize(path) > 0)

    def test_colors_fixed(self):
        self.assertEqual(pc.color_of("university"), pc.CAREER_COLORS["university"])
        self.assertEqual(pc.color_of("unknown"), pc.NEUTRAL)


if __name__ == "__main__":
    unittest.main()
