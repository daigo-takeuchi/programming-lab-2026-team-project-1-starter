# D1：配置アルゴリズムのテスト

import unittest
from itertools import combinations
from math import comb
from pathlib import Path

import coverage
import placement

DATA_FILE = Path(__file__).parent.parent / "data" / "sample_region.json"
ALGORITHMS = [
    lambda a, t, k: placement.random_placement(a, t, k, seed=0),
    placement.greedy,
    placement.brute_force,
]


class TestPlacement(unittest.TestCase):

    def setUp(self):
        self.region1, self.region2 = coverage.load_scenarios(DATA_FILE)

    def test_random_within_k(self):
        """1. ランダム配置は K 局（以内）を、重複なく選ぶ"""
        a, t = self.region2["areas"], self.region2["towers"]
        for k in range(0, len(t) + 1):
            for seed in range(10):
                selected = placement.random_placement(a, t, k, seed=seed)["selected"]
                self.assertLessEqual(len(selected), k)
                self.assertEqual(len(set(selected)), len(selected))
                self.assertTrue(set(selected) <= set(t))

    def test_random_reproducible(self):
        """2. 同じ乱数シードなら同じ結果"""
        a, t, k = self.region2["areas"], self.region2["towers"], self.region2["k"]
        self.assertEqual(placement.random_placement(a, t, k, seed=7),
                         placement.random_placement(a, t, k, seed=7))
        results = {tuple(placement.random_placement(a, t, k, seed=s)["selected"]) for s in range(20)}
        self.assertGreater(len(results), 1)         # シードが違えば違う配置も出る

    def test_brute_force_optimal(self):
        """3. 全探索は、すべての組合せの中で最大のカバー人口を返す"""
        for s in (self.region1, self.region2):
            a, t, k = s["areas"], s["towers"], s["k"]
            best = max(coverage.covered_population(a, t, c) for c in combinations(sorted(t), k))
            result = placement.brute_force(a, t, k)
            self.assertEqual(result["covered"], best)
            self.assertEqual(result["evaluated"], comb(len(t), k))
        self.assertEqual(placement.brute_force(self.region1["areas"], self.region1["towers"], 2)["selected"],
                         ["T2", "T5"])
        self.assertEqual(placement.brute_force(self.region2["areas"], self.region2["towers"], 2)["selected"],
                         ["T2", "T3"])

    def test_greedy_uses_marginal_gain(self):
        """4. 貪欲法は「総カバー人口」ではなく「追加でカバーできる人口」で選ぶ"""
        areas = {"A": 10, "B": 10, "C": 5}
        towers = {"T1": {"A", "B"}, "T2": {"A", "B"}, "T3": {"C"}}
        # 総カバー人口の順なら T1, T2（20, 20）だが、T2 の増分は 0 なので T3 を選ぶ
        self.assertEqual(placement.greedy(areas, towers, 2)["selected"], ["T1", "T3"])
        # サンプルデータ：Region 2 では T1 の後、増分 900 の T2（T4 と同点、ID の小さい方）
        r2 = placement.greedy(self.region2["areas"], self.region2["towers"], 2)
        self.assertEqual(r2["selected"], ["T1", "T2"])
        self.assertEqual(r2["covered"], 8000)

    def test_greedy_tie_and_stop(self):
        """5. 同点のときは ID の小さい方。増分が 0 になったら K 局未満で止まる"""
        areas = {"A": 5, "B": 5}
        towers = {"T2": {"A"}, "T1": {"B"}, "T3": {"A", "B"}}
        self.assertEqual(placement.greedy(areas, towers, 1)["selected"], ["T3"])
        self.assertEqual(placement.greedy(areas, towers, 3)["selected"], ["T3"])     # その後の増分は 0
        tie = {"T2": {"A"}, "T1": {"B"}}
        self.assertEqual(placement.greedy(areas, tie, 1)["selected"], ["T1"])
        self.assertEqual(placement.greedy(areas, tie, 1), placement.greedy(areas, tie, 1))

    def test_results_consistent(self):
        """6. 3方式の covered・rate は、選んだ基地局から計算した値と一致する"""
        for s in (self.region1, self.region2):
            a, t, k = s["areas"], s["towers"], s["k"]
            for algorithm in ALGORITHMS:
                result = algorithm(a, t, k)
                self.assertEqual(result["covered"], coverage.covered_population(a, t, result["selected"]))
                self.assertAlmostEqual(result["rate"], coverage.coverage_rate(a, t, result["selected"]))

    def test_brute_force_at_least_greedy_and_random(self):
        """7・8. 全探索の結果は、貪欲法・ランダム配置以上"""
        for s in (self.region1, self.region2):
            a, t = s["areas"], s["towers"]
            for k in range(0, len(t) + 1):
                optimum = placement.brute_force(a, t, k)["covered"]
                self.assertGreaterEqual(optimum, placement.greedy(a, t, k)["covered"])
                for seed in range(5):
                    self.assertGreaterEqual(optimum, placement.random_placement(a, t, k, seed=seed)["covered"])

    def test_greedy_optimal_and_suboptimal_examples(self):
        """サンプルの Region 1 では貪欲法が最適、Region 2 では最適でない（近似比 8000/8800）"""
        r1, r2 = self.region1, self.region2
        self.assertEqual(placement.greedy(r1["areas"], r1["towers"], 2)["covered"], 4200)
        self.assertEqual(placement.brute_force(r1["areas"], r1["towers"], 2)["covered"], 4200)
        g = placement.greedy(r2["areas"], r2["towers"], 2)["covered"]
        opt = placement.brute_force(r2["areas"], r2["towers"], 2)["covered"]
        self.assertAlmostEqual(placement.approximation_ratio(g, opt), 8000 / 8800)

    def test_k_zero(self):
        """9. K = 0 なら何も選ばず、カバー人口 0"""
        a, t = self.region1["areas"], self.region1["towers"]
        for algorithm in ALGORITHMS:
            result = algorithm(a, t, 0)
            self.assertEqual(result["selected"], [])
            self.assertEqual(result["covered"], 0)

    def test_k_larger_than_m(self):
        """10. K が候補数 M を超えたら ValueError"""
        a, t = self.region1["areas"], self.region1["towers"]
        for algorithm in ALGORITHMS:
            with self.assertRaises(ValueError):
                algorithm(a, t, len(t) + 1)
            with self.assertRaises(ValueError):
                algorithm(a, t, -1)

    def test_all_population_zero(self):
        """11. 人口がすべて 0 でも安全（近似比は定義できないので None）"""
        areas = {"A": 0, "B": 0, "C": 0}
        towers = {"T1": {"A"}, "T2": {"B", "C"}}
        for algorithm in ALGORITHMS:
            result = algorithm(areas, towers, 1)
            self.assertEqual(result["covered"], 0)
            self.assertEqual(result["rate"], 0.0)
        self.assertEqual(placement.greedy(areas, towers, 2)["selected"], [])
        self.assertIsNone(placement.approximation_ratio(0, 0))


if __name__ == "__main__":
    unittest.main()
