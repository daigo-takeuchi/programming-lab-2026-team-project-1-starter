# D2：距離計算と入力検証のテスト

import math
import os
import tempfile
import unittest
from pathlib import Path

from distance import check_route, distance, route_distance
from locations import delivery_ids, load_scenarios, validate_locations

DATA_FILE = Path(__file__).parent.parent / "data" / "sample_deliveries.json"
LOCS = {"Depot": (0, 0), "A": (3, 4), "B": (3, 0), "C": (0, 4)}


class TestDistance(unittest.TestCase):

    def test_two_points(self):
        """1. 2地点間のユークリッド距離"""
        self.assertAlmostEqual(distance(LOCS, "Depot", "A"), 5.0)
        self.assertAlmostEqual(distance(LOCS, "B", "C"), 5.0)
        self.assertAlmostEqual(distance(LOCS, "A", "B"), 4.0)

    def test_same_point(self):
        """2. 同じ地点間の距離は 0"""
        for location_id in LOCS:
            self.assertEqual(distance(LOCS, location_id, location_id), 0.0)

    def test_symmetric(self):
        """3. 距離は対称"""
        for a in LOCS:
            for b in LOCS:
                self.assertEqual(distance(LOCS, a, b), distance(LOCS, b, a))

    def test_route_distance(self):
        """4・5. ルートの総距離（配送拠点への帰着を含む）"""
        # Depot → B → A → C → Depot = 3 + 4 + 3 + 4 = 14
        self.assertAlmostEqual(route_distance(LOCS, "Depot", ["B", "A", "C"]), 14.0)
        # Depot → A → B → C → Depot = 5 + 4 + 5 + 4 = 18（最後の C → Depot の 4 を含む）
        self.assertAlmostEqual(route_distance(LOCS, "Depot", ["A", "B", "C"]), 18.0)

    def test_no_deliveries(self):
        """6. 配送先が0件なら総距離 0"""
        self.assertEqual(route_distance({"Depot": (5, 5)}, "Depot", []), 0.0)
        self.assertEqual(delivery_ids({"Depot": (5, 5)}, "Depot"), [])

    def test_invalid_ids(self):
        """7. 存在しない地点ID・重複・不足・配送拠点を含むルートは ValueError"""
        with self.assertRaises(ValueError):
            distance(LOCS, "A", "Z")
        for bad in [["A", "B", "Z"], ["A", "B", "B"], ["A", "B"], ["Depot", "A", "B", "C"], ["A", "B", "C", "A"]]:
            with self.subTest(route=bad):
                with self.assertRaises(ValueError):
                    route_distance(LOCS, "Depot", bad)
        check_route(LOCS, "Depot", ["C", "A", "B"])     # 正しいルートは例外にならない


class TestLocations(unittest.TestCase):

    def test_validate(self):
        """配送拠点の存在、座標が有限の数値であること"""
        validate_locations(LOCS, "Depot")
        bad_cases = [
            ({"A": (1, 2)}, "Depot"),                       # 配送拠点がない
            ({"Depot": (0, 0), "A": (1,)}, "Depot"),        # 座標が2つでない
            ({"Depot": (0, 0), "A": ("1", 2)}, "Depot"),    # 数値でない
            ({"Depot": (0, 0), "A": (True, 2)}, "Depot"),   # bool は数値として扱わない
            ({"Depot": (0, 0), "A": (math.nan, 2)}, "Depot"),
            ({"Depot": (0, 0), "A": (math.inf, 2)}, "Depot"),
        ]
        for locations, depot in bad_cases:
            with self.subTest(locations=locations):
                with self.assertRaises(ValueError):
                    validate_locations(locations, depot)

    def test_load_sample(self):
        """サンプルデータ：配送拠点1か所、配送先 5〜8 か所"""
        for scenario in load_scenarios(DATA_FILE):
            n = len(delivery_ids(scenario["locations"], scenario["depot"]))
            self.assertTrue(5 <= n <= 8)
            self.assertIn(scenario["depot"], scenario["locations"])

    def test_duplicate_ids_in_json(self):
        """JSON の地点IDの重複を検出する"""
        text = ('{"scenarios": [{"name": "x", "description": "", "depot": "Depot",'
                ' "locations": {"Depot": [0, 0], "A": [1, 1], "A": [2, 2]}}]}')
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "deliveries.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            with self.assertRaises(ValueError):
                load_scenarios(path)


if __name__ == "__main__":
    unittest.main()
