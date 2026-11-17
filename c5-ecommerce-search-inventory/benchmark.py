# C5：商品検索の性能比較 — 学生が実験を作るための入口
#
# ここにあるのは「1つの N・Q で1回だけ測る例」だけである。
# N・Q・成功率を変えた繰り返し測定、ソート・在庫更新の測定、グラフ化は、学生が実装する（下の TODO）。
#
# 実行：python3 benchmark.py

import random
import time

import products as product_data
import search

if __name__ == "__main__":
    N = 10_000      # 商品数
    Q = 200         # 検索回数

    # 商品データと検索キーの生成時間は、測定に含めない
    products = product_data.generate_products(N, seed=2026)
    rng = random.Random(1)
    # 半分は存在する商品ID、半分は存在しない可能性のあるID（1〜2N の範囲）
    keys = [rng.choice(products)["id"] for _ in range(Q // 2)] + \
           [rng.randrange(1, 2 * N + 1) for _ in range(Q - Q // 2)]

    # 前処理の時間
    start = time.perf_counter()
    ids = search.build_linear_index(products)
    linear_build = time.perf_counter() - start

    start = time.perf_counter()
    sorted_ids, sorted_products = search.build_sorted_index(products)
    sorted_build = time.perf_counter() - start

    start = time.perf_counter()
    products_by_id = search.build_dict_index(products)
    dict_build = time.perf_counter() - start

    # 検索の時間（Q 回の合計）
    start = time.perf_counter()
    linear_results = [search.linear_search(ids, products, k) for k in keys]
    linear_time = time.perf_counter() - start

    start = time.perf_counter()
    binary_results = [search.binary_search(sorted_ids, sorted_products, k) for k in keys]
    binary_time = time.perf_counter() - start

    start = time.perf_counter()
    dict_results = [search.dict_search(products_by_id, k) for k in keys]
    dict_time = time.perf_counter() - start

    print(f"N = {N:,}, Q = {Q}（1回だけの測定例）")
    print(f"  線形探索：前処理 {linear_build:.6f} 秒、検索 {linear_time:.6f} 秒")
    print(f"  二分探索：前処理 {sorted_build:.6f} 秒、検索 {binary_time:.6f} 秒")
    print(f"  辞書検索：前処理 {dict_build:.6f} 秒、検索 {dict_time:.6f} 秒")
    print("  3方式の結果が一致:", linear_results == binary_results == dict_results)
    print("  検索成功の回数:", sum(r is not None for r in dict_results), "/", Q)


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO 1：商品数 N を増やす（例：100 / 1,000 / 10,000 / 100,000）。
# TODO 2：線形探索の時間を測定する。
# TODO 3：二分探索の時間を測定する。
# TODO 4：辞書検索の時間を測定する。
# TODO 5：検索成功・失敗を分けて比較する（存在しない商品IDの検索は、線形探索では最悪の場合になる）。
# TODO 6：検索回数 Q を変更する（Q = 1 と Q = 10,000 で、前処理を含めた総コストの順位は変わるか？）。
# TODO 7：ソート時間を測定する（sorted と教科書のソート）。
# TODO 8：辞書構築時間を測定する。
# TODO 9：在庫更新の時間を測定する（商品の特定に使う検索方法ごとに）。
# TODO 10：メモリ使用量を比較する（tracemalloc モジュール）。
# TODO 11：結果を表・グラフにまとめる。
# TODO 12：理論計算量と実測結果を比較する。
#
# 公平な比較の条件：
#   - 同じ商品集合・同じ検索キー・同じ検索回数・同じ成功率を使う。
#   - 前処理時間と検索時間を分けて記録する（二分探索や辞書を「常に速い」と結論しない）。
#   - 複数回測定する。商品データの生成時間は検索時間に含めない。
#   - 測りたい処理だけを time.perf_counter() で挟む：
#       start = time.perf_counter()
#       search.dict_search(products_by_id, key)
#       elapsed = time.perf_counter() - start
