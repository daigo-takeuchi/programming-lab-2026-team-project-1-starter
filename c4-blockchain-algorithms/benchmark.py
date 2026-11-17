# C4：Merkle Tree の性能比較 — 学生が実験を作るための入口
#
# ここにあるのは「1つの N で1回だけ測る例」だけである。
# N を変えた繰り返し測定、Proof の生成・検証の測定、グラフ化は、学生が実装する（下の TODO）。
#
# 実行：python3 benchmark.py

import hashlib
import time

import merkle_tree

if __name__ == "__main__":
    N = 1024

    # データの生成時間は、測定に含めない
    data = [f"Tx {i}" for i in range(N)]

    start = time.perf_counter()
    for d in data:
        hashlib.sha256(d.encode("utf-8")).digest()
    all_hash_time = time.perf_counter() - start

    start = time.perf_counter()
    tree = merkle_tree.build_tree(data)
    build_time = time.perf_counter() - start

    print(f"N = {N}（1回だけの測定例）")
    print(f"  全データのハッシュ計算 : {all_hash_time:.6f} 秒")
    print(f"  Merkle Tree の構築      : {build_time:.6f} 秒（木の高さ {merkle_tree.tree_height(tree)}）")


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO 1：データ件数 N を変更する（例：2^4, 2^8, 2^12, 2^16）。
# TODO 2：全件データのハッシュ計算時間を測定する。
# TODO 3：Merkle Tree の構築時間を測定する。
# TODO 4：Merkle Proof の生成時間を測定する（generate_proof を実装してから）。
# TODO 5：Merkle Proof の検証時間を測定する（verify_proof を実装してから）。
# TODO 6：必要なハッシュ計算回数を比較する（complexity.py の理論値とも比べる）。
# TODO 7：Proof のデータサイズ（兄弟ハッシュ 32 バイト × 個数 ＋ 左右の情報）を測定する。
# TODO 8：メモリ使用量を比較する（tracemalloc モジュール）。
# TODO 9：結果を表・グラフにまとめる。
# TODO 10：理論計算量（構築 O(N)、Proof 検証 O(log N)）と実測結果を比較する。
#
# 比較条件に注意：
#   - 「全件を受け取って Root を作り直す方法」と「既知の Root に対して Proof で1件を検証する方法」は、
#     前提が違う。後者は、Root と Proof を信頼できる経路で手に入れていることが前提である。
#   - 構築（O(N)）と検証（O(log N)）を混同しない。
#   - 測りたい処理だけを time.perf_counter() で挟む：
#       start = time.perf_counter()
#       merkle_tree.build_tree(data)
#       elapsed = time.perf_counter() - start
#   - 1回の処理が短すぎるときは、何回も繰り返して合計時間を測る。
