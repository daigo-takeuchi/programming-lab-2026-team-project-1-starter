# Notebook 用のグラフ（experiments/plots.py）のテスト。matplotlib がない環境ではスキップする
import importlib.util
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from experiments import plots  # noqa: E402
from experiments import compare_algorithms as ca  # noqa: E402

HAS_MPL = importlib.util.find_spec("matplotlib") is not None


class TestPlotsWithoutMatplotlib(unittest.TestCase):
    def test_theory_functions(self):
        self.assertEqual(plots.THEORY["O(N)"](100), 100)
        self.assertAlmostEqual(plots.THEORY["O(log N)"](1024), 10)
        self.assertEqual(plots.algorithm_colors([{"algorithm": "A"}, {"algorithm": "B"}, {"algorithm": "A"}]),
                         {"A": plots.COLORS[0], "B": plots.COLORS[1]})


@unittest.skipUnless(HAS_MPL, "matplotlib がない環境ではスキップ")
class TestPlots(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        import matplotlib
        matplotlib.use("Agg")
        cls.rows = ca.run_comparison(ca.make_search_task(queries=10), sizes=(10, 100), repeat=2, warmup=0)

    def tearDown(self):
        import matplotlib.pyplot as plt
        plt.close("all")

    def test_all_plots(self):
        figs = [plots.plot_time_vs_size(self.rows), plots.plot_bars_by_size(self.rows),
                plots.plot_theory([10, 100, 1000], {"A": "O(N)", "B": "O(log N)"}),
                plots.plot_measured_vs_theory(self.rows, {"A": "O(N)", "B": "O(log N)"}),
                plots.plot_operations(self.rows), plots.plot_repeats(self.rows, 100)]
        self.assertTrue(all(len(f.axes) >= 1 for f in figs))


if __name__ == "__main__":
    unittest.main()
