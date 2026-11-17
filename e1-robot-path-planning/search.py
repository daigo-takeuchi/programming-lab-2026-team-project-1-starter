# E1：経路探索アルゴリズム（DFS・BFS・A*）
#
# どの関数も同じ形の辞書を返す。
#   found    : ゴールに到達できたか（True / False）
#   path     : スタートからゴールまでのセル座標のリスト。到達できなければ None
#   length   : 経路長 = 移動回数 = len(path) - 1。到達できなければ None
#              （例：5セルからなる経路の経路長は 4）
#   expanded : 展開ノード数
#   order    : 探索順序（展開したセルを、展開した順に並べたリスト）
#
# ■ 展開ノード数の定義（3方式で共通）
#   スタック・キュー・優先度付きキューから取り出したセルのうち、
#   実際に隣接セルを調べたセルの数。同じセルは2回以上展開しない。
#   ゴール判定は「取り出した直後・隣接セルを調べる前」に行う。
#   そのため、ゴールを取り出した時点で探索を終え、ゴール自身は展開ノード数にも
#   探索順序にも含めない。スタート = ゴールの場合、展開ノード数は 0。
#
# 隣接セルは grid_map.neighbors() が返す「上・右・下・左」の順に調べる。

import heapq

from textbook.fixed_queue import FixedQueue
from textbook.fixed_stack import FixedStack

from grid_map import neighbors, passable_cells


def _result(path, expanded, order):
    return {
        "found": path is not None,
        "path": path,
        "length": None if path is None else len(path) - 1,
        "expanded": expanded,
        "order": order,
    }


def _reconstruct(parent, goal):
    """parent（セル → 1つ前のセル）をゴールからたどり、スタート → ゴールの経路を作る"""
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return path


# ------------------------------------------------------------
# DFS（深さ優先探索）
# ------------------------------------------------------------

def dfs(grid_map):
    """DFS：スタックを使い、行けるところまで深く進んでから引き返す

    到達可能なら必ず経路を見つけるが、最短経路とは限らない。

    スタックには教科書 第4章の FixedStack を使う。
    ・スタックの要素は (セル, 1つ前のセル)。
    ・訪問済みの印は「取り出したとき」に付ける。同じセルが複数回 push されることがあるが、
      2回目以降に取り出したものは読み飛ばす（展開しない）。
    ・push の回数は「スタートの1回 + 展開した各セルから最大4回」なので、
      容量 1 + 4V で満杯（FixedStack.Full）にならない。
    ・スタックは後から入れたものを先に取り出すので、上・右・下・左の順に調べたいときは
      逆順（左・下・右・上）に push する。
    """
    start, goal = grid_map.start, grid_map.goal
    stack = FixedStack(1 + 4 * len(passable_cells(grid_map)))
    stack.push((start, None))
    parent = {}       # 訪問済みセル → 1つ前のセル（訪問済みセルの記録も兼ねる）
    order = []

    while not stack.is_empty():
        cell, prev = stack.pop()
        if cell in parent:            # すでに訪問済み（古い要素）
            continue
        parent[cell] = prev
        if cell == goal:
            return _result(_reconstruct(parent, goal), len(order), order)
        order.append(cell)            # 展開する
        for nxt in reversed(neighbors(grid_map, cell)):
            if nxt not in parent:
                stack.push((nxt, cell))

    return _result(None, len(order), order)


# ------------------------------------------------------------
# BFS（幅優先探索）
# ------------------------------------------------------------

def bfs(grid_map):
    """BFS：FIFO キューを使い、スタートに近いセルから順に調べる

    4方向・移動コスト1のグリッドでは、最短経路（移動回数が最小）を求める。

    キューには教科書 第4章の FixedQueue（リングバッファ）を使う。
    ・訪問済みの印は「キューに入れたとき」に付けるので、各セルは最大1回しか入らない。
      容量を通行可能セル数 V にすれば満杯（FixedQueue.Full）にならない。
    """
    start, goal = grid_map.start, grid_map.goal
    queue = FixedQueue(len(passable_cells(grid_map)))
    queue.enque(start)
    parent = {start: None}   # 発見済みセル → 1つ前のセル
    order = []

    while not queue.is_empty():
        cell = queue.deque()
        if cell == goal:
            return _result(_reconstruct(parent, goal), len(order), order)
        order.append(cell)   # 展開する
        for nxt in neighbors(grid_map, cell):
            if nxt not in parent:
                parent[nxt] = cell
                queue.enque(nxt)

    return _result(None, len(order), order)


# ------------------------------------------------------------
# A*（エースター）探索
# ------------------------------------------------------------

def manhattan_distance(cell, goal):
    """マンハッタン距離 h(n) = |row_n - row_goal| + |col_n - col_goal|

    4方向・移動コスト1では、実際の残り移動回数を超えない（許容的）。
    また1回の移動で h は最大1しか変わらない（整合的）。
    """
    return abs(cell[0] - goal[0]) + abs(cell[1] - goal[1])


# TODO（Advanced B）：h(n) = 0、ユークリッド距離などのヒューリスティックを実装し、
#   a_star(grid_map, heuristic=...) に渡して展開ノード数・探索時間を比較する。


def a_star(grid_map, heuristic=manhattan_distance):
    """A*：f(n) = g(n) + h(n) が最小のセルから順に展開する

    g(n)：スタートから n までの移動コスト（Core Research では移動回数）
    h(n)：n からゴールまでの推定コスト（heuristic(n, goal)）

    優先度付きキューには Python 標準の heapq を使う（教科書に優先度付きキューのクラスはない）。
    ・要素は (f, h, 追加順の番号, セル)。f が同じなら h が小さい（ゴールに近い）方、
      それも同じなら先に追加した方を先に取り出す（同点時の順序を固定して再現性を保つ）。
    ・より短い経路が見つかったときは新しい要素を追加する（heapq は優先度を直接変更できない）。
      古い要素は、取り出したときに「展開済み」なら読み飛ばす。
    ・ヒューリスティックが整合的なら、展開済みのセルの g は確定しているので再展開しない。
    """
    start, goal = grid_map.start, grid_map.goal
    g = {start: 0}           # セル → 現時点で分かっている最小の移動コスト
    parent = {start: None}
    closed = set()           # 展開済みセル
    order = []
    counter = 0
    h0 = heuristic(start, goal)
    heap = [(h0, h0, counter, start)]

    while heap:
        _f, _h, _n, cell = heapq.heappop(heap)
        if cell in closed:   # 古い要素
            continue
        if cell == goal:
            return _result(_reconstruct(parent, goal), len(order), order)
        closed.add(cell)
        order.append(cell)   # 展開する
        for nxt in neighbors(grid_map, cell):
            new_g = g[cell] + 1          # Core Research：すべての移動コストは1
            if nxt not in closed and new_g < g.get(nxt, float("inf")):
                g[nxt] = new_g
                parent[nxt] = cell
                h = heuristic(nxt, goal)
                counter += 1
                heapq.heappush(heap, (new_g + h, h, counter, nxt))

    return _result(None, len(order), order)


ALGORITHMS = [("DFS", dfs), ("BFS", bfs), ("A*", a_star)]
