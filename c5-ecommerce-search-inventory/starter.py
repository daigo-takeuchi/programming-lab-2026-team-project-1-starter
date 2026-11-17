# C5：ECサイトの商品検索・在庫管理 — starter code
#
# Demo A：商品IDで、線形探索・二分探索・辞書検索を行い、結果を比べる
# Demo B：商品を価格の昇順・降順に並べる
# Demo C：購入・入荷で在庫を更新し、3つの検索方法で在庫が一致することを確かめる
#
# 商品データはすべて架空のもの（data/sample_products.csv）。

from pathlib import Path

import inventory
import products as product_data
import search
import sorting

CSV_FILE = Path(__file__).parent / "data" / "sample_products.csv"
TARGET_ID = 1013        # 検索する商品ID（変えて試してみよう）


def show(product):
    if product is None:
        return "見つかりません"
    return (f"{product['id']} {product['name']} / {product['category']} / "
            f"{product['price']}円 / 在庫 {product['stock']}")


def search_all(product_id):
    """3つの方法で検索した結果を (線形, 二分, 辞書) で返す"""
    return (
        search.linear_search(ids, products, product_id),
        search.binary_search(sorted_ids, sorted_products, product_id),
        search.dict_search(products_by_id, product_id),
    )


print("=== C5：ECサイトの商品検索・在庫管理 ===")
print()

# ------------------------------------------------------------
# Demo A：商品検索
# ------------------------------------------------------------
print("--- Demo A：商品検索 ---")
products = product_data.load_products(CSV_FILE)
print("商品数:", len(products))

# 前処理（索引の作成）。3つの索引は、同じ商品の辞書を参照する
ids = search.build_linear_index(products)
sorted_ids, sorted_products = search.build_sorted_index(products)
products_by_id = search.build_dict_index(products)

for product_id in [TARGET_ID, 9999]:
    linear, binary, by_dict = search_all(product_id)
    print(f"商品ID {product_id} を検索")
    print("  線形探索:", show(linear))
    print("  二分探索:", show(binary))
    print("  辞書検索:", show(by_dict))
    print("  3方式の結果が一致:", linear is binary is by_dict)

# ------------------------------------------------------------
# Demo B：価格順ソート
# ------------------------------------------------------------
print()
print("--- Demo B：価格順ソート（同じ価格は商品IDの小さい順） ---")
print("価格の安い順 上位5件:")
for product in sorting.sort_by_price(products)[:5]:
    print("  " + show(product))
print("価格の高い順 上位5件:")
for product in sorting.sort_by_price(products, descending=True)[:5]:
    print("  " + show(product))
same = sorting.sort_by_price_insertion(products) == sorting.sort_by_price(products)
print("教科書の挿入ソート版と sorted() 版の結果が一致:", same)

# ------------------------------------------------------------
# Demo C：在庫更新
# ------------------------------------------------------------
print()
print("--- Demo C：在庫更新 ---")
product_id = 1007
print(f"商品ID {product_id} の在庫:", inventory.get_stock(products_by_id, product_id))

ok = inventory.purchase(products_by_id, product_id, 3)
print(f"3個購入 → {'成功' if ok else '在庫不足'}、在庫:", inventory.get_stock(products_by_id, product_id))

ok = inventory.purchase(products_by_id, product_id, 100)
print(f"100個購入 → {'成功' if ok else '在庫不足（在庫は変更しない）'}、在庫:",
      inventory.get_stock(products_by_id, product_id))

inventory.restock(products_by_id, product_id, 10)
print("10個入荷 → 在庫:", inventory.get_stock(products_by_id, product_id))

stocks = [p["stock"] for p in search_all(product_id)]
print("3つの検索方法で得た在庫数:", stocks, " 一致:", len(set(stocks)) == 1)


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：benchmark.py を使って、商品数 N と検索回数 Q を変えて検索時間を比較する。
# TODO 2：sorting.py のバブルソート版・選択ソート版を実装する。
# TODO 3：在庫0の商品（1010, 1016, 1019）を購入しようとするとどうなるか確かめる。
