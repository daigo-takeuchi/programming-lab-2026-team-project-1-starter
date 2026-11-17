# D1：カバー人口の計算のテスト

import json
import os
import tempfile
import unittest
from pathlib import Path

import coverage

DATA_FILE = Path(__file__).parent.parent / "data" / "sample_region.json"

AREAS = {"A": 1200, "B": 800, "C": 1500, "D": 600, "E": 1000, "F": 900}
TOWERS = {"T1": {"A", "B"}, "T2": {"B", "C"}, "T3": {"C", "D"}, "T4": {"D", "E"}, "T5": {"E", "F"}}


class TestCoverage(unittest.TestCase):

    def test_union(self):
        """1. カバーエリアの和集合"""
        self.assertEqual(coverage.covered_areas(TOWERS, ["T1", "T3"]), {"A", "B", "C", "D"})
        self.assertEqual(coverage.covered_areas(TOWERS, ["T1", "T2"]), {"A", "B", "C"})

    def test_no_double_count(self):
        """2. 重複してカバーされたエリアの人口を二重に数えない"""
        # T1 と T2 は B を重複してカバー：1200 + 800 + 1500 = 3500（800 を2回数えない）
        self.assertEqual(coverage.covered_population(AREAS, TOWERS, ["T1", "T2"]), 3500)

    def test_covered_population(self):
        """3. カバー人口"""
        self.assertEqual(coverage.covered_population(AREAS, TOWERS, ["T2", "T5"]), 4200)
        self.assertEqual(coverage.covered_population(AREAS, TOWERS, list(TOWERS)), 6000)

    def test_coverage_rate(self):
        """4. 人口カバー率"""
        self.assertAlmostEqual(coverage.coverage_rate(AREAS, TOWERS, ["T2", "T5"]), 0.7)
        self.assertAlmostEqual(coverage.coverage_rate(AREAS, TOWERS, list(TOWERS)), 1.0)

    def test_no_selection(self):
        """5. 基地局を選ばない場合は 0"""
        self.assertEqual(coverage.covered_areas(TOWERS, []), set())
        self.assertEqual(coverage.covered_population(AREAS, TOWERS, []), 0)
        self.assertEqual(coverage.coverage_rate(AREAS, TOWERS, []), 0.0)

    def test_zero_total_population(self):
        """6. 総人口が 0 でも安全（カバー率は 0.0）"""
        areas = {"A": 0, "B": 0}
        towers = {"T1": {"A", "B"}}
        self.assertEqual(coverage.total_population(areas), 0)
        self.assertEqual(coverage.coverage_rate(areas, towers, ["T1"]), 0.0)

    def test_unknown_or_duplicate_tower(self):
        """7. 存在しない基地局ID・同じ基地局の重複選択は ValueError"""
        with self.assertRaises(ValueError):
            coverage.covered_population(AREAS, TOWERS, ["T9"])
        with self.assertRaises(ValueError):
            coverage.covered_population(AREAS, TOWERS, ["T1", "T1"])

    def test_invalid_region(self):
        """8. 不正な人口・未定義のエリアを拒否する"""
        for bad in [{"A": -1}, {"A": 1.5}, {"A": "100"}]:
            with self.assertRaises(ValueError):
                coverage.validate_region(bad, {})
        with self.assertRaises(ValueError):
            coverage.validate_region({"A": 1}, {"T1": {"A", "Z"}})

    def test_check_k(self):
        """K は 0 以上の整数で、候補数以下"""
        coverage.check_k(0, TOWERS)
        coverage.check_k(5, TOWERS)
        for bad in [-1, 6, 1.0, True]:
            with self.assertRaises(ValueError):
                coverage.check_k(bad, TOWERS)

    def test_load_scenarios(self):
        """サンプルデータを読み込める（エリア 6〜10、候補 5〜8、K 2〜3）"""
        scenarios = coverage.load_scenarios(DATA_FILE)
        self.assertEqual(len(scenarios), 2)
        for s in scenarios:
            self.assertTrue(6 <= len(s["areas"]) <= 10)
            self.assertTrue(5 <= len(s["towers"]) <= 8)
            self.assertTrue(2 <= s["k"] <= 3)
            self.assertIsInstance(s["towers"]["T1"], set)

    def test_duplicate_tower_id_in_json(self):
        """JSON の基地局IDの重複を検出する"""
        text = ('{"scenarios": [{"name": "x", "description": "", "k": 1, "areas": {"A": 1},'
                ' "towers": {"T1": ["A"], "T1": ["A"]}}]}')
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "region.json")
            with open(path, "w", encoding="utf-8") as f:
                f.write(text)
            with self.assertRaises(ValueError):
                coverage.load_scenarios(path)
            json.loads(text)        # 標準の json.loads では、黙って上書きされてしまう


if __name__ == "__main__":
    unittest.main()
