# C5：在庫管理のテスト

import unittest
from pathlib import Path

import inventory
import products as product_data
import search

SAMPLE_CSV = Path(__file__).parent.parent / "data" / "sample_products.csv"


class TestInventory(unittest.TestCase):

    def setUp(self):
        self.products = product_data.load_products(SAMPLE_CSV)
        self.by_id = search.build_dict_index(self.products)

    def test_purchase(self):
        """1. 購入で在庫が減る"""
        self.assertTrue(inventory.purchase(self.by_id, 1007, 3))
        self.assertEqual(inventory.get_stock(self.by_id, 1007), 17)
        self.assertTrue(inventory.purchase(self.by_id, 1007, 17))      # ちょうど在庫数まで買える
        self.assertEqual(inventory.get_stock(self.by_id, 1007), 0)

    def test_restock(self):
        """2. 入荷で在庫が増える"""
        inventory.restock(self.by_id, 1019, 10)
        self.assertEqual(inventory.get_stock(self.by_id, 1019), 10)

    def test_insufficient_stock(self):
        """3・4. 在庫不足の購入は拒否され、在庫数は変わらない"""
        self.assertFalse(inventory.purchase(self.by_id, 1004, 9))       # 在庫 8
        self.assertEqual(inventory.get_stock(self.by_id, 1004), 8)
        self.assertFalse(inventory.purchase(self.by_id, 1016, 1))       # 在庫 0
        self.assertEqual(inventory.get_stock(self.by_id, 1016), 0)

    def test_invalid_quantity(self):
        """5・6. 負の数量・0・整数でない数量は拒否し、在庫は変わらない"""
        for bad in [-1, 0, 1.5, "3", True]:
            with self.subTest(quantity=bad):
                with self.assertRaises(ValueError):
                    inventory.purchase(self.by_id, 1007, bad)
                with self.assertRaises(ValueError):
                    inventory.restock(self.by_id, 1007, bad)
        self.assertEqual(inventory.get_stock(self.by_id, 1007), 20)

    def test_unknown_product(self):
        """7. 存在しない商品IDは KeyError"""
        for func, args in [(inventory.get_stock, ()), (inventory.purchase, (1,)), (inventory.restock, (1,))]:
            with self.assertRaises(KeyError):
                func(self.by_id, 9999, *args)

    def test_never_negative(self):
        """8. 何度購入しても在庫は負にならない"""
        for _ in range(100):
            inventory.purchase(self.by_id, 1017, 2)
        self.assertEqual(inventory.get_stock(self.by_id, 1017), 1)       # 在庫 3 から 2 個だけ
        for p in self.products:
            self.assertGreaterEqual(p["stock"], 0)

    def test_consistent_with_search(self):
        """9. 在庫更新後も、3つの検索方法の結果が一致する"""
        ids = search.build_linear_index(self.products)
        sorted_ids, sorted_products = search.build_sorted_index(self.products)
        inventory.purchase(self.by_id, 1013, 2)
        inventory.restock(self.by_id, 1013, 6)
        stocks = [
            search.linear_search(ids, self.products, 1013)["stock"],
            search.binary_search(sorted_ids, sorted_products, 1013)["stock"],
            search.dict_search(self.by_id, 1013)["stock"],
        ]
        self.assertEqual(stocks, [9, 9, 9])


if __name__ == "__main__":
    unittest.main()
