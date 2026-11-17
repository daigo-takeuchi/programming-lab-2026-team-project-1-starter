# Notebook 用のグラフ（growth_charts.py）のテスト。matplotlib がない環境ではスキップする
import importlib.util
import unittest

from tests import _helpers  # noqa: F401
import economic_model as em
import simulation as sim
import allocation_strategies as al
import optimization as op
import growth_charts as gc

HAS_MPL = importlib.util.find_spec("matplotlib") is not None


class TestChartsWithoutMatplotlib(unittest.TestCase):
    def test_import_and_colors(self):
        self.assertEqual(set(gc.SECTOR_COLORS), set(em.SECTORS))
        self.assertEqual(len(gc.ramp(4)), 4)


@unittest.skipUnless(HAS_MPL, "matplotlib がない環境ではスキップ")
class TestCharts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import matplotlib
        matplotlib.use("Agg")
        cls.p = em.load_economy()
        cls.scs = al.load_scenarios()
        cls.runs = sim.run_scenarios(cls.scs, cls.p, 10)
        cls.res = op.compare_algorithms(cls.p, "final_gdp", 0.25, 10)

    def tearDown(self):
        import matplotlib.pyplot as plt
        plt.close("all")

    def test_charts(self):
        figs = [gc.plot_series(self.runs, "gdp", "t"), gc.plot_state_panels(self.runs["equal"]),
                gc.plot_allocation_bars([(sc["id"], sc["shares"]) for sc in self.scs]),
                gc.plot_grouped_bars(["a", "b"], ["x", "y"], {"x": [1, 2], "y": [2, 1]}, "t", "y"),
                gc.plot_algorithm_metric(self.res, "objective", "t", "y"),
                gc.plot_search_path(self.res["greedy"], "t"), gc.plot_search_path(self.res["local_search"], "t"),
                gc.plot_tradeoff_scatter([(1, 2, al.equal_allocation()), (2, 1, al.equal_allocation())], {"a": (1, 2)},
                                         color_by="rd"),
                gc.plot_share_lines([1, 2], [al.equal_allocation(), al.priority_allocation("rd")], "x", "t"),
                gc.plot_heatmap([1, 2], [1, 2], [[0.1, 0.2], [0.3, 0.4]], "x", "y", "t", "v"),
                gc.plot_xy([1, 2], {"a": [1, 2]}, "x", "y", "t")]
        self.assertTrue(all(len(f.axes) >= 1 for f in figs))


if __name__ == "__main__":
    unittest.main()
