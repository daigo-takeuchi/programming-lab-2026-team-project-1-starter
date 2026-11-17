# Notebook 用のグラフ（conflict_charts.py）のテスト。matplotlib がない環境ではスキップする
import importlib.util
import unittest

from tests import _helpers  # noqa: F401
import agents as ag
import game_theory as gt
import simulation as sim
import state_transitions as st
import network_model as nm
import conflict_charts as cc

HAS_MPL = importlib.util.find_spec("matplotlib") is not None


class TestChartsWithoutMatplotlib(unittest.TestCase):
    def test_import_and_layout(self):
        self.assertEqual(set(cc.STATE_COLORS), set(st.STATES))
        self.assertEqual(set(cc.STRATEGY_COLORS), set(ag.STRATEGIES))
        pos = cc.circle_layout(["A", "B", "C"])
        self.assertAlmostEqual(pos["A"][1], 1.0)


@unittest.skipUnless(HAS_MPL, "matplotlib がない環境ではスキップ")
class TestCharts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import matplotlib
        matplotlib.use("Agg")
        cls.cs = ag.load_countries()
        cls.p = sim.load_parameters()
        cls.m = gt.load_payoff_matrix()
        cls.ids = [c["id"] for c in cls.cs]
        cls.edges = nm.make_network("ring", cls.ids)

    def tearDown(self):
        import matplotlib.pyplot as plt
        plt.close("all")

    def test_charts(self):
        tp = self.p["transition"]
        out = sim.simulate(self.cs, self.edges, self.p, self.m, years=10)
        adj = nm.adjacency_list(self.ids, self.edges)
        figs = [cc.plot_payoff_matrix(self.m), cc.plot_transition_matrix(st.transition_matrix("C", "N", 0.5, False, False, tp),
                                                                         st.STATES, "t"),
                cc.plot_transition_diagram(st.transition_matrix("C", "N", 0.5, True, False, tp), st.STATES, "t"),
                cc.plot_state_timeline(out["records"], "t"), cc.plot_lines([1, 2], {"a": [0.1, 0.2]}, "t", "y"),
                cc.plot_hist([0.1, 0.2, 0.3], "t", "x"), cc.plot_running_mean([0.1, 0.3, 0.2], "t", "y"),
                cc.plot_networks([("ring", self.ids, self.edges)], states=[out["records"][-1]["states"]],
                                 highlight=[(self.edges[0],)]),
                cc.plot_search_orders(adj, "A", nm.dfs(adj, "A"), nm.bfs(adj, "A")),
                cc.plot_bar(["a", "b"], [1, 2], "t", "y"), cc.plot_grouped(["g"], ["s1", "s2"], {"s1": [0.2], "s2": [0.4]}, "t", "y"),
                cc.plot_loglog([10, 100], {"DFS": [0.1, 1.0]}, "t", "y")]
        self.assertTrue(all(len(f.axes) >= 1 for f in figs))


if __name__ == "__main__":
    unittest.main()
