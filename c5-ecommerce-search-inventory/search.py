# C5：商品IDによる商品検索（完全一致）
#
# 3つの方法で、商品IDから商品（辞書）を探す。見つからなければ None を返す。
#
#   線形探索：商品IDのリストを先頭から順に調べる（教科書 第3章 seq_search）
#   二分探索：商品IDの昇順に並べたリストを、範囲を半分ずつ絞って調べる（教科書 第3章 bin_search）
#   辞書検索：商品IDをキーとする辞書から取り出す（Python の dict）
#
# ■ データの持ち方（整合性のため）
#   商品の辞書そのものは1つだけ作り、3つの索引はどれも「同じ辞書」を参照する。
#   コピーを作らないので、在庫を更新すると、どの方法で検索しても同じ在庫数が返る。
#   在庫の更新は products_by_id（辞書の索引）を正本として行う（inventory.py）。

from textbook.bsearch import bin_search
from textbook.ssearch_while import seq_search


# ------------------------------------------------------------
# 線形探索
# ------------------------------------------------------------

def build_linear_index(products):
    """線形探索用の索引：元の並び順のままの商品IDのリスト

    ids[i] が products[i] の商品IDになる（前処理は O(N)）。
    """
    return [product["id"] for product in products]


def linear_search(ids, products, product_id):
    """線形探索：ids を先頭から調べ、見つかった位置の商品を返す"""
    index = seq_search(ids, product_id)
    if index == -1:
        return None
    return products[index]


# ------------------------------------------------------------
# 二分探索
# ------------------------------------------------------------

def build_sorted_index(products):
    """二分探索用の索引：(商品IDの昇順のリスト, 同じ順に並べた商品のリスト)

    sorted_ids[i] が sorted_products[i] の商品IDになる。
    並べ替えには Python 標準の sorted()（Timsort、O(N log N)）を使う。
    """
    sorted_products = sorted(products, key=lambda product: product["id"])
    sorted_ids = [product["id"] for product in sorted_products]
    return sorted_ids, sorted_products


def binary_search(sorted_ids, sorted_products, product_id):
    """二分探索：昇順の sorted_ids を調べ、見つかった位置の商品を返す

    教科書の bin_search() は空のリストを渡すと IndexError になるため、先に確認する。
    """
    if len(sorted_ids) == 0:
        return None
    index = bin_search(sorted_ids, product_id)
    if index == -1:
        return None
    return sorted_products[index]


# ------------------------------------------------------------
# 辞書検索
# ------------------------------------------------------------

def build_dict_index(products):
    """辞書検索用の索引：{商品ID: 商品}（前処理は平均 O(N)）

    商品IDが重複していたら ValueError にする（後の商品で上書きされるのを防ぐ）。
    """
    products_by_id = {}
    for product in products:
        if product["id"] in products_by_id:
            raise ValueError(f"商品ID {product['id']} が重複しています")
        products_by_id[product["id"]] = product
    return products_by_id


def dict_search(products_by_id, product_id):
    """辞書検索：商品IDから商品を取り出す"""
    return products_by_id.get(product_id)


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO（Core 8・9 / Advanced A）：比較回数を数える版の線形探索・二分探索を自分たちで作る。
# TODO（Advanced C）：商品名の部分一致・カテゴリ・価格帯による検索を作る。
#   辞書検索の平均 O(1) は「商品IDの完全一致」の性質であり、部分一致にはそのまま使えない。
