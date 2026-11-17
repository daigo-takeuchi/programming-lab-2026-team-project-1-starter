# D1：配置アルゴリズムの性能比較 — 学生が実験を作るための入口
#
# ここにあるのは「架空の地域をランダムに作る関数」と「1つの条件で1回だけ測る例」だけである。
# M・K・R を変えた繰り返し実験、ランダム配置の多数回試行、グラフ化は、学生が実装する（下の TODO）。
#
# 実行：python3 benchmark.py

import random
import time
from math import comb

import placement


def make_region(r, m, cover_size, seed=0):
    """架空の地域を作る：R 個のエリア（人口 100〜2000）と、M 個の基地局候補

    各基地局は、ランダムに選んだ cover_size 個のエリアをカバーする。
    """
    rng = random.Random(seed)
    areas = {f"A{i}": rng.randrange(100, 2001) for i in range(r)}
    names = list(areas)
    towers = {f"T{j:03d}": set(rng.sample(names, cover_size)) for j in range(m)}
    return areas, towers


if __name__ == "__main__":
    R, M, K, COVER = 40, 16, 4, 5

    # 地域データの生成時間は、測定に含めない
    areas, towers = make_region(R, M, COVER, seed=2026)

    for name, run in [("Greedy", lambda: placement.greedy(areas, towers, K)),
                      ("Brute Force", lambda: placement.brute_force(areas, towers, K))]:
        start = time.perf_counter()
        result = run()
        elapsed = time.perf_counter() - start
        print(f"{name:<12}: covered = {result['covered']}, evaluated = {result['evaluated']}, "
              f"time = {elapsed:.6f} 秒")

    print(f"R = {R}, M = {M}, K = {K}（1回だけの測定例）  C(M, K) = {comb(M, K):,}")


# ------------------------------------------------------------
# 学生が取り組む課題
# ------------------------------------------------------------
# TODO 1：候補地点数 M を変更する（全探索は C(M, K) が急増するので、小さい値から）。
# TODO 2：設置可能な基地局数 K を変更する。
# TODO 3：居住エリア数 R を変更する（カバー範囲の大きさ cover_size も）。
# TODO 4：ランダム配置を複数回実行する（seed を変えて、平均・最小・最大を記録）。
# TODO 5：貪欲法の処理時間を測定する。
# TODO 6：全探索の処理時間を測定する。
# TODO 7：評価した候補配置数（evaluated）を比較する。
# TODO 8：カバー人口を比較する。
# TODO 9：最適解との差（OPT − カバー人口）と近似比を比較する。
# TODO 10：結果を表・グラフにまとめる。
# TODO 11：理論計算量と実測結果を比較する。
#
# 公平な比較の条件：
#   - 同じ地域データ・同じ K・同じ目的関数（カバー人口）を使う。
#   - ランダム配置は複数回試行し、乱数シードを記録する。
#   - 実行時間と解の品質を分けて評価する。
#   - 全探索が最後まで完了した場合だけ、その結果を厳密な最適解として扱う。
#   - 測りたい処理だけを time.perf_counter() で挟む：
#       start = time.perf_counter()
#       placement.greedy(areas, towers, K)
#       elapsed = time.perf_counter() - start
