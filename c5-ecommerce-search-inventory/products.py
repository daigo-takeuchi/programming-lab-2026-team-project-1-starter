# C5：商品データの読み込み・生成
#
# 商品は次のような辞書で表す（すべて架空のデータ）。
#   {"id": 1001, "name": "Notebook", "category": "Stationery", "price": 350, "stock": 20}
#
#   - id    ：商品ID（整数、重複なし）
#   - price ：価格（0 以上の整数）
#   - stock ：在庫数（0 以上の整数）

import csv
import random

FIELDS = ["id", "name", "category", "price", "stock"]


def _to_int(value, name, line_number):
    try:
        return int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{line_number}行目：{name} が整数ではありません（{value!r}）") from None


def load_products(path):
    """CSV ファイルから商品のリストを読み込む

    不正なデータ（数値でない値、負の価格・在庫、重複した商品ID、列の不足）は ValueError にする。
    空のファイルや、見出し行だけのファイルは空のリストを返す。
    """
    products = []
    seen_ids = set()
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if reader.fieldnames is None:          # 完全に空のファイル
            return []
        missing = [name for name in FIELDS if name not in reader.fieldnames]
        if missing:
            raise ValueError(f"必要な列がありません：{missing}")

        for line_number, row in enumerate(reader, start=2):     # 1行目は見出し
            product_id = _to_int(row["id"], "id", line_number)
            price = _to_int(row["price"], "price", line_number)
            stock = _to_int(row["stock"], "stock", line_number)
            if price < 0:
                raise ValueError(f"{line_number}行目：価格が負です（{price}）")
            if stock < 0:
                raise ValueError(f"{line_number}行目：在庫数が負です（{stock}）")
            if product_id in seen_ids:
                raise ValueError(f"{line_number}行目：商品ID {product_id} が重複しています")
            seen_ids.add(product_id)
            products.append({
                "id": product_id,
                "name": row["name"],
                "category": row["category"],
                "price": price,
                "stock": stock,
            })
    return products


def generate_products(n, seed=0):
    """実験用に、架空の商品を n 個作る

    商品IDは 1 〜 2n の範囲から重複なしに選び、順番はばらばらにする
    （存在しない商品IDを検索する実験ができるように、使わないIDを残している）。
    """
    rng = random.Random(seed)
    ids = rng.sample(range(1, 2 * n + 1), n)
    categories = ["Stationery", "Electronics", "Kitchen", "Furniture"]
    return [
        {
            "id": product_id,
            "name": f"Item {product_id}",
            "category": rng.choice(categories),
            "price": rng.randrange(100, 10001, 10),
            "stock": rng.randrange(0, 100),
        }
        for product_id in ids
    ]
