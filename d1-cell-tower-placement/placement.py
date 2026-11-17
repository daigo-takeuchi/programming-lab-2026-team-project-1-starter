# D1：基地局の配置アルゴリズム（Maximum Coverage Problem）
#
# 共通の条件：
#   - K 局以内の基地局を選び、カバー人口を最大化する（同じエリアの人口は1回だけ数える）
#   - 基地局の設置コストはすべて等しい
#   - 基地局IDは昇順に並べて扱う（同点のときに結果が毎回同じになるように）
#
# どの関数も同じ形の辞書を返す。
#   selected  : 選んだ基地局IDのリスト（貪欲法は選んだ順、それ以外は昇順）
#   covered   : カバー人口
#   rate      : 人口カバー率
#   evaluated : カバー人口（または追加カバー人口）を計算した回数

import random
from itertools import combinations

import coverage


def _result(areas, towers, selected, evaluated):
    return {
        "selected": list(selected),
        "covered": coverage.covered_population(areas, towers, selected),
        "rate": coverage.coverage_rate(areas, towers, selected),
        "evaluated": evaluated,
    }


def random_placement(areas, towers, k, seed=None):
    """ランダム配置：候補から K 局をランダムに選ぶ（seed を指定すると再現できる）

    1回の呼び出しで1つの配置を作る。複数回の試行は、seed を変えて呼び出す。
    """
    coverage.check_k(k, towers)
    rng = random.Random(seed)
    selected = sorted(rng.sample(sorted(towers), k))
    return _result(areas, towers, selected, evaluated=1)


def brute_force(areas, towers, k):
    """全探索：M 個の候補から K 個を選ぶすべての組合せを調べ、カバー人口が最大の配置を返す

    基地局を増やしてもカバー人口は減らないので、ちょうど K 局の組合せだけを調べれば、
    「K 局以内」の最適解が得られる。同点なら、組合せを列挙した順で最初のもの（ID の辞書順）。
    """
    coverage.check_k(k, towers)
    best = None
    best_covered = -1
    evaluated = 0
    for combo in combinations(sorted(towers), k):
        evaluated += 1
        covered = coverage.covered_population(areas, towers, combo)
        if covered > best_covered:
            best, best_covered = combo, covered
    return _result(areas, towers, best, evaluated)


def greedy(areas, towers, k):
    """貪欲法：毎回「まだカバーされていない人口を最も多く追加でカバーできる基地局」を選ぶ

    1. 最初は何も選んでいない
    2. 未選択の各基地局について、追加でカバーできる人口（増分）を計算する
    3. 増分が最大の基地局を選び（同点なら ID の小さい方）、カバー済みエリアを更新する
    4. K 局に達するまで繰り返す。増分が 0 になったら、その時点で終了する（K 局以内）

    「各基地局の総カバー人口が大きい順に K 局選ぶ」方法とは違う。
    総カバー人口が大きくても、すでに選んだ基地局と重なっていれば増分は小さい。
    """
    coverage.check_k(k, towers)
    selected = []
    covered = set()
    evaluated = 0
    for _ in range(k):
        best, best_gain = None, 0
        for tower in sorted(towers):
            if tower in selected:
                continue
            evaluated += 1
            gain = sum(areas[area] for area in towers[tower] - covered)
            if gain > best_gain:                # 同点なら先に見つけた（ID の小さい）方
                best, best_gain = tower, gain
        if best is None:                        # どれを選んでも増えない
            break
        selected.append(best)
        covered |= towers[best]
    return _result(areas, towers, selected, evaluated)


def approximation_ratio(value, optimum):
    """近似比 = アルゴリズムのカバー人口 / 最適解のカバー人口（OPT）

    OPT が 0 のときは、比が定義できないので None を返す。
    """
    if optimum == 0:
        return None
    return value / optimum


# ------------------------------------------------------------
# 学生が取り組む課題（Advanced Research）
# ------------------------------------------------------------
# TODO（Advanced C）：設置コストと予算を追加し、「追加カバー人口 / コスト」で選ぶ貪欲法を作る。
# TODO（Advanced E）：1局が故障したときのカバー人口を調べる関数を作る。
# TODO：再帰（バックトラッキング）で組合せを列挙する全探索を書き、itertools.combinations と比べる。
