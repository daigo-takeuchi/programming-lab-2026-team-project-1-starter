# D3：経路探索（BFS・Dijkstra 法・A*）
#
# どの関数も、指定した車両（"general" / "emergency"）が通行できる道路だけを使い、
# 同じ形の辞書を返す。
#   path     : 経路（ノードIDのリスト）。到達できなければ None
#   hops     : 通った道路の本数（到達できなければ None）
#   distance : 総距離（到達できなければ None）
#   cost     : 総移動コスト = 各道路の 距離 × コスト倍率 の合計（到達できなければ None）
#   expanded : 展開ノード数
#
# ■ 展開ノード数の定義（3方式で共通）
#   キューから取り出したノードのうち（優先度付きキューでは古い候補を除き）、
#   実際に隣接する道路を調べたノードの数。目的地を取り出した時点で探索を終えるので、
#   目的地そのものは数えない。出発地 = 目的地の場合は 0。

import heapq
import math

from textbook.fixed_queue import FixedQueue

from road_network import adjacency, find_road, road_cost, road_distance


def _check_nodes(network, start, goal):
    for node_id in (start, goal):
        if node_id not in network["nodes"]:
            raise ValueError(f"ノード {node_id!r} は存在しません")


def _build_result(network, path, expanded):
    """経路から、ホップ数・総距離・総移動コストを計算して結果の辞書を作る"""
    if path is None:
        return {"path": None, "hops": None, "distance": None, "cost": None, "expanded": expanded}
    edges = [find_road(network, path[i], path[i + 1]) for i in range(len(path) - 1)]
    return {
        "path": path,
        "hops": len(edges),
        "distance": sum(road_distance(road) for road in edges),
        "cost": sum(road_cost(road) for road in edges),
        "expanded": expanded,
    }


def _reconstruct(parent, goal):
    """parent（ノード → 1つ前のノード）を目的地からたどって経路を復元する"""
    path = [goal]
    while parent[path[-1]] is not None:
        path.append(parent[path[-1]])
    path.reverse()
    return path


# ------------------------------------------------------------
# BFS（幅優先探索）
# ------------------------------------------------------------

def bfs(network, start, goal, vehicle):
    """BFS：通る道路の本数（ホップ数）が最小の経路を求める

    キューには教科書 第4章の FixedQueue（リングバッファ）を使う。
    各ノードをキューに入れるのは「初めて見つけたとき」の1回だけなので、
    容量をノード数にすれば満杯にならない（満杯になっても、データが黙って消えずに例外になる）。

    ⚠️ BFS は道路の距離やコストを見ないので、総距離・総移動コストが最小になるとは限らない。
    """
    _check_nodes(network, start, goal)
    adj = adjacency(network, vehicle)
    queue = FixedQueue(len(network["nodes"]))
    parent = {start: None}          # 見つけたノード → 1つ前のノード（訪問済みの記録を兼ねる）
    expanded = 0

    queue.enque(start)
    while not queue.is_empty():
        node = queue.deque()
        if node == goal:
            return _build_result(network, _reconstruct(parent, goal), expanded)
        expanded += 1
        for other, _ in adj[node]:
            if other not in parent:
                parent[other] = node
                queue.enque(other)
    return _build_result(network, None, expanded)


# ------------------------------------------------------------
# Dijkstra 法
# ------------------------------------------------------------

def dijkstra(network, start, goal, vehicle):
    """Dijkstra 法：総移動コスト（距離 × コスト倍率）が最小の経路を求める

    優先度付きキューには Python 標準の heapq（二分ヒープ）を使う。
    同じノードの候補がキューに複数残ることがあるので、取り出したときに
    確定済みのノードや、記録より大きいコストの古い候補は読み飛ばす。
    移動コストは正の数（非負）であることが前提。
    """
    _check_nodes(network, start, goal)
    adj = adjacency(network, vehicle)
    best = {start: 0.0}             # 出発地からの、これまでに見つけた最小コスト
    parent = {start: None}
    done = set()                    # コストが確定したノード
    heap = [(0.0, start)]
    expanded = 0

    while heap:
        cost, node = heapq.heappop(heap)
        if node in done or cost > best[node]:
            continue                # 古い候補
        if node == goal:
            return _build_result(network, _reconstruct(parent, goal), expanded)
        done.add(node)
        expanded += 1
        for other, road in adj[node]:
            new_cost = cost + road_cost(road)
            if other not in best or new_cost < best[other]:
                best[other] = new_cost
                parent[other] = node
                heapq.heappush(heap, (new_cost, other))
    return _build_result(network, None, expanded)


# ------------------------------------------------------------
# A* 探索
# ------------------------------------------------------------

def zero_heuristic(network, node, goal):
    """h(n) = 0（このとき A* は Dijkstra 法と同じ探索になる）"""
    return 0.0


def euclidean_heuristic(network, node, goal):
    """TODO（学生の課題）：h(n) = node から goal までの直線距離（ユークリッド距離）

    ヒント：network["nodes"][node]["x"], ["y"] と math.hypot を使う。

    この h(n) が移動コストの下界（許容的）になるのは、次の条件がそろうときだけ：
      - すべての道路で、距離 ≥ 両端ノードの直線距離
        （road_network.euclidean_lower_bound_violations(network) が空）
      - すべての道路で、コスト倍率 ≥ 1
    コスト倍率が 1 未満の道路を許す場合は、許容性を考え直す必要がある。
    """
    raise NotImplementedError("ユークリッド距離のヒューリスティックは学生の課題です")


def a_star(network, start, goal, vehicle, heuristic=zero_heuristic):
    """A* 探索：f(n) = g(n) + h(n) が小さいノードから展開する

    g(n)：出発地から n までの累積移動コスト
    h(n)：n から目的地までの推定残余コスト（heuristic(network, n, goal)）

    h が許容的（実際の残りコストを超えない）かつ一貫的（道路 u–v について h(u) ≤ cost(u, v) + h(v)）
    なら、最小移動コストの経路が得られる。直線距離は、上の条件のもとで一貫的になる。
    """
    _check_nodes(network, start, goal)
    adj = adjacency(network, vehicle)
    best = {start: 0.0}             # g(n)
    parent = {start: None}
    done = set()
    heap = [(heuristic(network, start, goal), 0.0, start)]     # (f, g, ノード)
    expanded = 0

    while heap:
        f, g, node = heapq.heappop(heap)
        if node in done or g > best[node]:
            continue                # 古い候補
        if node == goal:
            return _build_result(network, _reconstruct(parent, goal), expanded)
        done.add(node)
        expanded += 1
        for other, road in adj[node]:
            new_g = g + road_cost(road)
            if other not in best or new_g < best[other]:
                best[other] = new_g
                parent[other] = node
                heapq.heappush(heap, (new_g + heuristic(network, other, goal), new_g, other))
    return _build_result(network, None, expanded)
