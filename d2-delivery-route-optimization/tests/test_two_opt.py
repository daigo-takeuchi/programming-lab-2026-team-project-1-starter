# D2：2-opt のテスト
#
# 部分反転（reverse_segment）のテストは常に実行する。
# two_opt() のテストは、学生が実装するまでスキップされる（通常のテストは失敗しない）。

import unittest
from pathlib import Path

import solvers
from distance import route_distance
from locations import delivery_ids, load_scenarios
from two_opt import reverse_segment, two_opt

DATA_FILE = Path(__file__).parent.parent / "data" / "sample_deliveries.json"


class TestReverseSegment(unittest.TestCase):

    def test_reverse(self):
        """1. 部分反転が正しい"""
        route = ["A", "B", "C", "D", "E"]
        self.assertEqual(reverse_segment(route, 1, 2), ["A", "C", "B", "D", "E"])
        self.assertEqual(reverse_segment(route, 1, 3), ["A", "D", "C", "B", "E"])
        self.assertEqual(reverse_segment(route, 0, 4), ["E", "D", "C", "B", "A"])
        self.assertEqual(reverse_segment(route, 2, 2), route)          # 1要素だけなら変わらない
        self.assertEqual(route, ["A", "B", "C", "D", "E"])               # 元のリストは変更しない

    def test_same_set_no_duplicates(self):
        """2・3. 反転後も配送先の集合は変わらず、重複もない"""
        route = ["A", "B", "C", "D", "E", "F"]
        for i in range(len(route)):
            for j in range(i, len(route)):
                new = reverse_segment(route, i, j)
                self.assertEqual(sorted(new), sorted(route))
                self.assertEqual(len(set(new)), len(new))

    def test_invalid_range(self):
        """範囲外・i > j は ValueError"""
        for i, j in [(-1, 2), (2, 1), (0, 5)]:
            with self.assertRaises(ValueError):
                reverse_segment(["A", "B", "C", "D", "E"], i, j)

    def test_reverse_can_shorten_route(self):
        """交差しているルートは、部分反転で短くなる（2-opt の基本原理）"""
        locs = {"Depot": (0, 0), "A": (0, 2), "B": (2, 0), "C": (2, 2)}
        crossed = ["A", "B", "C"]           # Depot→A→B→C→Depot は A–B と C–Depot が交差
        fixed = reverse_segment(crossed, 1, 2)
        self.assertEqual(fixed, ["A", "C", "B"])
        self.assertLess(route_distance(locs, "Depot", fixed), route_distance(locs, "Depot", crossed))


class TestTwoOpt(unittest.TestCase):
    """4. two_opt() を実装したら実行されるテスト（未実装の間はスキップ）"""

    def setUp(self):
        self.scenarios = load_scenarios(DATA_FILE)
        try:
            two_opt(["A"], {"Depot": (0, 0), "A": (1, 1)}, "Depot")
        except NotImplementedError:
            self.skipTest("two_opt は未実装")

    def test_improves_and_stays_valid(self):
        """改善後も正しいルートで、距離は初期ルート以下、最適解以上"""
        for s in self.scenarios:
            locs, depot = s["locations"], s["depot"]
            optimum = solvers.brute_force(locs, depot)["distance"]
            for initial in [solvers.nearest_neighbor(locs, depot)["route"],
                            solvers.random_search(locs, depot, 1, seed=3)["route"]]:
                result = two_opt(initial, locs, depot)
                self.assertEqual(sorted(result["route"]), delivery_ids(locs, depot))
                self.assertLessEqual(result["distance"], route_distance(locs, depot, initial) + 1e-9)
                self.assertGreaterEqual(result["distance"], optimum - 1e-9)
                self.assertAlmostEqual(result["distance"], route_distance(locs, depot, result["route"]))

    # TODO：2-opt を実装したら、次のようなテストも追加してみよう
    #   - 交差のあるルートを入力すると、交差のないルートが返る
    #   - 2-opt の結果からは、どの (i, j) で反転しても短くならない（局所最適）


if __name__ == "__main__":
    unittest.main()
