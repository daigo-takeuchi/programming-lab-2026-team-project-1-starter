# C2：サイバー攻撃・障害に強いネットワーク構造の設計 — starter code
#
# 4種類の小さなネットワークを作り、DFS・BFS で探索してから、
# 1つのノードまたはリンクを取り除いたときの連結性を比べる。
# （「障害」はグラフからノード・リンクを取り除く抽象的なモデルである）

import network
import resilience
import traversal

RANDOM_SEED = 6         # ランダム型の乱数シード（6 では非連結になる。変えて試してみよう）
RANDOM_P = 0.3          # ランダム型のリンク生成確率


def show_network(name, graph):
    """ネットワークの情報と、DFS・BFS の結果を表示する"""
    print(f"--- {name} ---")
    print("ノード数:", len(graph), " リンク数:", network.count_edges(graph))
    print("隣接リスト:")
    print(network.format_graph(graph))
    order, hops = traversal.bfs(graph, 0)
    print("DFS（ノード0から）:", traversal.dfs(graph, 0))
    print("BFS（ノード0から）:", order)
    print("BFS 最短ホップ数  :", hops)
    components = resilience.connected_components(graph)
    print("連結か:", resilience.is_connected(graph),
          " 連結成分数:", len(components),
          " 最大連結成分サイズ:", resilience.largest_component_size(graph))
    print()


print("=== C2：サイバー攻撃・障害に強いネットワーク構造の設計 ===")
print()

networks = [
    ("スター型（6ノード）", network.star(6)),
    ("リング型（6ノード）", network.ring(6)),
    (f"ランダム型（8ノード, p={RANDOM_P}, seed={RANDOM_SEED}）",
     network.random_graph(8, RANDOM_P, seed=RANDOM_SEED)),
    ("メッシュ型（3×3）", network.mesh(3, 3)),
]

for name, graph in networks:
    show_network(name, graph)

# ------------------------------------------------------------
# 単一障害の比較
# ------------------------------------------------------------
star = network.star(6)
ring = network.ring(6)
mesh = network.mesh(3, 3)

failures = [
    ("スター型", "中心ノード0の障害", star, resilience.remove_node(star, 0)),
    ("スター型", "末端ノード5の障害", star, resilience.remove_node(star, 5)),
    ("リング型", "リンク0--1の障害", ring, resilience.remove_edge(ring, 0, 1)),
    ("メッシュ型", "リンク4--5の障害", mesh, resilience.remove_edge(mesh, 4, 5)),
]

print("=== 単一障害の比較 ===")
print("割合A：最大連結成分のノード数 / 障害前のノード数")
print("割合B：最大連結成分のノード数 / 障害後に残ったノード数")
print()
for kind, label, before, after in failures:
    print(f"{kind}：{label}")
    print("  障害前の連結性:", "連結" if resilience.is_connected(before) else "非連結")
    print("  障害後の連結性:", "連結" if resilience.is_connected(after) else "非連結")
    print("  連結成分数    :", len(resilience.connected_components(after)))
    print("  最大連結成分  :", resilience.largest_component_size(after))
    print(f"  割合A = {resilience.largest_component_ratio(after, len(before)):.2f}"
          f"  割合B = {resilience.largest_component_ratio(after, len(after)):.2f}")


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：ノード数を増やしたネットワークで、同じ比較を行う。
# TODO 2：すべてのノード（またはリンク）を1つずつ取り除いて、連結性が失われるものを数える。
# TODO 3：RANDOM_SEED や RANDOM_P を変えて、ランダム型の連結性がどう変わるか調べる。
# TODO 4：benchmark.py を使って、DFS・BFS の処理時間を測定する。
