# G2：国家間ネットワーク（無向グラフ）と、グラフ探索（DFS・BFS）
#
# ・ノード = 国家、エッジ = 国家ペアの関係。エッジは (小さい ID, 大きい ID) のタプルで表す。
# ・ネットワークの「つながり」は、関係が存在すること（対戦相手であること）を表すだけで、
#   政治的な協調関係そのものではない。協調関係は、エッジの状態（Cooperation など）で別に表す。
#
# ■ データ構造
#   隣接リスト：{ノード: [隣のノード, ...]}       メモリ O(V + E)、隣を列挙 O(次数)、辺の有無 O(次数)
#   隣接行列  ：V × V の 0/1 の表                 メモリ O(V²)、    隣を列挙 O(V)、   辺の有無 O(1)
#
# ■ グラフ探索（どちらも O(V + E)）
#   DFS：教科書の FixedStack（第4章）を使うスタック版と、再帰版（第5章の再帰の考え方）
#   BFS：教科書の FixedQueue（第4章）を使う。無向・重みなしのグラフで、辺の数が最小の経路（最短経路）が求まる

import random

from textbook.fixed_stack import FixedStack
from textbook.fixed_queue import FixedQueue

NETWORK_TYPES = ("line", "ring", "star", "random")


# ------------------------------------------------------------
# ネットワークの生成
# ------------------------------------------------------------
def edge(u, v):
    if u == v:
        raise ValueError(f"自己ループ ({u}, {v}) は使いません")
    return (u, v) if u < v else (v, u)


def validate_edges(nodes, edges):
    ns = set(nodes)
    seen = set()
    for u, v in edges:
        if u not in ns or v not in ns:
            raise ValueError(f"エッジ ({u}, {v}) のノードがありません")
        e = edge(u, v)
        if e in seen:
            raise ValueError(f"エッジ {e} が重複しています")
        seen.add(e)
    return True


def line_network(nodes):
    return [edge(nodes[i], nodes[i + 1]) for i in range(len(nodes) - 1)]


def ring_network(nodes):
    if len(nodes) < 3:
        return line_network(nodes)
    return line_network(nodes) + [edge(nodes[-1], nodes[0])]


def star_network(nodes, center=None):
    if not nodes:
        return []
    center = nodes[0] if center is None else center
    return [edge(center, v) for v in nodes if v != center]


def random_network(nodes, p=0.4, seed=0):
    """各ペアを確率 p でつなぐランダムネットワーク（Erdős–Rényi 型）。連結とは限らない"""
    rng = random.Random(seed)
    out = []
    for i in range(len(nodes)):
        for j in range(i + 1, len(nodes)):
            if rng.random() < p:
                out.append(edge(nodes[i], nodes[j]))
    return out


def make_network(kind, nodes, p=0.4, seed=0):
    if kind == "line":
        edges = line_network(nodes)
    elif kind == "ring":
        edges = ring_network(nodes)
    elif kind == "star":
        edges = star_network(nodes)
    elif kind == "random":
        edges = random_network(nodes, p, seed)
    else:
        raise ValueError(f"ネットワーク {kind!r} は {NETWORK_TYPES} のどれかにしてください")
    return sorted(edges)


def node_names(n):
    """n 個のノード名（A, B, ..., Z, N26, N27, ...）"""
    return [chr(ord("A") + i) if i < 26 else f"N{i}" for i in range(n)]


# ------------------------------------------------------------
# 隣接リスト・隣接行列
# ------------------------------------------------------------
def adjacency_list(nodes, edges):
    adj = {v: [] for v in nodes}
    for u, v in edges:
        adj[u].append(v)
        adj[v].append(u)
    for v in adj:
        adj[v].sort()
    return adj


def adjacency_matrix(nodes, edges):
    """(ノードの並び, V × V の 0/1 行列)"""
    index = {v: i for i, v in enumerate(nodes)}
    mat = [[0] * len(nodes) for _ in nodes]
    for u, v in edges:
        mat[index[u]][index[v]] = mat[index[v]][index[u]] = 1
    return list(nodes), mat


def neighbors_from_matrix(order, mat, v):
    """隣接行列から隣のノードを列挙する（O(V)：行を全部見る）"""
    i = order.index(v)
    return [order[j] for j in range(len(order)) if mat[i][j]]


def memory_estimate(nodes, edges):
    """格納する値の数の概算：隣接リスト V + 2E、隣接行列 V²"""
    return {"adjacency_list": len(nodes) + 2 * len(edges), "adjacency_matrix": len(nodes) ** 2}


# ------------------------------------------------------------
# DFS・BFS
# ------------------------------------------------------------
def dfs(adj, start):
    """深さ優先探索（スタック版）。隣は ID の小さい順に訪問する

    戻り値：{"order": 訪問順, "visited": 訪問したノード数, "pushes": push の回数,
             "max_frontier": スタックの最大の長さ, "parent": 親}
    """
    if start not in adj:
        raise KeyError(f"ノード {start!r} がありません")
    capacity = 1 + sum(len(ns) for ns in adj.values())       # push は最大 1 + 2E 回
    stack = FixedStack(capacity)
    stack.push((start, None))
    seen, order, parent = set(), [], {}
    pushes, max_frontier = 1, 1
    while not stack.is_empty():
        v, p = stack.pop()
        if v in seen:
            continue
        seen.add(v)
        order.append(v)
        parent[v] = p
        for w in reversed(adj[v]):                            # 逆順に積むと、小さい ID から取り出される
            if w not in seen:
                stack.push((w, v))
                pushes += 1
        max_frontier = max(max_frontier, len(stack))
    return {"order": order, "visited": len(order), "pushes": pushes, "max_frontier": max_frontier, "parent": parent}


def dfs_recursive(adj, start):
    """深さ優先探索（再帰版）。訪問順はスタック版と同じ。深いグラフでは Python の再帰の上限（約 1,000）に注意"""
    if start not in adj:
        raise KeyError(f"ノード {start!r} がありません")
    order, parent = [], {start: None}
    seen = set()
    depth = {"max": 0}

    def visit(v, d):
        seen.add(v)
        order.append(v)
        depth["max"] = max(depth["max"], d)
        for w in adj[v]:
            if w not in seen:
                parent[w] = v
                visit(w, d + 1)

    visit(start, 1)
    return {"order": order, "visited": len(order), "max_depth": depth["max"], "parent": parent}


def bfs(adj, start):
    """幅優先探索（キュー版）。隣は ID の小さい順。dist = 辺の数で数えた距離（最短）

    戻り値：{"order", "visited", "enqueues", "max_frontier": キューの最大の長さ, "dist", "parent"}
    """
    if start not in adj:
        raise KeyError(f"ノード {start!r} がありません")
    queue = FixedQueue(max(1, len(adj)))                     # 各ノードは 1 回だけキューに入る
    queue.enque(start)
    dist, parent, order = {start: 0}, {start: None}, []
    enqueues, max_frontier = 1, 1
    while not queue.is_empty():
        v = queue.deque()
        order.append(v)
        for w in adj[v]:
            if w not in dist:
                dist[w] = dist[v] + 1
                parent[w] = v
                queue.enque(w)
                enqueues += 1
        max_frontier = max(max_frontier, len(queue))
    return {"order": order, "visited": len(order), "enqueues": enqueues, "max_frontier": max_frontier,
            "dist": dist, "parent": parent}


def path_to(parent, target):
    """parent をたどって start → target の経路を作る（到達できなければ None）"""
    if target not in parent:
        return None
    path = []
    v = target
    while v is not None:
        path.append(v)
        v = parent[v]
    return path[::-1]


def reachable(adj, start, target, method="bfs"):
    result = bfs(adj, start) if method == "bfs" else dfs(adj, start)
    return target in result["parent"]


# ------------------------------------------------------------
# 評価指標
# ------------------------------------------------------------
def connected_components(adj):
    """連結成分のリスト（各成分はソート済み。最小のノードの順）。BFS をくり返す"""
    seen, comps = set(), []
    for v in sorted(adj):
        if v not in seen:
            comp = bfs(adj, v)["order"]
            seen.update(comp)
            comps.append(sorted(comp))
    return comps


def network_metrics(nodes, edges, states=None):
    """ノード数・エッジ数・平均次数・連結成分数・最大連結成分のサイズ・協調エッジの割合

    states = {エッジ: 状態} を与えると、協調エッジ（状態が Cooperation）の割合と、
    協調エッジだけでできたグラフ（協調ネットワーク）の連結成分も計算する。
    """
    adj = adjacency_list(nodes, edges)
    comps = connected_components(adj) if nodes else []
    out = {"nodes": len(nodes), "edges": len(edges),
           "average_degree": 2 * len(edges) / len(nodes) if nodes else 0.0,
           "components": len(comps), "largest_component": max((len(c) for c in comps), default=0)}
    if states is not None:
        coop = [e for e in edges if states.get(e) == "Cooperation"]
        cadj = adjacency_list(nodes, coop)
        ccomps = connected_components(cadj) if nodes else []
        out.update({"cooperation_edge_ratio": len(coop) / len(edges) if edges else None,
                    "cooperation_components": len(ccomps),
                    "cooperation_largest_component": max((len(c) for c in ccomps), default=0)})
    return out


# TODO 1：ノード数を増やし（10・100・1,000）、DFS と BFS の実行時間・最大の長さを比べる（Notebook 04）。
# TODO 2：協調・非協調に応じてエッジが増えたり消えたりするモデルにする（Advanced D）。
# TODO 3：隣接行列版の BFS を作り、隣接リスト版と実行時間を比べる。
