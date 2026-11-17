# C2：障害の適用と接続性の評価
#
# 「障害」「攻撃」は、グラフのノードやリンクを取り除く抽象的なモデルである。
# 実際のネットワークへの攻撃や通信妨害を再現するものではない。
#
# どの関数も元のグラフを変更せず、必要なら新しいグラフを返す。

from textbook.fixed_queue import FixedQueue


def remove_node(graph, node):
    """ノード障害：node と、node につながるリンクを取り除いた新しいグラフを返す"""
    return {
        u: [v for v in neighbors if v != node]
        for u, neighbors in graph.items()
        if u != node
    }


def remove_edge(graph, u, v):
    """リンク障害：u -- v のリンクを（両方向とも）取り除いた新しいグラフを返す

    ノードは残る。そのリンクがなければ、元と同じ内容のコピーを返す。
    """
    new_graph = {node: list(neighbors) for node, neighbors in graph.items()}
    if u in new_graph and v in new_graph[u]:
        new_graph[u].remove(v)
        new_graph[v].remove(u)
    return new_graph


def connected_components(graph):
    """連結成分（互いに行き来できるノードの集まり）のリストを返す

    まだどの成分にも入っていないノードから BFS を行い、到達できたノードを1つの成分とする。
    traversal.bfs() と同じ手順だが、成分ごとに容量 V のキューを作り直すと
    孤立ノードが多いときに O(V²) かかるため、1つのキューを使い回している。
    （各ノードがキューに入るのは全体で1回だけなので、容量 V で足りる）
    """
    components = []
    seen = set()
    queue = FixedQueue(max(len(graph), 1))
    for start in graph:
        if start in seen:
            continue
        component = []
        seen.add(start)
        queue.enque(start)
        while not queue.is_empty():
            node = queue.deque()
            component.append(node)
            for neighbor in graph[node]:
                if neighbor not in seen:
                    seen.add(neighbor)
                    queue.enque(neighbor)
        components.append(component)
    return components


def is_connected(graph):
    """ネットワーク全体が連結しているか（連結成分がちょうど1つか）

    ノードが1つもないグラフは、連結とはみなさない（False）。
    """
    return len(connected_components(graph)) == 1


def largest_component_size(graph):
    """最大連結成分のノード数（ノードがなければ 0）"""
    return max((len(c) for c in connected_components(graph)), default=0)


def largest_component_ratio(graph, total_nodes):
    """最大連結成分の割合 = 最大連結成分のノード数 / total_nodes

    分母 total_nodes は呼び出し側が決める。
      - 障害前のノード数を分母にする → 失われたノードの影響も含めて評価できる
      - 障害後に残ったノード数（len(graph)）を分母にする → 残ったノードどうしのつながりだけを評価する
    どちらを使ったかを、必ず明記すること。分母が 0 のときは 0.0 を返す。
    """
    if total_nodes == 0:
        return 0.0
    return largest_component_size(graph) / total_nodes


# ------------------------------------------------------------
# 学生が取り組む課題（Advanced Research）
# ------------------------------------------------------------
# TODO（Advanced A）：複数のノード・リンクをランダムに取り除く関数を作る（乱数シードを指定できるように）。
# TODO（Advanced A）：次数の高いノードから順に取り除く（標的型障害の抽象モデル）。
# TODO（Advanced C）：BFS を使って平均最短経路長・ネットワーク効率を計算する。
# TODO（Advanced D）：関節点・橋を調べる（まずは「1つずつ取り除いて is_connected を調べる」素朴な方法から）。
