# C2：DFS・BFS と障害実験の性能比較 — 学生が実験を作るための入口
#
# ここにあるのは「1つのネットワークで1回だけ測る例」だけである。
# V・E・障害率を変えた繰り返し実験、グラフ化は、学生が実装する（下の TODO）。
#
# 実行：python3 benchmark.py

import time

import network
import resilience
import traversal

if __name__ == "__main__":
    # ネットワークの生成時間は、探索時間に含めない
    graph = network.mesh(30, 30)
    v = len(graph)
    e = network.count_edges(graph)

    start = time.perf_counter()
    traversal.dfs(graph, 0)
    dfs_time = time.perf_counter() - start

    start = time.perf_counter()
    traversal.bfs(graph, 0)
    bfs_time = time.perf_counter() - start

    print(f"メッシュ型 30×30（V = {v}, E = {e}）での1回だけの測定例")
    print(f"  DFS: {dfs_time:.6f} 秒")
    print(f"  BFS: {bfs_time:.6f} 秒")
    print(f"  最大連結成分の割合: {resilience.largest_component_ratio(graph, v):.2f}")


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO 1：ノード数 V を増やす（例：100 / 1,000 / 10,000）。
# TODO 2：リンク数 E を増やす（ランダム型の p を変える、など）。
# TODO 3：DFS の処理時間を測定する。
# TODO 4：BFS の処理時間を測定する。
# TODO 5：ネットワーク構造（スター・リング・ランダム・メッシュ）ごとの処理時間を比較する。
# TODO 6：ノード障害率を変える（例：0%, 10%, 20%, ... のノードをランダムに取り除く）。
# TODO 7：リンク障害率を変える。
# TODO 8：障害後の最大連結成分の割合を測定する（分母を明記すること）。
# TODO 9：結果を表・グラフにまとめ、理論計算量 O(V + E) と比較する。
#
# 測定のコツ：
#   - ネットワークの生成・障害の適用の時間と、探索の時間を分けて測る。
#       start = time.perf_counter()
#       traversal.bfs(graph, 0)                 # 測りたい処理だけを挟む
#       elapsed = time.perf_counter() - start
#   - ランダム型や障害の実験では、乱数シードを記録し、複数回の平均・ばらつきを見る。
