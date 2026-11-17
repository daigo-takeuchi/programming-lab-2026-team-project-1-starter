# C2：ネットワーク（重みなし・無向グラフ）の生成
#
# ■ グラフの表し方（隣接リスト）
#   {ノードID: [隣接するノードIDのリスト], ...} の辞書で表す。
#     graph = {0: [1, 2, 3], 1: [0], 2: [0], 3: [0]}   # 中心0のスター型
#
#   - 無向グラフなので、u の隣接リストに v があれば、v の隣接リストにも u がある（対称）
#   - 自己ループ（u -- u）や重複リンク（同じ u -- v が2本）は作らない
#   - リンクを持たない孤立ノードも、空のリストとして辞書に残す
#   - 隣接リストは番号の小さい順に並べる（DFS・BFS の訪問順序が毎回同じになる）

import random


def _empty_graph(n):
    """ノード 0〜n-1 だけがあり、リンクがないグラフ"""
    return {node: [] for node in range(n)}


def _add_edge(graph, u, v):
    """u -- v のリンクを追加する（自己ループ・重複リンクは追加しない）"""
    if u != v and v not in graph[u]:
        graph[u].append(v)
        graph[v].append(u)


def _sort_neighbors(graph):
    for node in graph:
        graph[node].sort()
    return graph


def star(n):
    """スター型：ノード0を中心に、他のすべてのノードを接続する"""
    graph = _empty_graph(n)
    for node in range(1, n):
        _add_edge(graph, 0, node)
    return _sort_neighbors(graph)


def ring(n):
    """リング型：隣どうしを接続し、最後のノードと最初のノードもつなぐ

    n = 2 のときはリンク1本（0 -- 1）だけになる（重複リンクは作らない）。
    """
    graph = _empty_graph(n)
    for node in range(n):
        _add_edge(graph, node, (node + 1) % n)
    return _sort_neighbors(graph)


def mesh(rows, cols):
    """メッシュ型（2次元格子）：上下左右の隣どうしを接続する

    ノードIDは左上から行優先で 0, 1, 2, ...（3×3 なら 0〜8）。
    全ノード間をつなぐ「完全グラフ（完全メッシュ）」とは異なる。
    """
    graph = _empty_graph(rows * cols)
    for r in range(rows):
        for c in range(cols):
            node = r * cols + c
            if c + 1 < cols:
                _add_edge(graph, node, node + 1)        # 右隣
            if r + 1 < rows:
                _add_edge(graph, node, node + cols)     # 下隣
    return _sort_neighbors(graph)


def random_graph(n, p, seed=None):
    """ランダム型：すべてのノードの組について、確率 p でリンクを作る

    seed を指定すると、毎回同じグラフが生成される（再現可能）。
    生成されたグラフが連結になるとは限らない（孤立ノードができることもある）。
    """
    rng = random.Random(seed)
    graph = _empty_graph(n)
    for u in range(n):
        for v in range(u + 1, n):
            if rng.random() < p:
                _add_edge(graph, u, v)
    return _sort_neighbors(graph)


def count_edges(graph):
    """リンク数（無向グラフなので、隣接リストの長さの合計の半分）"""
    return sum(len(neighbors) for neighbors in graph.values()) // 2


def degrees(graph):
    """各ノードの次数（接続しているリンクの数）を {ノード: 次数} で返す"""
    return {node: len(neighbors) for node, neighbors in graph.items()}


def format_graph(graph):
    """隣接リストを1行ずつの文字列にする"""
    return "\n".join(f"  {node}: {neighbors}" for node, neighbors in graph.items())
