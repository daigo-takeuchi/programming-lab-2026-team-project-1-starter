# F3：matching_charts.py のテスト（matplotlib がない環境ではスキップ）

import importlib.util
import os
import tempfile
import unittest

HAS_MPL = importlib.util.find_spec("matplotlib") is not None

import evaluation as ev
import matching_algorithms as ma
import matching_charts as mc
import participants as pt
import preferences as pr
import relationship_stability as rs


@unittest.skipUnless(HAS_MPL, "matplotlib が必要です")
class TestCharts(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import matplotlib
        matplotlib.use("Agg")
        import matplotlib.pyplot as plt
        cls.plt = plt
        mc.setup_style()
        cls.g = pt.load_participants()
        cls.s = pr.score_table(cls.g)
        cls.r = pr.build_rankings(cls.g, cls.s)
        cls.a = [p["id"] for p in cls.g["A"]]
        cls.b = [p["id"] for p in cls.g["B"]]
        cls.params = rs.load_parameters()

    def tearDown(self):
        self.plt.close("all")

    def test_heatmap_and_matching(self):
        vals = {(a, b): pr.pair_compatibility(a, b, self.s) for a in self.a for b in self.b}
        fig = mc.plot_score_heatmap(self.a, self.b, vals, self.r, "t")
        self.assertEqual(len(fig.axes[0].texts), 25)
        m = ma.greedy_matching(self.r, self.a, self.b)
        mc.plot_matching(self.a, self.b, m, "t", ev.blocking_pairs(m, self.r, self.a, self.b))
        _m, steps = ma.gale_shapley(self.r, self.a, self.b, record=True)
        fig = mc.plot_gs_steps(steps, self.a, self.b)
        self.assertGreaterEqual(len(fig.axes), len(steps))

    def test_comparison_charts(self):
        res = ev.compare_algorithms(self.g, self.r, self.s, self.params, range(2), 10)
        mc.plot_metric_bars(res, "matching_rate", "t", "rate", err_key="matching_rate_seed_sd")
        mc.plot_grouped(res, [("matching_rate", "x"), ("long_term_10y", "y")], "t")
        fig = mc.plot_survival({mc.ALG_LABELS[k]: v["survival_curve"] for k, v in res.items()}, "t")
        self.assertEqual(len(fig.axes[0].get_lines()[0].get_ydata()), self.params["simulation_years"] + 1)
        mc.plot_trials({"random": [0.1, 0.2], "greedy": [0.3]}, "t", "y")
        mc.plot_sensitivity([0.0, 0.04], {"greedy": [0.4, 0.6], "gale_shapley": [0.4, 0.62]}, "x", "t")

    def test_duration_and_save(self):
        pairs = [{"pair_id": "A1-B1", "participant_ids": ["A1", "B1"], "algorithm": "t",
                  "initial_compatibility": 0.7, "initial_satisfaction": None}]
        recs = [r for run in rs.monte_carlo(pairs, self.params, 50) for r in run]
        fig = mc.plot_duration_hist(recs, 20, "t")
        with tempfile.TemporaryDirectory() as d:
            self.assertTrue(os.path.exists(mc.save(fig, os.path.join(d, "f", "x.png"))))

    def test_ramp(self):
        self.assertEqual(len(mc.ramp(4)), 4)


if __name__ == "__main__":
    unittest.main()
