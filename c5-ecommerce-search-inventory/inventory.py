# C5：在庫管理
#
# 商品IDをキーとする辞書 products_by_id（search.build_dict_index で作る）を正本として、
# 在庫数を読み書きする。線形探索・二分探索の索引も同じ商品の辞書を参照しているので、
# ここで在庫を更新すると、どの検索方法でも更新後の在庫数が返る。
#
# 既存の商品の在庫を変えるだけなら、商品IDの索引を作り直す必要はない。
# 商品の追加・削除や商品IDの変更をする場合は、すべての索引の更新が必要になる（Advanced B）。


def _find(products_by_id, product_id):
    product = products_by_id.get(product_id)
    if product is None:
        raise KeyError(f"商品ID {product_id} は存在しません")
    return product


def _check_quantity(quantity):
    if not isinstance(quantity, int) or isinstance(quantity, bool) or quantity <= 0:
        raise ValueError(f"数量は正の整数である必要があります（{quantity!r}）")


def get_stock(products_by_id, product_id):
    """現在の在庫数を返す（商品がなければ KeyError）"""
    return _find(products_by_id, product_id)["stock"]


def purchase(products_by_id, product_id, quantity):
    """購入：在庫を quantity だけ減らす

    戻り値：購入できたら True、在庫不足なら False（在庫は変更しない）
    商品が存在しなければ KeyError、数量が正の整数でなければ ValueError。
    """
    product = _find(products_by_id, product_id)
    _check_quantity(quantity)
    if product["stock"] < quantity:
        return False                    # 在庫不足：何も変更しない
    product["stock"] -= quantity
    return True


def restock(products_by_id, product_id, quantity):
    """入荷：在庫を quantity だけ増やす

    商品が存在しなければ KeyError、数量が正の整数でなければ ValueError。
    """
    product = _find(products_by_id, product_id)
    _check_quantity(quantity)
    product["stock"] += quantity


# ------------------------------------------------------------
# 学生が取り組む課題（Advanced E）
# ------------------------------------------------------------
# TODO：複数の商品をまとめて購入する処理を設計する。
#       途中の商品で在庫不足になったら、それまでに減らした在庫を元に戻す（ロールバック）か、
#       最初にすべての在庫を確認してから減らすか、を比べる。
