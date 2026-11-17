# D3：経路探索のテスト
#
# euclidean_heuristic は学生の課題なので、未実装の間はその A* のテストをスキップする。

import itertools
import unittest
from pathlib import Path

import disaster
import routing
from road_network import adjacency, can_pass, find_road, load_network, road_cost

DATA_FILE = Path(__file__).parent.parent / "data" / "sample_tokyo_network.json"
SEARCHES = [routing.bfs, routing.dijkstra, routing.a_star]


def all_simple_paths(network, start, goal, vehicle):
    """テスト用：通行できる道路だけを使う単純な経路を、深さ優先ですべて列挙する（小さなネットワーク専用）

    (経路, 移動コスト) を順に返す。Dijkstra 法とは独立した方法で最小コストを確かめるために使う。
    """
    adj = adjacency(network, vehicle)

    def extend(path, cost):
        if path[-1] == goal:
            yield path, cost
            return
        for other, road in adj[path[-1]]:
            if other not in path:
                yield from extend(path + [other], cost + road_cost(road))

    yield from extend([start], 0.0)


class TestRouting(unittest.TestCase):

    def setUp(self):
        self.base = load_network(DATA_FILE)
        self.networks = {name: disaster.apply_scenario(self.base, name) for name in disaster.SCENARIOS}

    def test_bfs_min_hops(self):
        """1. BFS は最小ホップ数の経路を返す"""
        result = routing.bfs(self.base, "SJK", "KOT", "general")
        self.assertEqual(result["path"], ["SJK", "TKY", "KOT"])
        self.assertEqual(result["hops"], 2)
        result = routing.bfs(self.base, "KWS", "URY", "general")
        self.assertEqual(result["hops"], 3)                 # 川崎 → 品川 → 豊洲 → 浦安

    def test_dijkstra_min_cost(self):
        """2. Dijkstra 法は最小移動コストの経路を返す（すべての経路を列挙した結果と一致）"""
        for name, network in self.networks.items():
            for vehicle in ("general", "emergency"):
                best = min(c for _, c in all_simple_paths(network, "SJK", "KOT", vehicle))
                result = routing.dijkstra(network, "SJK", "KOT", vehicle)
                self.assertAlmostEqual(result["cost"], best, msg=(name, vehicle))

    def test_a_star_zero_heuristic(self):
        """3・4. A*（h = 0、許容的）は最小移動コストを返し、Dijkstra 法と一致する"""
        for network in self.networks.values():
            for start, goal in itertools.permutations(network["nodes"], 2):
                for vehicle in ("general", "emergency"):
                    d = routing.dijkstra(network, start, goal, vehicle)
                    a = routing.a_star(network, start, goal, vehicle)
                    self.assertEqual(d["cost"] is None, a["cost"] is None)
                    if d["cost"] is not None:
                        self.assertAlmostEqual(d["cost"], a["cost"])

    def test_a_star_euclidean(self):
        """3・4.（学生の課題）A*（直線距離）も Dijkstra 法と同じ最小移動コストを返す"""
        try:
            routing.euclidean_heuristic(self.base, "SJK", "KOT")
        except NotImplementedError:
            self.skipTest("euclidean_heuristic は未実装")
        for network in self.networks.values():
            for start, goal in itertools.permutations(network["nodes"], 2):
                d = routing.dijkstra(network, start, goal, "emergency")
                a = routing.a_star(network, start, goal, "emergency", heuristic=routing.euclidean_heuristic)
                if d["cost"] is not None:
                    self.assertAlmostEqual(d["cost"], a["cost"])
                    self.assertLessEqual(a["expanded"], d["expanded"])

    def test_bfs_not_cost_optimal(self):
        """5. BFS は最小移動コストを保証しない（地震前の新宿 → 江東）"""
        bfs = routing.bfs(self.base, "SJK", "KOT", "general")
        dij = routing.dijkstra(self.base, "SJK", "KOT", "general")
        self.assertLess(bfs["hops"], dij["hops"])
        self.assertGreater(bfs["cost"], dij["cost"])

    def test_closure_reflected(self):
        """6. 道路閉鎖を反映する（地震前と経路が変わる）"""
        before = routing.dijkstra(self.networks["before"], "SJK", "KOT", "general")
        after = routing.dijkstra(self.networks["closure"], "SJK", "KOT", "general")
        self.assertEqual(before["path"], ["SJK", "IKB", "UEN", "KOT"])
        self.assertEqual(after["path"], ["SJK", "SBY", "SNG", "TYS", "KOT"])
        self.assertGreater(after["cost"], before["cost"])

    def test_vehicle_regulation_reflected(self):
        """7. 車両別の交通規制を反映する（一般車両と緊急車両で経路が変わる）"""
        network = self.networks["regulation"]
        general = routing.dijkstra(network, "SJK", "KOT", "general")
        emergency = routing.dijkstra(network, "SJK", "KOT", "emergency")
        self.assertNotIn(("IKB", "UEN"), list(zip(general["path"], general["path"][1:])))
        self.assertEqual(emergency["path"], ["SJK", "IKB", "UEN", "KOT"])
        self.assertLess(emergency["cost"], general["cost"])

    def test_unreachable(self):
        """8. 到達できない場合は path = None（緊急車両も閉鎖道路は通れない）"""
        cut = disaster.apply_changes(self.base, closed=[("SNG", "KWS")])          # 川崎への唯一の道路
        for search in SEARCHES:
            for vehicle in ("general", "emergency"):
                result = search(cut, "SJK", "KWS", vehicle)
                self.assertIsNone(result["path"])
                self.assertIsNone(result["cost"])
        only_em = disaster.apply_changes(self.base, emergency_only=[("SNG", "KWS")])
        self.assertIsNone(routing.dijkstra(only_em, "SJK", "KWS", "general")["path"])
        self.assertIsNotNone(routing.dijkstra(only_em, "SJK", "KWS", "emergency")["path"])

    def test_same_start_and_goal(self):
        """9. 出発地 = 目的地なら、経路は [出発地]、コスト 0、展開 0"""
        for search in SEARCHES:
            result = search(self.base, "TKY", "TKY", "general")
            self.assertEqual(result["path"], ["TKY"])
            self.assertEqual((result["hops"], result["cost"], result["expanded"]), (0, 0, 0))

    def test_isolated_node(self):
        """10. 孤立ノードへは到達できず、孤立ノードからも出発できない"""
        network = {"nodes": {**self.base["nodes"], "ISO": {"name": "Island", "x": 20, "y": 20}},
                   "roads": self.base["roads"]}
        for search in SEARCHES:
            self.assertIsNone(search(network, "SJK", "ISO", "emergency")["path"])
            self.assertIsNone(search(network, "ISO", "SJK", "emergency")["path"])
        with self.assertRaises(ValueError):
            routing.bfs(network, "SJK", "NOWHERE", "general")

    def test_no_closed_roads_in_path(self):
        """11. 経路に、その車両が通行できない道路が含まれない"""
        for network in self.networks.values():
            for start, goal in itertools.permutations(network["nodes"], 2):
                for vehicle in ("general", "emergency"):
                    for search in SEARCHES:
                        path = search(network, start, goal, vehicle)["path"]
                        if path is not None:
                            for u, v in zip(path, path[1:]):
                                self.assertTrue(can_pass(find_road(network, u, v), vehicle))

    def test_expanded_recorded(self):
        """12. 展開ノード数を記録する（0 以上、ノード数以下）"""
        for search in SEARCHES:
            result = search(self.base, "SJK", "URY", "general")
            self.assertGreater(result["expanded"], 0)
            self.assertLessEqual(result["expanded"], len(self.base["nodes"]))


if __name__ == "__main__":
    unittest.main()
