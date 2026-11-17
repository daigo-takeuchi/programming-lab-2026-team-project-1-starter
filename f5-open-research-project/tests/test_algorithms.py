# 初期デモ（Algorithm A：線形探索、Algorithm B：二分探索）のテスト
# 研究テーマを変えたら、新しいアルゴリズムのテストをこのファイル（または新しいファイル）に追加すること。
import random
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from algorithms import algorithm_a as alg_a  # noqa: E402
from algorithms import algorithm_b as alg_b  # noqa: E402


class TestAlgorithmA(unittest.TestCase):
    def test_correct_result(self):
        a = [7, 3, 9, 3, 1]
        self.assertEqual(alg_a.linear_search(a, 9), 2)
        self.assertEqual(alg_a.linear_search(a, 3), 1)          # 最初の位置
        self.assertEqual(alg_a.linear_search(a, 4), -1)
        self.assertEqual(alg_a.linear_search(("x", "y"), "y"), 1)

    def test_empty_and_boundaries(self):
        self.assertEqual(alg_a.linear_search([], 1), -1)
        self.assertEqual(alg_a.linear_search([5], 5), 0)
        self.assertEqual(alg_a.linear_search([5], 6), -1)
        a = list(range(10))
        self.assertEqual(alg_a.linear_search(a, 0), 0)           # 先頭
        self.assertEqual(alg_a.linear_search(a, 9), 9)           # 末尾

    def test_invalid_input(self):
        for bad in (None, 123, "abc", {1, 2}):
            with self.assertRaises(TypeError):
                alg_a.linear_search(bad, 1)

    def test_count(self):
        self.assertEqual(alg_a.linear_search_count([4, 5, 6], 6), (2, 3))
        self.assertEqual(alg_a.linear_search_count([4, 5, 6], 7), (-1, 3))   # 最悪：N 回
        self.assertEqual(alg_a.linear_search_count([], 7), (-1, 0))


class TestAlgorithmB(unittest.TestCase):
    def test_correct_result(self):
        a = [1, 3, 3, 3, 7, 9]
        self.assertEqual(alg_b.binary_search(a, 7), 4)
        self.assertEqual(alg_b.binary_search(a, 3), 1)           # 最初の位置
        self.assertEqual(alg_b.binary_search(a, 4), -1)
        self.assertEqual(alg_b.binary_search(a, 0), -1)          # 範囲の外（小さい）
        self.assertEqual(alg_b.binary_search(a, 10), -1)         # 範囲の外（大きい）

    def test_empty_and_boundaries(self):
        self.assertEqual(alg_b.binary_search([], 1), -1)
        self.assertEqual(alg_b.binary_search([5], 5), 0)
        self.assertEqual(alg_b.binary_search([5], 6), -1)
        a = list(range(0, 20, 2))
        self.assertEqual(alg_b.binary_search(a, 0), 0)
        self.assertEqual(alg_b.binary_search(a, 18), 9)
        self.assertEqual(alg_b.binary_search([2, 2, 2, 2], 2), 0)

    def test_invalid_input(self):
        for bad in (None, 123, "abc"):
            with self.assertRaises(TypeError):
                alg_b.binary_search(bad, 1)
        with self.assertRaises(ValueError):
            alg_b.binary_search([3, 1, 2], 1, check_sorted=True)    # 前提（ソート済み）を満たさない
        with self.assertRaises(TypeError):
            alg_b.binary_search([1, 2, 3], None)                    # 大小を比べられない値

    def test_prepare(self):
        a = [5, 1, 4]
        s = alg_b.prepare(a)
        self.assertEqual(s, [1, 4, 5])
        self.assertEqual(a, [5, 1, 4])                              # 元の入力は変えない
        self.assertTrue(alg_b.is_sorted(s))
        self.assertTrue(alg_b.is_sorted([]))
        self.assertFalse(alg_b.is_sorted([2, 1]))

    def test_count_is_logarithmic(self):
        a = list(range(1024))
        _idx, c = alg_b.binary_search_count(a, -5)
        self.assertLessEqual(c, 12)                                 # log2(1024) + 1 回 + 最後の確認
        self.assertEqual(alg_b.binary_search_count(a, 700)[0], 700)


class TestConsistency(unittest.TestCase):
    def test_same_answer_on_random_inputs(self):
        rng = random.Random(1)
        for _ in range(200):
            n = rng.randrange(0, 40)
            a = sorted(rng.randrange(0, 30) for _ in range(n))      # 重複あり
            key = rng.randrange(-2, 32)
            # ソート済みの同じ配列なら、A と B は同じ添字（最初の位置）を返す
            self.assertEqual(alg_a.linear_search(a, key), alg_b.binary_search(a, key))
            # ソート前の配列でも「見つかるか」は一致する
            u = a[:]
            rng.shuffle(u)
            self.assertEqual(alg_a.linear_search(u, key) != -1, alg_b.binary_search(alg_b.prepare(u), key) != -1)

    def test_count_matches_result(self):
        rng = random.Random(2)
        a = sorted(rng.sample(range(1000), 200))
        for key in rng.sample(range(-10, 1010), 50):
            self.assertEqual(alg_a.linear_search_count(a, key)[0], alg_a.linear_search(a, key))
            self.assertEqual(alg_b.binary_search_count(a, key)[0], alg_b.binary_search(a, key))

    def test_metadata(self):
        for m in (alg_a, alg_b):
            for k in ("N", "best", "average", "worst", "space", "preprocess"):
                self.assertIn(k, m.COMPLEXITY)
            self.assertTrue(m.NAME and m.PRECONDITION)


if __name__ == "__main__":
    unittest.main()
