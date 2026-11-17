# D2：2-opt によるルート改善（学生の実装課題）
#
# 2-opt は、ルートの中の2本の辺（移動区間）を取り除き、つなぎ方を変えることで、
# ルートを短くする局所探索アルゴリズムである。
# 訪問順のリストで見ると、「ルートの一部分を逆順にする」操作に当たる。
#
#   変更前：Depot → A → [B → C] → D → Depot
#   変更後：Depot → A → [C → B] → D → Depot     （B〜C の部分を反転）
#   取り除いた辺：A–B と C–D、新しくつないだ辺：A–C と B–D

from distance import route_distance


def reverse_segment(route, i, j):
    """route の i 番目から j 番目まで（両端を含む）を逆順にした新しいルートを返す

    元のリストは変更しない。0 ≤ i ≤ j < len(route) である必要がある。

    例：reverse_segment(["A", "B", "C", "D"], 1, 2) → ["A", "C", "B", "D"]
    """
    if not (0 <= i <= j < len(route)):
        raise ValueError(f"範囲が正しくありません（i = {i}, j = {j}, ルートの長さ = {len(route)}）")
    return list(route[:i]) + list(reversed(route[i:j + 1])) + list(route[j + 1:])


def two_opt(route, locations, depot):
    """TODO（Core 8 / Advanced A）：2-opt でルートを改善し、改善後のルートを返す

    引数
        route     : 初期ルート（配送先IDのリスト。例：最近傍法やランダム探索の結果）
        locations : 地点データ
        depot     : 配送拠点のID（総距離の計算に必要）

    実装の手順（README 8章）
        1. 初期ルートを用意する
        2. すべての (i, j)（i < j）について、reverse_segment(route, i, j) で候補ルートを作る
        3. 候補ルートの総距離を route_distance() で計算する
        4. 今のルートより短くなれば、そのルートに更新する
        5. どの候補でも短くならなくなるまで、2〜4 を繰り返す

    戻り値の形は solvers.py の関数にそろえるとよい
        {"route": ..., "distance": ..., "evaluated": 総距離を計算した候補の数}
    """
    raise NotImplementedError("2-opt は学生の課題です")
