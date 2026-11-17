# C5：価格順ソートのテスト
#
# バブルソート版・選択ソート版は学生の課題なので、未実装の間はテストをスキップする。

import copy
import unittest
from pathlib import Path

import products as product_data
import sorting

SAMPLE_CSV = Path(__file__).parent.parent / "data" / "sample_products.csv"


class TestSorting(unittest.TestCase):

    def setUp(self):
        self.products = product_data.load_products(SAMPLE_CSV)

    def test_ascending(self):
        """1. 価格の昇順"""
        result = sorting.sort_by_price(self.products)
        prices = [p["price"] for p in result]
        self.assertEqual(prices, sorted(prices))
        self.assertEqual(result[0]["id"], 1002)       # 120円の2件のうち、IDが小さい方

    def test_descending(self):
        """2. 価格の降順"""
        result = sorting.sort_by_price(self.products, descending=True)
        prices = [p["price"] for p in result]
        self.assertEqual(prices, sorted(prices, reverse=True))
        self.assertEqual(result[0]["name"], "Office Chair")

    def test_same_price(self):
        """3. 同じ価格の商品は、昇順・降順とも商品IDの小さい順"""
        for descending in (False, True):
            result = sorting.sort_by_price(self.products, descending=descending)
            for a, b in zip(result, result[1:]):
                if a["price"] == b["price"]:
                    self.assertLess(a["id"], b["id"])
        ids_350 = [p["id"] for p in sorting.sort_by_price(self.products) if p["price"] == 350]
        self.assertEqual(ids_350, [1001, 1007])

    def test_correspondence_kept(self):
        """4・5. ソート後も商品の情報は元のまま、商品の集合も失われない"""
        backup = copy.deepcopy(self.products)
        for result in [sorting.sort_by_price(self.products),
                       sorting.sort_by_price(self.products, descending=True),
                       sorting.sort_by_price_insertion(self.products),
                       sorting.sort_by_price_insertion(self.products, descending=True)]:
            self.assertEqual(sorted(result, key=lambda p: p["id"]),
                             sorted(backup, key=lambda p: p["id"]))
        self.assertEqual(self.products, backup)        # 元のリストの並び順も変わらない

    def test_insertion_matches_sorted(self):
        """教科書の挿入ソート版は sorted() 版と同じ結果になる"""
        many = product_data.generate_products(200, seed=3)
        for descending in (False, True):
            self.assertEqual(sorting.sort_by_price_insertion(many, descending),
                             sorting.sort_by_price(many, descending))

    def test_empty(self):
        """6. 空リストでも安全"""
        self.assertEqual(sorting.sort_by_price([]), [])
        self.assertEqual(sorting.sort_by_price_insertion([]), [])

    def test_student_sorts(self):
        """（学生の課題）バブルソート版・選択ソート版は sorted() 版と同じ結果になる"""
        for func in (sorting.sort_by_price_bubble, sorting.sort_by_price_selection):
            for descending in (False, True):
                try:
                    result = func(self.products, descending)
                except NotImplementedError:
                    self.skipTest(f"{func.__name__} は未実装")
                self.assertEqual(result, sorting.sort_by_price(self.products, descending))


if __name__ == "__main__":
    unittest.main()
