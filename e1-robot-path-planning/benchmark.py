# E1：性能比較実験の入口
#
# ここにあるのは「障害物のない W × H のマップを作り、DFS・BFS・A* を1回ずつ測定する例」だけ。
# W・H・障害物の割合を変えた繰り返し実験、到達可能率の集計、グラフ化は、学生が実装する（下の TODO）。
#
# ■ 公平な比較の条件
#   ・同じマップ（同じ障害物配置）、同じスタート・ゴール、同じ移動規則（4方向・コスト1）を使う
#   ・経路長の定義（移動回数）をそろえる
#   ・探索時間と経路長は分けて評価する（速いが遠回り、ということがある）
#   ・探索時間は複数回測定する（1回だけの値はぶれる）
#   ・乱数を使う場合は、乱数シードを記録する
#   ・到達不能なマップは別に集計する（経路長の平均に混ぜない）

import time

from grid_map import count_edges, parse_map, passable_cells
from search import ALGORITHMS


def make_open_map(width, height):
    """障害物のない width × height のマップ（左上がスタート、右下がゴール）の文字列を作る"""
    if width < 2 and height < 2:
        raise ValueError("スタートとゴールを別のセルに置くには、2セル以上必要です")
    rows = [["."] * width for _ in range(height)]
    rows[0][0] = "S"
    rows[height - 1][width - 1] = "G"
    return "\n".join("".join(row) for row in rows)


def measure(search_function, grid_map):
    """探索を1回実行し、(結果, 探索時間[秒]) を返す"""
    t0 = time.perf_counter()
    result = search_function(grid_map)
    return result, time.perf_counter() - t0


if __name__ == "__main__":
    W, H = 30, 30
    grid_map = parse_map(make_open_map(W, H))
    print(f"障害物なし {W}×{H}（V = {len(passable_cells(grid_map))}, E = {count_edges(grid_map)}）、"
          f"{grid_map.start} → {grid_map.goal}（1回だけの測定例）")
    for name, search_function in ALGORITHMS:
        result, seconds = measure(search_function, grid_map)
        print(f"  {name:<4}: length = {result['length']}, expanded = {result['expanded']}, "
              f"time = {seconds:.6f} 秒")

# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：マップの幅 W を変更する。
# TODO 2：マップの高さ H を変更する。
# TODO 3：障害物の割合を変更する（random.Random(seed) でランダムに障害物を置く。シードを記録する。
#         S・G には障害物を置かない）。
# TODO 4：DFS の探索時間を測定する（複数回測定して平均・中央値を求める）。
# TODO 5：BFS の探索時間を測定する。
# TODO 6：A* の探索時間を測定する。
# TODO 7：展開ノード数を比較する。
# TODO 8：経路長を比較する（BFS と A* の経路長が一致するか、DFS がどれだけ長くなるか）。
# TODO 9：到達可能なマップの割合を計算する（到達不能なマップは別に集計する）。
# TODO 10：結果を表・グラフにまとめる。
# TODO 11：理論計算量 O(V + E) と実測結果を比較する（V・E を横軸にしたグラフなど）。
