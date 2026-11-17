# C5：価格順ソート
#
# 並べる規則：価格の順に並べ、同じ価格の商品は商品IDの小さい順にする（毎回同じ結果になる）。
#   昇順：(価格, 商品ID) の小さい順
#   降順：価格の大きい順。同じ価格なら商品IDの小さい順
#
# どの関数も、新しいリストを返し、元のリストの並び順は変えない。
# リストの中身は元と同じ商品の辞書（コピーではない）なので、商品の情報の対応は崩れない。

from textbook.insertion_sort import insertion_sort


def _sort_key(product, descending):
    if descending:
        return (-product["price"], product["id"])
    return (product["price"], product["id"])


def sort_by_price(products, descending=False):
    """Python 標準の sorted() による価格順ソート"""
    return sorted(products, key=lambda product: _sort_key(product, descending))


def sort_by_price_insertion(products, descending=False):
    """教科書の挿入ソート（insertion_sort）による価格順ソート

    教科書のソート関数は、リストの要素どうしを > で比べて並べ替える（in-place）。
    商品の辞書は > で比べられないので、次の手順で行う。
      1. 各商品から (価格, 商品ID) の組を作る（降順なら (−価格, 商品ID)）
      2. 組のリストを insertion_sort() で並べ替える
      3. 並んだ組の商品IDから、商品の辞書を取り出して並べる
    組に商品IDを入れているので、価格と商品の対応が失われない。
    """
    products_by_id = {product["id"]: product for product in products}
    pairs = [_sort_key(product, descending) for product in products]
    insertion_sort(pairs)
    return [products_by_id[product_id] for _, product_id in pairs]


# ------------------------------------------------------------
# 学生が取り組む課題（sort_by_price_insertion を参考に）
# ------------------------------------------------------------

def sort_by_price_bubble(products, descending=False):
    """TODO 1：教科書のバブルソート（textbook/bubble_sort1.py の bubble_sort）による価格順ソート"""
    raise NotImplementedError("バブルソートによる価格順ソートは学生の課題です")


def sort_by_price_selection(products, descending=False):
    """TODO 2：教科書の選択ソート（textbook/selection_sort.py の selection_sort）による価格順ソート"""
    raise NotImplementedError("選択ソートによる価格順ソートは学生の課題です")


# TODO 3：挿入ソート版（sort_by_price_insertion）の処理時間・比較回数を調べる。
# TODO 4：Python 標準の sorted（sort_by_price）と比較する。
# TODO 5：商品数 N と処理時間の関係を調べる。
# TODO 6：同じ価格の商品の扱い方を考える（商品IDを組に入れないとどうなるか？ 安定ソートとは？）。
# TODO 7：昇順・降順の切り替えが正しく動くことを確かめる。
