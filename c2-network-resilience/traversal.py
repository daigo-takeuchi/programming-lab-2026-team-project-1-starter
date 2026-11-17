# C2：深さ優先探索（DFS）と幅優先探索（BFS）
#
# どちらも教科書 第4章の固定長スタック・固定長キューを使う。
#   FixedStack / FixedQueue は、満杯で push / enque すると例外を送出する（データは黙って消えない）。
#   ここでは、満杯にならない容量を計算してから作っている（各関数のコメント参照）。
#
#   教科書の Stack / Queue（collections.deque(maxlen) 版）は、満杯のとき古いデータを
#   黙って捨てるため、未処理のノードが失われる危険がある。探索には使わない。

from textbook.fixed_queue import FixedQueue
from textbook.fixed_stack import FixedStack

import network


def dfs(graph, start):
    """深さ優先探索：start から到達できるノードを、訪問した順のリストで返す

    1. 開始ノードをスタックに積む。
    2. スタックからノードを取り出し、未訪問なら訪問済みにする。
    3. その隣接ノードのうち未訪問のものをスタックに積む。
       （番号の小さい隣接ノードから先に訪問するよう、逆順に積む）
    4. スタックが空になるまで 2〜3 を繰り返す。
       （進めなくなったら、スタックに残っている「前に見つけたノード」に戻る）

    スタックの容量：push は「開始ノードの1回」＋「訪問したノードの隣接ノードの数」なので、
    合計で 1 + 2E 回以下（E はリンク数）。容量を 2E + 1 にすれば満杯にならない。
    """
    if start not in graph:
        return []

    stack = FixedStack(2 * network.count_edges(graph) + 1)
    visited = set()
    order = []

    stack.push(start)
    while not stack.is_empty():
        node = stack.pop()
        if node in visited:
            continue
        visited.add(node)
        order.append(node)
        for neighbor in reversed(graph[node]):
            if neighbor not in visited:
                stack.push(neighbor)
    return order


def bfs(graph, start):
    """幅優先探索：start から到達できるノードの訪問順と、最短ホップ数を返す

    戻り値：(order, hops)
        order : 訪問した順のノードのリスト
        hops  : {ノード: start からの最短ホップ数（リンクの数）}

    1. 開始ノードをキューに入れる（ホップ数 0）。
    2. キューからノードを取り出す。
    3. 未訪問の隣接ノードを、ホップ数 +1 としてキューに入れる。
    4. キューが空になるまで 2〜3 を繰り返す。

    キューの容量：各ノードは「初めて見つけたとき」の1回だけキューに入るので、
    容量をノード数 V にすれば満杯にならない。
    """
    if start not in graph:
        return [], {}

    queue = FixedQueue(len(graph))
    hops = {start: 0}           # 見つけたノードとホップ数（訪問済みの記録を兼ねる）
    order = []

    queue.enque(start)
    while not queue.is_empty():
        node = queue.deque()
        order.append(node)
        for neighbor in graph[node]:
            if neighbor not in hops:
                hops[neighbor] = hops[node] + 1
                queue.enque(neighbor)
    return order, hops


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO：再帰を使った DFS（dfs_recursive）を書き、上の dfs() と訪問順序を比べる。
#       （教科書 第5章の再帰的アルゴリズムを参考に。ノード数が多いと
#         Python の再帰の深さの上限（通常 1000 程度）に達することにも注意）
# TODO：BFS で、最短経路そのもの（通るノードの列）を求める（親ノードを記録する）。
