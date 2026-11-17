# D3：東京圏での大地震発生時の交通規制・道路閉鎖を考慮した経路探索 — starter code
#
# ⚠️ 道路の接続・距離・閉鎖箇所・通行規制はすべて架空の設定です。
#    実際の災害時の通行可否や避難経路を示すものではありません。
#
# Demo A：地震発生前に、BFS・Dijkstra 法・A* で経路を探す
# Demo B：道路閉鎖のシナリオで、一般車両と緊急車両の経路を探す
# Demo C：交通規制（緊急車両のみ通行可能）・混雑のシナリオで、経路を比べる

from pathlib import Path

import disaster
import routing
from road_network import load_network, node_name

DATA_FILE = Path(__file__).parent / "data" / "sample_tokyo_network.json"
START = "SJK"       # Shinjuku
GOAL = "KOT"        # Koto

ALGORITHMS = [("BFS", routing.bfs), ("Dijkstra", routing.dijkstra), ("A* (h=0)", routing.a_star)]


def route_text(network, result):
    if result["path"] is None:
        return "到達できません（通行できる経路がありません）"
    return " → ".join(node_name(network, n) for n in result["path"])


def show_table(network, vehicle):
    """3つのアルゴリズムの結果を表示し、Dijkstra 法の結果を返す"""
    print(f"{'Algorithm':<10}{'Hops':>6}{'Distance':>10}{'Cost':>8}{'Expanded':>10}   Route")
    results = {}
    for name, search in ALGORITHMS:
        r = search(network, START, GOAL, vehicle)
        results[name] = r
        if r["path"] is None:
            print(f"{name:<10}{'-':>6}{'-':>10}{'-':>8}{r['expanded']:>10}   {route_text(network, r)}")
        else:
            print(f"{name:<10}{r['hops']:>6}{r['distance']:>10.1f}{r['cost']:>8.1f}{r['expanded']:>10}   "
                  f"{route_text(network, r)}")
    return results["Dijkstra"]


base = load_network(DATA_FILE)

print("D3: Earthquake Route Planning")
print("（架空の道路ネットワークです。実際の通行可否・避難経路を示すものではありません）")
print()
print("Network:")
print("  Nodes:", len(base["nodes"]))
print("  Roads:", len(base["roads"]))
print(f"Start: {node_name(base, START)}   Goal: {node_name(base, GOAL)}")

# ------------------------------------------------------------
# Demo A：地震発生前
# ------------------------------------------------------------
print()
print("=== Demo A ===")
print("Scenario:", disaster.SCENARIOS["before"]["title"])
print("Vehicle: General")
before = show_table(disaster.apply_scenario(base, "before"), "general")
print("※ BFS は道路本数（ホップ数）が最小の経路、Dijkstra 法・A* は移動コストが最小の経路を求める。")

# ------------------------------------------------------------
# Demo B・C：地震発生後
# ------------------------------------------------------------
for demo, name in [("B", "closure"), ("C", "regulation"), ("C", "congestion")]:
    scenario = disaster.SCENARIOS[name]
    network = disaster.apply_scenario(base, name)
    print()
    print(f"=== Demo {demo} ===")
    print("Scenario:", scenario["title"])
    for u, v in scenario["closed"]:
        print(f"  閉鎖：{node_name(base, u)}–{node_name(base, v)}")
    for u, v in scenario["emergency_only"]:
        print(f"  緊急車両のみ：{node_name(base, u)}–{node_name(base, v)}")
    for (u, v), m in scenario["cost_multipliers"].items():
        print(f"  コスト × {m}：{node_name(base, u)}–{node_name(base, v)}")

    for vehicle in ("general", "emergency"):
        print(f"Vehicle: {vehicle.capitalize()}")
        result = show_table(network, vehicle)
        if result["path"] is not None and before["path"] is not None:
            print(f"  地震前（一般車両・Dijkstra）との比較：移動コスト {before['cost']:.1f} → {result['cost']:.1f}"
                  f"（{result['cost'] - before['cost']:+.1f}）")

print()
print("Student TODO：routing.euclidean_heuristic() を実装し、A* の展開ノード数を Dijkstra 法と比べよう。")


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：euclidean_heuristic を実装し、routing.a_star(..., heuristic=routing.euclidean_heuristic) で試す。
# TODO 2：A* と Dijkstra 法の最小移動コストが一致することを確かめる。
# TODO 3：START・GOAL を変えて、地震前後の経路の変化を調べる。
# TODO 4：benchmark.py を使って、ノード数・道路閉鎖率を変えたときの処理時間を測る。
