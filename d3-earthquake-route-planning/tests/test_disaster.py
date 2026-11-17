# D3：地震シナリオのテスト

import copy
import unittest
from pathlib import Path

import disaster
from road_network import can_pass, find_road, load_network, road_cost

DATA_FILE = Path(__file__).parent.parent / "data" / "sample_tokyo_network.json"


class TestDisaster(unittest.TestCase):

    def setUp(self):
        self.base = load_network(DATA_FILE)

    def test_apply_closure(self):
        """1. 道路閉鎖シナリオを適用できる"""
        network = disaster.apply_scenario(self.base, "closure")
        for u, v in disaster.SCENARIOS["closure"]["closed"]:
            self.assertEqual(find_road(network, u, v)["status"], "closed")
        self.assertEqual(find_road(network, "SJK", "IKB")["status"], "open")

    def test_original_unchanged(self):
        """2. 元のネットワークは変更されない（コピーは独立している）"""
        backup = copy.deepcopy(self.base)
        for name in disaster.SCENARIOS:
            network = disaster.apply_scenario(self.base, name)
            network["roads"][0]["status"] = "closed"          # コピーを変更しても
        self.assertEqual(self.base, backup)                   # 元は変わらない

    def test_closed_road_blocks_both(self):
        """3. 完全閉鎖の道路は、一般車両も緊急車両も通行できない"""
        network = disaster.apply_scenario(self.base, "closure")
        road = find_road(network, "UEN", "KOT")
        self.assertFalse(can_pass(road, "general"))
        self.assertFalse(can_pass(road, "emergency"))

    def test_emergency_only(self):
        """4・5. 緊急車両専用道路は、一般車両は通行できず、緊急車両は通行できる"""
        network = disaster.apply_scenario(self.base, "regulation")
        road = find_road(network, "IKB", "UEN")
        self.assertEqual(road["status"], "emergency_only")
        self.assertFalse(can_pass(road, "general"))
        self.assertTrue(can_pass(road, "emergency"))

    def test_cost_multiplier(self):
        """6. 移動コスト倍率が正しく適用される（距離は変わらない）"""
        network = disaster.apply_scenario(self.base, "congestion")
        road = find_road(network, "UEN", "KOT")
        self.assertEqual(road["cost_multiplier"], 2.0)
        self.assertAlmostEqual(road_cost(road), 2.0 * find_road(self.base, "UEN", "KOT")["distance"])
        self.assertEqual(road["distance"], find_road(self.base, "UEN", "KOT")["distance"])

    def test_reproducible(self):
        """7. 同じシナリオは何度適用しても同じ結果"""
        for name in disaster.SCENARIOS:
            self.assertEqual(disaster.apply_scenario(self.base, name), disaster.apply_scenario(self.base, name))
        self.assertEqual(disaster.apply_scenario(self.base, "before"), self.base)

    def test_invalid_changes(self):
        """存在しない道路・不正な倍率は例外。閉鎖は規制より優先する"""
        with self.assertRaises(KeyError):
            disaster.apply_changes(self.base, closed=[("SJK", "URY")])
        with self.assertRaises(ValueError):
            disaster.apply_changes(self.base, cost_multipliers={("SJK", "IKB"): 0})
        both = disaster.apply_changes(self.base, closed=[("SJK", "IKB")], emergency_only=[("IKB", "SJK")])
        self.assertEqual(find_road(both, "SJK", "IKB")["status"], "closed")


if __name__ == "__main__":
    unittest.main()
