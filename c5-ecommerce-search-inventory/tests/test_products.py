# C5：商品データ読み込みのテスト

import os
import tempfile
import unittest
from pathlib import Path

import products as product_data

SAMPLE_CSV = Path(__file__).parent.parent / "data" / "sample_products.csv"
HEADER = "id,name,category,price,stock\n"


class TestProducts(unittest.TestCase):

    def setUp(self):
        self.tmpdir = tempfile.TemporaryDirectory()

    def tearDown(self):
        self.tmpdir.cleanup()

    def write_csv(self, text):
        path = os.path.join(self.tmpdir.name, "products.csv")
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        return path

    def test_load_sample(self):
        """1. サンプル CSV を読み込める（20件、条件を満たす）"""
        products = product_data.load_products(SAMPLE_CSV)
        self.assertEqual(len(products), 20)
        self.assertEqual(products[0], {"id": 1007, "name": "Notebook", "category": "Stationery",
                                       "price": 350, "stock": 20})
        ids = [p["id"] for p in products]
        self.assertEqual(len(set(ids)), 20)                       # 商品IDが重複しない
        self.assertNotEqual(ids, sorted(ids))                     # 昇順に並んでいない
        prices = [p["price"] for p in products]
        self.assertLess(len(set(prices)), len(prices))            # 同じ価格の商品がある
        self.assertIn(0, [p["stock"] for p in products])          # 在庫0の商品がある
        self.assertGreaterEqual(len({p["category"] for p in products}), 3)

    def test_integer_types(self):
        """2・3. 商品ID・価格・在庫数は整数として読み込まれる"""
        for p in product_data.load_products(SAMPLE_CSV):
            for key in ("id", "price", "stock"):
                self.assertIs(type(p[key]), int)

    def test_duplicate_id(self):
        """4. 商品IDの重複を検出する"""
        path = self.write_csv(HEADER + "1,A,X,100,1\n2,B,X,200,1\n1,C,X,300,1\n")
        with self.assertRaises(ValueError):
            product_data.load_products(path)

    def test_negative_price(self):
        """5. 負の価格を拒否する"""
        path = self.write_csv(HEADER + "1,A,X,-100,1\n")
        with self.assertRaises(ValueError):
            product_data.load_products(path)

    def test_negative_stock(self):
        """6. 負の在庫数を拒否する"""
        path = self.write_csv(HEADER + "1,A,X,100,-1\n")
        with self.assertRaises(ValueError):
            product_data.load_products(path)

    def test_invalid_numbers_and_columns(self):
        """数値でない値・値の不足・列の不足を拒否する"""
        for text in [HEADER + "1,A,X,abc,1\n", HEADER + "x,A,X,100,1\n",
                     HEADER + "1,A,X,100\n", "id,name,price\n1,A,100\n"]:
            with self.subTest(text=text):
                with self.assertRaises(ValueError):
                    product_data.load_products(self.write_csv(text))

    def test_empty_csv(self):
        """7. 空の CSV（完全に空・見出しだけ）は空のリストになる"""
        self.assertEqual(product_data.load_products(self.write_csv("")), [])
        self.assertEqual(product_data.load_products(self.write_csv(HEADER)), [])

    def test_generate_products(self):
        """実験用の商品生成：件数・ID の重複なし・再現可能"""
        products = product_data.generate_products(500, seed=1)
        self.assertEqual(len(products), 500)
        self.assertEqual(len({p["id"] for p in products}), 500)
        self.assertEqual(products, product_data.generate_products(500, seed=1))


if __name__ == "__main__":
    unittest.main()
