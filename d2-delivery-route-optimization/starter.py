# D2：配送ルートの最適化 — starter code
#
# 架空の配送先データ（data/sample_deliveries.json）の2つのシナリオについて、
# ランダム探索・最近傍法・全探索でルートを求め、総移動距離を比べる。
# 2-opt は学生の実装課題（two_opt.py）。

from pathlib import Path

import solvers
from distance import format_route
from locations import load_scenarios

DATA_FILE = Path(__file__).parent / "data" / "sample_deliveries.json"
RANDOM_TRIALS = 20      # ランダム探索の試行回数
RANDOM_SEED = 0         # ランダム探索の乱数シード

print("D2: Delivery Route Optimization")

for scenario in load_scenarios(DATA_FILE):
    locations, depot = scenario["locations"], scenario["depot"]

    print()
    print("===", scenario["name"], "===")
    print(scenario["description"])
    print("Delivery Locations:", len(locations) - 1)
    for location_id, point in locations.items():
        print(f"  {location_id:<6}{point}")

    results = [
        (f"Random ({RANDOM_TRIALS} trials)", solvers.random_search(locations, depot, RANDOM_TRIALS, seed=RANDOM_SEED)),
        ("Nearest Neighbor", solvers.nearest_neighbor(locations, depot)),
        ("Brute Force", solvers.brute_force(locations, depot)),
    ]
    optimum = results[-1][1]["distance"]    # 全探索が完了したので、これが厳密な最適解

    print()
    print(f"{'Algorithm':<20}{'Distance':>10}{'Optimality Gap':>16}{'Evaluated':>11}")
    for name, result in results:
        gap = solvers.optimality_gap(result["distance"], optimum)
        gap_text = "undefined" if gap is None else f"{gap:.1f}%"
        print(f"{name:<20}{result['distance']:>10.3f}{gap_text:>16}{result['evaluated']:>11}")

    print()
    for name, result in results:
        print(f"{name}:")
        print("  " + format_route(depot, result["route"]))

print()
print("Advanced / Student TODO:")
print("  Implement 2-opt improvement in two_opt.py (README 8章).")
print("  Then compare: random route + 2-opt, nearest neighbor + 2-opt, brute force.")


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：two_opt.two_opt() を実装し、最近傍法やランダム探索のルートを改善する。
# TODO 2：RANDOM_SEED と RANDOM_TRIALS を変えて、ランダム探索の結果のばらつきを調べる。
# TODO 3：Town 2 で、最近傍法が最適解を見つけられない理由を、訪問の過程から説明する。
# TODO 4：benchmark.py を使って、配送先数 N を変えたときの処理時間を測る。
