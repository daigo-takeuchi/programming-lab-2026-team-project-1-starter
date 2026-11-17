# C5：商品検索のテスト

import unittest
from pathlib import Path

import inventory
import products as product_data
import search

SAMPLE_CSV = Path(__file__).parent.parent / "data" / "sample_products.csv"


class TestSearch(unittest.TestCase):

    def setUp(self):
        self.products = product_data.load_products(SAMPLE_CSV)
        self.ids = search.build_linear_index(self.products)
        self.sorted_ids, self.sorted_products = search.build_sorted_index(self.products)
        self.by_id = search.build_dict_index(self.products)

    def search_all(self, product_id):
        return (
            search.linear_search(self.ids, self.products, product_id),
            search.binary_search(self.sorted_ids, self.sorted_products, product_id),
            search.dict_search(self.by_id, product_id),
        )

    def test_linear(self):
        """1. 線形探索で商品を見つけられる"""
        self.assertEqual(search.linear_search(self.ids, self.products, 1013)["name"], "Headphones")

    def test_binary(self):
        """2. 二分探索で商品を見つけられる"""
        found = search.binary_search(self.sorted_ids, self.sorted_products, 1013)
        self.assertEqual(found["name"], "Headphones")

    def test_dict(self):
        """3. 辞書検索で商品を見つけられる"""
        self.assertEqual(search.dict_search(self.by_id, 1013)["name"], "Headphones")

    def test_same_product_all_ids(self):
        """4. すべての商品IDで、3方式が同じ商品（同じ辞書）を返す"""
        for product in self.products:
            linear, binary, by_dict = self.search_all(product["id"])
            self.assertIs(linear, product)
            self.assertIs(binary, product)
            self.assertIs(by_dict, product)

    def test_not_found(self):
        """5. 存在しない商品IDは None"""
        for product_id in [0, 1000, 1021, 9999, -5]:
            self.assertEqual(self.search_all(product_id), (None, None, None))
        # 空の商品リストでも安全（教科書の bin_search は空リストで IndexError になる）
        self.assertIsNone(search.binary_search([], [], 1001))
        self.assertIsNone(search.linear_search([], [], 1001))

    def test_min_and_max_ids(self):
        """6. 商品IDの最小値・最大値を検索できる"""
        for product_id in [min(self.ids), max(self.ids)]:
            linear, binary, by_dict = self.search_all(product_id)
            self.assertEqual(linear["id"], product_id)
            self.assertIs(linear, binary)
            self.assertIs(binary, by_dict)

    def test_unsorted_source(self):
        """7. 元データの商品IDが未ソートでも正しく動作する（元の並び順は変えない）"""
        self.assertNotEqual(self.ids, sorted(self.ids))
        self.assertEqual(self.sorted_ids, sorted(self.ids))
        self.assertEqual(self.products[0]["id"], 1007)
        for i in range(len(self.sorted_ids)):
            self.assertEqual(self.sorted_products[i]["id"], self.sorted_ids[i])
        many = product_data.generate_products(300, seed=5)
        ids = search.build_linear_index(many)
        sorted_ids, sorted_products = search.build_sorted_index(many)
        by_id = search.build_dict_index(many)
        for key in range(0, 602):
            expected = by_id.get(key)
            self.assertIs(search.linear_search(ids, many, key), expected)
            self.assertIs(search.binary_search(sorted_ids, sorted_products, key), expected)

    def test_consistent_after_stock_update(self):
        """8. 在庫更新後も、3方式で同じ在庫数を返す"""
        inventory.purchase(self.by_id, 1004, 5)
        inventory.restock(self.by_id, 1019, 7)
        self.assertEqual([p["stock"] for p in self.search_all(1004)], [3, 3, 3])
        self.assertEqual([p["stock"] for p in self.search_all(1019)], [7, 7, 7])

    def test_duplicate_ids_rejected(self):
        """商品IDの重複を許可しない"""
        with self.assertRaises(ValueError):
            search.build_dict_index([{"id": 1}, {"id": 1}])


if __name__ == "__main__":
    unittest.main()
