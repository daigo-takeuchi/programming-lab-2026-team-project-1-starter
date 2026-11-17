# D2：ランダム探索・最近傍法・全探索のテスト

import unittest
from itertools import permutations
from pathlib import Path

import solvers
from distance import distance, route_distance
from locations import delivery_ids, load_scenarios

DATA_FILE = Path(__file__).parent.parent / "data" / "sample_deliveries.json"


class TestSolvers(unittest.TestCase):

    def setUp(self):
        self.town1, self.town2 = load_scenarios(DATA_FILE)

    def assert_valid_route(self, scenario, route):
        """8. すべての配送先を1回ずつ訪問する（配送拠点は含まない）"""
        self.assertEqual(sorted(route), delivery_ids(scenario["locations"], scenario["depot"]))

    def test_random_valid(self):
        """1. ランダム探索は有効なルートを返し、試行回数を記録する"""
        for s in (self.town1, self.town2):
            result = solvers.random_search(s["locations"], s["depot"], 30, seed=1)
            self.assert_valid_route(s, result["route"])
            self.assertEqual(result["evaluated"], 30)
            self.assertAlmostEqual(result["distance"], route_distance(s["locations"], s["depot"], result["route"]))
        with self.assertRaises(ValueError):
            solvers.random_search(self.town1["locations"], "Depot", 0)

    def test_random_reproducible(self):
        """2. 同じ乱数シードなら同じ結果"""
        locs = self.town2["locations"]
        self.assertEqual(solvers.random_search(locs, "Depot", 10, seed=5),
                         solvers.random_search(locs, "Depot", 10, seed=5))

    def test_nearest_neighbor_valid(self):
        """3. 最近傍法は有効なルートを返す"""
        for s in (self.town1, self.town2):
            self.assert_valid_route(s, solvers.nearest_neighbor(s["locations"], s["depot"])["route"])

    def test_nearest_neighbor_chooses_closest(self):
        """4. 最近傍法は、毎回いちばん近い未訪問の配送先を選ぶ（同じ距離なら ID の小さい方）"""
        for s in (self.town1, self.town2):
            locs, depot = s["locations"], s["depot"]
            route = solvers.nearest_neighbor(locs, depot)["route"]
            current, unvisited = depot, set(route)
            for chosen in route:
                closest = min(distance(locs, current, x) for x in unvisited)
                self.assertAlmostEqual(distance(locs, current, chosen), closest)
                unvisited.remove(chosen)
                current = chosen
        tie = {"Depot": (0, 0), "B": (1, 0), "A": (-1, 0)}
        self.assertEqual(solvers.nearest_neighbor(tie, "Depot")["route"], ["A", "B"])

    def test_brute_force_optimal(self):
        """5. 全探索は、すべての訪問順の中で最短の距離を返す"""
        for s in (self.town1, self.town2):
            locs, depot = s["locations"], s["depot"]
            ids = delivery_ids(locs, depot)
            best = min(route_distance(locs, depot, p) for p in permutations(ids))
            result = solvers.brute_force(locs, depot)
            self.assertAlmostEqual(result["distance"], best)
            self.assert_valid_route(s, result["route"])

    def test_brute_force_at_least_as_good(self):
        """6・7. 全探索の距離は、ランダム探索・最近傍法以下"""
        for s in (self.town1, self.town2):
            locs, depot = s["locations"], s["depot"]
            optimum = solvers.brute_force(locs, depot)["distance"]
            self.assertLessEqual(optimum, solvers.nearest_neighbor(locs, depot)["distance"] + 1e-9)
            for seed in range(5):
                self.assertLessEqual(optimum, solvers.random_search(locs, depot, 20, seed=seed)["distance"] + 1e-9)

    def test_sample_scenarios(self):
        """Town 1 では最近傍法が最適、Town 2 では最適でない（約 25% 長い）"""
        t1, t2 = self.town1, self.town2
        self.assertAlmostEqual(solvers.nearest_neighbor(t1["locations"], "Depot")["distance"],
                               solvers.brute_force(t1["locations"], "Depot")["distance"])
        nn = solvers.nearest_neighbor(t2["locations"], "Depot")["distance"]
        opt = solvers.brute_force(t2["locations"], "Depot")["distance"]
        self.assertGreater(solvers.optimality_gap(nn, opt), 20)

    def test_single_delivery(self):
        """9. 配送先が1件なら、その1件を往復する"""
        locs = {"Depot": (0, 0), "A": (3, 4)}
        for result in [solvers.random_search(locs, "Depot", 3, seed=0),
                       solvers.nearest_neighbor(locs, "Depot"),
                       solvers.brute_force(locs, "Depot")]:
            self.assertEqual(result["route"], ["A"])
            self.assertAlmostEqual(result["distance"], 10.0)

    def test_no_deliveries(self):
        """配送先が0件でも安全（距離 0、最適解との差は定義できないので None）"""
        locs = {"Depot": (0, 0)}
        for result in [solvers.random_search(locs, "Depot", 3, seed=0),
                       solvers.nearest_neighbor(locs, "Depot"),
                       solvers.brute_force(locs, "Depot")]:
            self.assertEqual(result["route"], [])
            self.assertEqual(result["distance"], 0.0)
        self.assertIsNone(solvers.optimality_gap(0.0, 0.0))

    def test_brute_force_limit(self):
        """10. 配送先数が全探索の上限を超えたら ValueError"""
        locs = {"Depot": (0, 0)}
        locs.update({f"L{i}": (i, i * i) for i in range(1, solvers.MAX_BRUTE_FORCE + 2)})
        with self.assertRaises(ValueError):
            solvers.brute_force(locs, "Depot")
        small = {"Depot": (0, 0), "A": (1, 0), "B": (0, 1), "C": (1, 1)}
        with self.assertRaises(ValueError):
            solvers.brute_force(small, "Depot", max_deliveries=2)

    def test_optimality_gap(self):
        """最適解との差（%）"""
        self.assertAlmostEqual(solvers.optimality_gap(12.5, 10.0), 25.0)
        self.assertEqual(solvers.optimality_gap(10.0, 10.0), 0.0)


if __name__ == "__main__":
    unittest.main()
