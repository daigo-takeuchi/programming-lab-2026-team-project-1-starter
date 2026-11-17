# D3：道路ネットワークのテスト

import copy
import os
import tempfile
import unittest
from pathlib import Path

import road_network as rn

DATA_FILE = Path(__file__).parent.parent / "data" / "sample_tokyo_network.json"


def small_network():
    return {
        "nodes": {"A": {"name": "A", "x": 0, "y": 0}, "B": {"name": "B", "x": 3, "y": 0},
                  "C": {"name": "C", "x": 3, "y": 4}, "Z": {"name": "Z", "x": 9, "y": 9}},
        "roads": [
            {"from": "A", "to": "B", "distance": 3.0, "status": "open", "cost_multiplier": 1.0},
            {"from": "C", "to": "B", "distance": 4.0, "status": "emergency_only", "cost_multiplier": 2.0},
        ],
    }


class TestRoadNetwork(unittest.TestCase):

    def test_load_json(self):
        """1. JSON ファイルを読み込める（ノード 8〜12、すべて道路の距離 ≥ 直線距離）"""
        network = rn.load_network(DATA_FILE)
        self.assertTrue(8 <= len(network["nodes"]) <= 12)
        self.assertEqual(rn.node_name(network, "SJK"), "Shinjuku")
        self.assertEqual(rn.euclidean_lower_bound_violations(network), [])
        self.assertTrue(all(r["cost_multiplier"] >= 1 for r in rn.roads(network)))

    def test_nodes_and_roads(self):
        """2. ノードと道路を取得できる"""
        network = small_network()
        self.assertEqual(rn.node_ids(network), ["A", "B", "C", "Z"])
        self.assertEqual(len(rn.roads(network)), 2)
        self.assertEqual(rn.road_distance(rn.find_road(network, "B", "C")), 4.0)
        self.assertEqual(rn.road_cost(rn.find_road(network, "B", "C")), 8.0)
        self.assertIsNone(rn.find_road(network, "A", "C"))

    def test_adjacency(self):
        """3・4. 隣接リスト：無向道路は両方向に登録、車両ごとに通行できる道路だけ"""
        network = small_network()
        general = rn.adjacency(network, "general")
        self.assertEqual([n for n, _ in general["A"]], ["B"])
        self.assertEqual([n for n, _ in general["B"]], ["A"])          # B–C は緊急車両のみ
        emergency = rn.adjacency(network, "emergency")
        self.assertEqual([n for n, _ in emergency["B"]], ["A", "C"])
        self.assertEqual([n for n, _ in emergency["C"]], ["B"])        # C → B も通れる（双方向）
        self.assertEqual(rn.neighbors(network, "B", "emergency"), ["A", "C"])

    def test_isolated_node_and_no_roads(self):
        """5. 孤立ノードや、道路が1本もないネットワークも扱える"""
        network = small_network()
        rn.validate_network(network)
        self.assertEqual(rn.adjacency(network, "emergency")["Z"], [])
        empty = {"nodes": {"A": {"name": "A", "x": 0, "y": 0}}, "roads": []}
        rn.validate_network(empty)
        self.assertEqual(rn.adjacency(empty, "general"), {"A": []})

    def test_invalid_node_id(self):
        """6. 存在しないノードを端点とする道路・自己ループを拒否する"""
        for change in [{"to": "X"}, {"from": "X"}, {"to": "A"}]:
            network = small_network()
            network["roads"][0].update(change)
            with self.subTest(change=change):
                with self.assertRaises(ValueError):
                    rn.validate_network(network)

    def test_invalid_distance_and_multiplier(self):
        """7. 負・0・無限大・NaN の距離やコスト倍率を拒否する"""
        for key in ("distance", "cost_multiplier"):
            for bad in [-1.0, 0, float("inf"), float("nan"), "3"]:
                network = small_network()
                network["roads"][0][key] = bad
                with self.subTest(key=key, value=bad):
                    with self.assertRaises(ValueError):
                        rn.validate_network(network)

    def test_invalid_status(self):
        """8. 定義されていない通行状態を拒否する"""
        network = small_network()
        network["roads"][0]["status"] = "maybe"
        with self.assertRaises(ValueError):
            rn.validate_network(network)
        with self.assertRaises(ValueError):
            rn.can_pass(network["roads"][0], "bicycle")         # 定義されていない車両

    def test_duplicate_road(self):
        """9. 同じ無向道路の重複を拒否する（向きが逆でも同じ道路）"""
        network = small_network()
        network["roads"].append(dict(network["roads"][0], **{"from": "B", "to": "A"}))
        with self.assertRaises(ValueError):
            rn.validate_network(network)

    def test_duplicate_node_id_in_json(self):
        """JSON のノードIDの重複を検出する"""
        text = ('{"nodes": {"A": {"name": "A", "x": 0, "y": 0}, "A": {"name": "A2", "x": 1, "y": 1}},'
                ' "roads": []}')
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "network.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            with self.assertRaises(ValueError):
                rn.load_network(path)

    def test_can_pass(self):
        """通行状態と車両の組合せ"""
        expected = {("open", "general"): True, ("open", "emergency"): True,
                    ("emergency_only", "general"): False, ("emergency_only", "emergency"): True,
                    ("closed", "general"): False, ("closed", "emergency"): False}
        for (status, vehicle), allowed in expected.items():
            road = dict(copy.deepcopy(small_network()["roads"][0]), status=status)
            self.assertEqual(rn.can_pass(road, vehicle), allowed, (status, vehicle))


if __name__ == "__main__":
    unittest.main()
