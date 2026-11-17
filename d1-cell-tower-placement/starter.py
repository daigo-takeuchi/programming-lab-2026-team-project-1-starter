# D1：携帯電話基地局・アンテナの最適配置 — starter code
#
# 架空の地域データ（data/sample_region.json）の2つのシナリオについて、
# ランダム配置・貪欲法・全探索で基地局を選び、カバー人口を比べる。

from pathlib import Path

import coverage
import placement

DATA_FILE = Path(__file__).parent / "data" / "sample_region.json"
RANDOM_SEED = 0         # ランダム配置の乱数シード（変えて試してみよう）

print("D1: Cell Tower Placement Optimization")

for scenario in coverage.load_scenarios(DATA_FILE):
    areas, towers, k = scenario["areas"], scenario["towers"], scenario["k"]

    print()
    print("===", scenario["name"], "===")
    print(scenario["description"])
    print("Residential Areas:", len(areas))
    print("Candidate Towers :", len(towers))
    print("Maximum Towers K :", k)
    print("Total Population :", coverage.total_population(areas))
    print("Coverage of each tower:")
    for tower in sorted(towers):
        print(f"  {tower}: {sorted(towers[tower])}  "
              f"population {coverage.covered_population(areas, towers, [tower])}")

    results = [
        ("Random", placement.random_placement(areas, towers, k, seed=RANDOM_SEED)),
        ("Greedy", placement.greedy(areas, towers, k)),
        ("Brute Force", placement.brute_force(areas, towers, k)),
    ]
    optimum = results[-1][1]["covered"]     # 全探索が完了したので、これが厳密な最適解

    print()
    print(f"{'Algorithm':<13}{'Selected Towers':<18}{'Covered Population':>19}{'Evaluated':>11}")
    for name, result in results:
        print(f"{name:<13}{', '.join(result['selected']):<18}{result['covered']:>19}{result['evaluated']:>11}")

    print()
    print("Population Coverage:")
    for name, result in results:
        print(f"  {name}: {result['rate']:.1%}")

    print("Optimality Gap (OPT - coverage, ratio = coverage / OPT):")
    for name, result in results[:2]:
        ratio = placement.approximation_ratio(result["covered"], optimum)
        ratio_text = "undefined" if ratio is None else f"{ratio:.3f}"
        print(f"  {name}: {optimum - result['covered']} (ratio {ratio_text})")

print()
print(f"※ Random は seed = {RANDOM_SEED} の1回だけの結果です。seed を変えて複数回試しましょう。")


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：RANDOM_SEED を変えてランダム配置を何度も実行し、カバー人口の平均・最小・最大を求める。
# TODO 2：K を 1, 2, 3, ... と変えて、3方式の結果を比べる。
# TODO 3：Region 2 で、貪欲法が最適解を見つけられない理由を、選択の過程から説明する。
# TODO 4：benchmark.py を使って、M・K・R を変えたときの処理時間を測る。
