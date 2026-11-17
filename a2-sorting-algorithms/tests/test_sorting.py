# A2：教科書の3つのソート関数のテスト
#
# 教科書の関数はそのまま使う。どの関数もリストを直接書き換える（in-place）ため、
# 毎回コピーを渡して検証する。正解値には Python 標準の sorted() を使う。

import random
import unittest

from textbook.bubble_sort1 import bubble_sort
from textbook.selection_sort import selection_sort
from textbook.insertion_sort import insertion_sort

SORT_FUNCTIONS = [bubble_sort, selection_sort, insertion_sort]


class TestSorting(unittest.TestCase):

    def assert_sorts_correctly(self, data):
        """3つの関数それぞれで data のコピーをソートし、sorted(data) と一致するか確認する"""
        for sort_function in SORT_FUNCTIONS:
            with self.subTest(func=sort_function.__name__, data=data):
                values = data.copy()
                sort_function(values)
                self.assertEqual(values, sorted(data))

    def test_basic(self):
        """1. 昇順に正しくソートできる"""
        self.assert_sorts_correctly([8, 3, 5, 1, 9, 2, 7])

    def test_empty(self):
        """2. 空リストを処理できる"""
        self.assert_sorts_correctly([])

    def test_single_element(self):
        """3. 要素数1のリストを処理できる"""
        self.assert_sorts_correctly([42])

    def test_already_sorted(self):
        """4. すでに昇順のリストを処理できる"""
        self.assert_sorts_correctly([1, 2, 3, 4, 5, 6, 7])

    def test_reversed(self):
        """5. 降順のリストを処理できる"""
        self.assert_sorts_correctly([7, 6, 5, 4, 3, 2, 1])

    def test_duplicates(self):
        """6. 重複値を含むリストを処理できる"""
        self.assert_sorts_correctly([5, 3, 5, 1, 3, 3, 9, 1])
        self.assert_sorts_correctly([2, 2, 2, 2])

    def test_negative_numbers(self):
        """7. 負の整数を含むリストを処理できる"""
        self.assert_sorts_correctly([3, -1, 0, -7, 12, -1, 5])

    def test_results_match(self):
        """8. 3つのアルゴリズムの結果が一致する（乱数データで確認）"""
        rng = random.Random(2026)     # 乱数シードを固定して、毎回同じデータにする
        for n in [2, 10, 50, 100]:
            data = [rng.randint(-50, 50) for _ in range(n)]
            results = []
            for sort_function in SORT_FUNCTIONS:
                values = data.copy()
                sort_function(values)
                results.append(values)
            with self.subTest(n=n):
                self.assertEqual(results[0], results[1])
                self.assertEqual(results[1], results[2])
                self.assertEqual(results[0], sorted(data))

    def test_in_place_and_returns_none(self):
        """9. リストを直接書き換え（in-place）、戻り値は None"""
        for sort_function in SORT_FUNCTIONS:
            with self.subTest(func=sort_function.__name__):
                values = [3, 1, 2]
                result = sort_function(values)
                self.assertIsNone(result)
                self.assertEqual(values, [1, 2, 3])

    def test_original_unchanged_when_copied(self):
        """10. コピーを渡せば、元データは変更されない"""
        data = [8, 3, 5, 1, 9, 2, 7]
        for sort_function in SORT_FUNCTIONS:
            with self.subTest(func=sort_function.__name__):
                values = data.copy()
                sort_function(values)
                self.assertEqual(data, [8, 3, 5, 1, 9, 2, 7])


if __name__ == "__main__":
    unittest.main()
