# Notebook 用のグラフ（partnership_charts.py）のテスト。matplotlib がない環境ではスキップする
import importlib.util
import unittest

from tests import _helpers  # noqa: F401
import partners as pt
import decision_strategies as ds
import relationship_dynamics as rd
import evaluation as ev
import partnership_charts as pc

HAS_MPL = importlib.util.find_spec("matplotlib") is not None


class TestChartsWithoutMatplotlib(unittest.TestCase):
    def test_import_and_colors(self):
        # matplotlib がなくても import できる（Core は標準ライブラリだけで動く）
        self.assertEqual(set(pc.STRATEGY_COLORS), set(ds.STRATEGIES))
        self.assertEqual(len(pc.ramp(4)), 4)


@unittest.skipUnless(HAS_MPL, "matplotlib がない環境ではスキップ")
class TestCharts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import matplotlib
        matplotlib.use("Agg")
        cls.plt = __import__("matplotlib.pyplot", fromlist=["pyplot"])
        cls.sc = pt.scenario_by_id(pt.load_scenarios(), "A")
        cls.params = rd.load_parameters()
        cls.events = pt.load_stress_events()["combined"]
        cls.res = ev.compare_strategies(cls.sc, cls.params, cls.events, ds.STRATEGIES, 20, (0,))

    def tearDown(self):
        self.plt.close("all")

    def test_strategy_charts(self):
        for fig in (pc.plot_strategy_metrics(self.res, [("mean_satisfaction", "mean")], "t"),
                    pc.plot_checkpoints(self.res, "t"), pc.plot_short_vs_long(self.res, "t"),
                    pc.plot_survival({s: self.res[s]["survival"] for s in ds.STRATEGIES}, "t",
                                     theory={s: self.res[s]["theoretical_survival"] for s in ds.STRATEGIES})):
            self.assertEqual(len(fig.axes) >= 1, True)

    def test_timeseries_charts(self):
        trajs = {s: self.res[s]["trajectory"] for s in ds.STRATEGIES}
        pc.plot_strategy_paths(trajs, "housework_share", "x", "t", [5, 8])
        pc.plot_yearly(trajs, "dissolution_probability", "p", "t", [5, 8])
        pc.plot_satisfaction_timeseries(trajs["adaptive"], "t", [5, 8])
        out = rd.monte_carlo(self.sc, "fixed", self.params, self.events, 50)
        pc.plot_duration_hist(out["outcomes"], 20, "t")

    def test_allocation_charts(self, ):
        rows = [{"name": "50:50", "A": 15, "B": 15, "limit_A": 22, "limit_B": 15}]
        pc.plot_hours_bars(rows)
        pc.plot_money_bars([{"name": "50:50", "A": 180, "B": 180}])
        pc.plot_share_comparison([{"name": "A", "income": 0.4, "work": 0.44, "housework": 0.5, "financial": 0.5}])
        pc.plot_partner_bars([{"name": "r", "A": 0.6, "B": 0.5}])
        pc.plot_share_sweep([0, 0.5, 1], [0.2, 0.6, 0.3], [0.5, 0.5, 0.1], "x", "t", {"50:50": 0.5})
        pc.plot_heatmap([0, 0.5, 1], [0, 1], [[0.5, None, 0.7], [0.6, 0.8, None]], "t", "v", {"p": (0.5, 0.0)})
        rows = [{"name": "c", **self.res}]
        pc.plot_condition_bars(rows, "continuation_10", "t", "y")


if __name__ == "__main__":
    unittest.main()
