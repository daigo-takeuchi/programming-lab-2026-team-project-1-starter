# E2：algorithm_benchmark.py のテスト（教科書の探索・ソートを import して使う）

import inspect
import unittest

import numpy as np

import algorithm_benchmark as ab


class TestLinearSearch(unittest.TestCase):
    def test_found_first_occurrence(self):
        self.assertEqual(ab.linear_search([5, 3, 7, 3], 3), 1)   # 先頭から探すので最初の位置

    def test_not_found(self):
        self.assertEqual(ab.linear_search([5, 3, 7], 4), -1)

    def test_empty(self):
        self.assertEqual(ab.linear_search([], 1), -1)

    def test_unsorted_ok(self):
        self.assertEqual(ab.linear_search([9, 1, 8], 8), 2)


class TestBinarySearch(unittest.TestCase):
    def test_found(self):
        a = [1, 3, 5, 7, 9, 11]
        for i, v in enumerate(a):
            self.assertEqual(ab.binary_search(a, v), i)

    def test_not_found(self):
        self.assertEqual(ab.binary_search([1, 3, 5], 4), -1)
        self.assertEqual(ab.binary_search([1, 3, 5], 0), -1)
        self.assertEqual(ab.binary_search([1, 3, 5], 9), -1)

    def test_empty(self):
        self.assertEqual(ab.binary_search([], 1), -1)

    def test_single(self):
        self.assertEqual(ab.binary_search([4], 4), 0)
        self.assertEqual(ab.binary_search([4], 5), -1)

    def test_duplicates(self):
        a = [1, 2, 2, 2, 3]
        idx = ab.binary_search(a, 2)
        self.assertEqual(a[idx], 2)   # どの 2 の位置かは決まっていない

    def test_precondition_documented(self):
        # 二分探索の前提条件（ソート済み）が説明に書かれていること
        self.assertIn("ソート", inspect.getdoc(ab.binary_search))

    def test_unsorted_input_can_fail(self):
        # 前提を満たさない（ソートされていない）と、存在する値でも見つからないことがある
        a = [9, 1, 8, 2, 7]
        self.assertFalse(ab.is_sorted(a))
        self.assertEqual(ab.binary_search(a, 9), -1)

    def test_agrees_with_linear(self):
        data = ab.make_data(500, "few_unique", seed=3)
        s = sorted(data)
        for key in range(-2, 13):
            self.assertEqual(ab.linear_search(s, key) == -1, ab.binary_search(s, key) == -1)


class TestSorts(unittest.TestCase):
    CASES = {
        "random": [5, 2, 9, 1, 5, 6],
        "duplicates": [3, 3, 1, 1, 2, 2],
        "sorted": [1, 2, 3, 4],
        "reversed": [4, 3, 2, 1],
        "empty": [],
        "single": [7],
        "negative": [0, -5, 3, -1],
    }

    def test_all_sorts(self):
        for name, func in ab.SORTS.items():
            for case, data in self.CASES.items():
                with self.subTest(sort=name, case=case):
                    original = list(data)
                    result = func(data)
                    self.assertEqual(list(np.asarray(result).tolist()), sorted(data))
                    self.assertEqual(data, original)   # 入力のリストは書き換えない

    def test_random_large(self):
        data = ab.make_data(300, "random", seed=5)
        for name, func in ab.SORTS.items():
            self.assertTrue(ab.is_sorted(list(func(data))), name)


class TestExperiments(unittest.TestCase):
    def test_make_data(self):
        self.assertTrue(ab.is_sorted(ab.make_data(50, "sorted")))
        self.assertEqual(ab.make_data(50, "reversed"), sorted(ab.make_data(50, "reversed"), reverse=True))
        self.assertLessEqual(len(set(ab.make_data(100, "few_unique"))), 10)
        self.assertEqual(ab.make_data(0), [])
        with self.assertRaises(ValueError):
            ab.make_data(5, "unknown")

    def test_search_experiment(self):
        r = ab.search_experiment(200, queries=10, repeats=2)
        self.assertGreater(r["linear_search_s"], 0)
        self.assertGreater(r["binary_with_sort_s"], r["binary_search_s"])

    def test_sort_experiment_safety_limit(self):
        rows = ab.sort_experiment(ab.QUADRATIC_MAX_N + 1, names=["bubble_sort", "sorted"], repeats=1)
        by = {r["algorithm"]: r for r in rows}
        self.assertIsNone(by["bubble_sort"]["time_s"])
        self.assertIsNotNone(by["sorted"]["time_s"])

    def test_complexity(self):
        self.assertEqual(ab.complexity_value("bubble_sort", 10), 100)
        self.assertAlmostEqual(ab.complexity_value("binary_search", 1024), 10)
        rows = ab.complexity_table([{"algorithm": "sorted", "n": 8, "time_s": 24.0},
                                    {"algorithm": "sorted", "n": 8, "time_s": None}])
        self.assertEqual(len(rows), 1)
        self.assertAlmostEqual(rows[0]["time_per_f"], 1.0)


if __name__ == "__main__":
    unittest.main()
