# D3：経路探索の性能比較 — 学生が実験を作るための入口
#
# ここにあるのは「格子状の架空の道路ネットワークを作る関数」と「1つの条件で1回だけ測る例」だけである。
# V・E・閉鎖率を変えた繰り返し実験、到達可能率の集計、グラフ化は、学生が実装する（下の TODO）。
#
# 実行：python3 benchmark.py

import random
import time

import routing


def make_grid_network(rows, cols, seed=0):
    """rows × cols の格子状の架空の道路ネットワークを作る

    ノード (r, c) の座標は (c, r)。隣り合うノードを道路でつなぐ。
    道路の距離は直線距離（= 1）の 1.0〜1.5 倍（直線距離以上なので、直線距離を A* に使える）。
    すべての道路は "open"、コスト倍率は 1.0。
    """
    rng = random.Random(seed)
    nodes = {f"N{r}_{c}": {"name": f"N{r}_{c}", "x": c, "y": r} for r in range(rows) for c in range(cols)}
    roads = []
    for r in range(rows):
        for c in range(cols):
            for dr, dc in ((0, 1), (1, 0)):
                if r + dr < rows and c + dc < cols:
                    roads.append({"from": f"N{r}_{c}", "to": f"N{r + dr}_{c + dc}",
                                  "distance": round(rng.uniform(1.0, 1.5), 3),
                                  "status": "open", "cost_multiplier": 1.0})
    return {"nodes": nodes, "roads": roads}


if __name__ == "__main__":
    ROWS, COLS = 30, 30

    # ネットワークの生成時間は、探索時間に含めない
    network = make_grid_network(ROWS, COLS, seed=2026)
    start, goal = "N0_0", f"N{ROWS - 1}_{COLS - 1}"

    print(f"格子 {ROWS}×{COLS}（V = {len(network['nodes'])}, E = {len(network['roads'])}）、"
          f"{start} → {goal}、一般車両（1回だけの測定例）")
    for name, search in [("BFS", routing.bfs), ("Dijkstra", routing.dijkstra), ("A* (h=0)", routing.a_star)]:
        t0 = time.perf_counter()
        result = search(network, start, goal, "general")
        elapsed = time.perf_counter() - t0
        print(f"  {name:<9}: hops = {result['hops']}, cost = {result['cost']:.3f}, "
              f"expanded = {result['expanded']}, time = {elapsed:.6f} 秒")


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO 1：ノード数 V を変更する（格子の大きさ、またはランダムなグラフ）。
# TODO 2：道路数 E を変更する（斜めの道路を加える、道路をランダムに間引く など）。
# TODO 3：道路閉鎖率を変更する（disaster.apply_changes でランダムに選んだ道路を閉鎖。シードを記録）。
# TODO 4：一般車両と緊急車両を比較する（一部の道路を emergency_only にする）。
# TODO 5：BFS の処理時間を測定する。
# TODO 6：Dijkstra 法の処理時間を測定する。
# TODO 7：A* の処理時間を測定する（h = 0 と、euclidean_heuristic を実装した場合）。
# TODO 8：展開ノード数を比較する。
# TODO 9：総移動コストを比較する（A* と Dijkstra 法の最小移動コストが一致するか確認）。
# TODO 10：到達可能なケース（出発地・目的地の組）の割合を計算する。
# TODO 11：結果を表・グラフにまとめる。
# TODO 12：理論計算量と実測結果を比較する。
#
# 公平な比較の条件：
#   - 同じ道路ネットワーク・同じ災害シナリオ・同じ車両・同じ出発地と目的地・同じ移動コストを使う。
#   - 乱数を使う場合はシードを記録する。到達できない場合は別に集計する。
#   - BFS の「最小ホップ数」と、Dijkstra 法の「最小移動コスト」を混同しない。
#   - A* の最適性は、Dijkstra 法との比較で検証する。
#   - 測りたい処理だけを time.perf_counter() で挟む：
#       t0 = time.perf_counter()
#       routing.dijkstra(network, start, goal, "general")
#       elapsed = time.perf_counter() - t0
