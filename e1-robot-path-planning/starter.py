# E1：自律移動ロボットの経路探索 ―― DFS・BFS・A* の実行例
#
# 3つのサンプルマップで DFS・BFS・A* を実行し、
# 経路長・展開ノード数・探索時間を表にして、探索結果を ASCII マップで表示する。
# （探索時間は1回だけの測定なので、実行するたびに少し変わる。比較実験は benchmark.py で行う）

import os
import time

from grid_map import count_edges, load_map, passable_cells
from search import ALGORITHMS
from visualization import render, render_result

DATA_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
MAP_FILES = ["simple_map.txt", "maze_map.txt", "blocked_map.txt"]


def run_timed(search_function, grid_map):
    """探索を1回実行し、(結果, 探索時間[ms]) を返す"""
    t0 = time.perf_counter()
    result = search_function(grid_map)
    elapsed_ms = (time.perf_counter() - t0) * 1000
    return result, elapsed_ms


def show_map(map_file):
    grid_map = load_map(os.path.join(DATA_DIR, map_file))
    print(f"Map: {map_file}")
    print(f"Map Size: {grid_map.width} x {grid_map.height}"
          f"   (V = {len(passable_cells(grid_map))} 通行可能セル, E = {count_edges(grid_map)} 隣接関係)")
    print(f"Start: {grid_map.start}   Goal: {grid_map.goal}")
    print()
    print(render(grid_map))
    print()

    results = {}
    print(f"{'Algorithm':<12}{'Path Length':>12}{'Path Cells':>12}{'Expanded Nodes':>16}{'Time (ms)':>12}")
    for name, search_function in ALGORITHMS:
        result, elapsed_ms = run_timed(search_function, grid_map)
        results[name] = result
        if result["found"]:
            length, cells = str(result["length"]), str(len(result["path"]))
        else:
            length, cells = "unreachable", "-"
        print(f"{name:<12}{length:>12}{cells:>12}{result['expanded']:>16}{elapsed_ms:>12.3f}")
    print()

    print("Shortest Path Check:")
    if results["BFS"]["found"] and results["A*"]["found"]:
        print(f"BFS length == A* length: {results['BFS']['length'] == results['A*']['length']}")
        print(f"DFS length == BFS length: {results['DFS']['length'] == results['BFS']['length']}"
              "（DFS は最短経路を保証しない）")
    else:
        print("ゴールに到達できません（スタートとゴールが障害物で分断されています）")
    print()

    print("Map Visualization（* = 最終経路, o = 探索済みセル）:")
    for name, _ in ALGORITHMS:
        print(f"[{name}]")
        print(render_result(grid_map, results[name]))
        print()


print("E1: Robot Path Planning")
print("（4方向移動・移動コスト1のグリッド上のシミュレーションです。実際のロボット制御ではありません）")
print()

for map_file in MAP_FILES:
    print("=" * 60)
    show_map(map_file)

print("=" * 60)
print("Student TODO：benchmark.py でマップの大きさ・障害物の割合を変えて、DFS・BFS・A* を比較しよう。")

# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：data/ に自分たちのマップを追加し（障害物が少ない・多い・狭い通路・行き止まり）、結果を比べる。
# TODO 2：grid_map.DIRECTIONS の順序を変えると、DFS の経路と展開ノード数がどう変わるか調べる。
# TODO 3：BFS と A* の経路長が常に一致することを、多くのマップで確かめる。
# TODO 4：探索時間を複数回測定し、平均・ばらつきを求める（benchmark.py）。
