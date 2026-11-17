# A1：教科書の2つの探索関数のテスト
#
# 教科書の関数はそのまま使い、昇順に整列済みのデータで検証する。
# 注意：教科書の bin_search() は空リストに対応していない（IndexError になる）ため、
#       空リストはテストに含めない。

import unittest

from textbook.ssearch_while import seq_search
from textbook.bsearch import bin_search

SEARCH_FUNCTIONS = [seq_search, bin_search]

DATA = [2, 5, 8, 12, 17, 21, 30]


class TestSearch(unittest.TestCase):

    def test_linear_search_finds_first_middle_last(self):
        """1. 線形探索で先頭・中央・末尾の要素が見つかる"""
        self.assertEqual(seq_search(DATA, 2), 0)
        self.assertEqual(seq_search(DATA, 12), 3)
        self.assertEqual(seq_search(DATA, 30), 6)

    def test_binary_search_finds_first_middle_last(self):
        """2. 二分探索で先頭・中央・末尾の要素が見つかる"""
        self.assertEqual(bin_search(DATA, 2), 0)
        self.assertEqual(bin_search(DATA, 12), 3)
        self.assertEqual(bin_search(DATA, 30), 6)

    def test_not_found(self):
        """3. 存在しない値では -1 を返す（範囲より小さい・間・大きい値）"""
        for search in SEARCH_FUNCTIONS:
            for key in [1, 10, 99]:
                with self.subTest(func=search.__name__, key=key):
                    self.assertEqual(search(DATA, key), -1)

    def test_single_element(self):
        """4. 要素数1のリストでも正しく動作する"""
        for search in SEARCH_FUNCTIONS:
            with self.subTest(func=search.__name__):
                self.assertEqual(search([7], 7), 0)
                self.assertEqual(search([7], 3), -1)
                self.assertEqual(search([7], 9), -1)

    def test_negative_numbers(self):
        """5. 負の整数を含む整列済みリストでも正しく動作する"""
        data = [-30, -12, -5, 0, 4, 9]
        for search in SEARCH_FUNCTIONS:
            with self.subTest(func=search.__name__):
                for i, key in enumerate(data):
                    self.assertEqual(search(data, key), i)
                self.assertEqual(search(data, -7), -1)

    def test_various_sorted_lists(self):
        """6. 複数の整列済みリストで、すべての要素の位置が正しく求まる"""
        lists = [
            [1, 2],
            [1, 3, 5],
            [10, 20, 30, 40],
            list(range(0, 100, 3)),
            list(range(1000)),
        ]
        for data in lists:
            for search in SEARCH_FUNCTIONS:
                with self.subTest(func=search.__name__, n=len(data)):
                    for i, key in enumerate(data):
                        self.assertEqual(search(data, key), i)
                    self.assertEqual(search(data, data[-1] + 1), -1)

    def test_duplicates(self):
        """7. 重複要素があっても、返したインデックスの位置の値が探索対象と一致する"""
        data = [1, 2, 2, 2, 3, 5, 5, 8]
        for search in SEARCH_FUNCTIONS:
            for key in [2, 5]:
                with self.subTest(func=search.__name__, key=key):
                    idx = search(data, key)
                    self.assertTrue(0 <= idx < len(data))
                    self.assertEqual(data[idx], key)


if __name__ == "__main__":
    unittest.main()
