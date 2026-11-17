# G1：最適化アルゴリズム（全探索・Greedy 法・局所探索）
#
# ■ 探索空間
#   予算を M 個の整数単位に分け（M = 1 / 刻み。刻み 0.1 なら M = 10）、4 分野への配分を
#   整数の組 (u1, u2, u3, u4)（合計 M、各 0 以上）で表す。配分率 = u / M。
#   整数で扱うので、合計がちょうど 1 になる（浮動小数点の誤差で制約を破らない）。
#   候補の数 = C(M + K − 1, K − 1)（K = 4 分野。M = 10 なら 286 通り、M = 20 なら 1,771 通り）
#
# ■ 3 つのアルゴリズムは、同じ目的関数（Evaluator）・同じ経済シミュレーション・同じ探索空間を使う。
#   全探索の最良値は、この「離散化した探索空間」の中での基準値（真の連続最適値ではない）。
#   Greedy 法・局所探索が全探索と同じ結果になるとは限らない。
#
# ■ 同点の処理（決定的）
#   最大値を教科書の max_of（第2章）で求め、それが最初に現れる位置を seq_search（第3章）で探す。
#   → 候補の並び順で最初のものを選ぶ。候補の並び順は各関数のコメントのとおり。

import math
import time

import economic_model as em
import simulation as sim
from allocation_strategies import K, shares_from_units, units_count, units_from_shares, equal_allocation
from textbook.max import max_of
from textbook.ssearch_while import seq_search
from textbook.insertion_sort import insertion_sort

OBJECTIVES = ("final_gdp", "cumulative_gdp", "final_living_standard", "average_living_standard", "weighted")
OBJECTIVE_LABELS = {"final_gdp": "final GDP", "cumulative_gdp": "cumulative GDP",
                    "final_living_standard": "final living standard",
                    "average_living_standard": "average living standard",
                    "weighted": "weighted (GDP index & living standard)"}


# ------------------------------------------------------------
# 目的関数
# ------------------------------------------------------------
def objective_value(records, params, objective="final_gdp", gdp_weight=0.5):
    """シミュレーション結果 records から目的関数の値を計算する（大きいほど良い）

      final_gdp               ：最終年の GDP
      cumulative_gdp          ：1〜T 年の GDP の合計
      final_living_standard   ：最終年の生活水準
      average_living_standard ：1〜T 年の生活水準の平均
      weighted                ：gdp_weight × GDP 指数 + (1 − gdp_weight) × 生活水準
                                （GDP 指数 = 最終 GDP / 初期 GDP。単位をそろえるため、どちらも初年度 = 1 の指数）
    """
    last = records[-1]
    years = records[1:]
    if objective == "final_gdp":
        return last["gdp"]
    if objective == "cumulative_gdp":
        return sum(r["gdp"] for r in years)
    if objective == "final_living_standard":
        return last["living_standard"]
    if objective == "average_living_standard":
        return sum(r["living_standard"] for r in years) / len(years) if years else last["living_standard"]
    if objective == "weighted":
        if not 0 <= gdp_weight <= 1:
            raise ValueError("gdp_weight は 0〜1 にしてください")
        gdp_index = last["gdp"] / params["initial_gdp"] if params["initial_gdp"] > 0 else 0.0
        return gdp_weight * gdp_index + (1 - gdp_weight) * last["living_standard"]
    raise ValueError(f"目的関数 {objective!r} は {OBJECTIVES} のどれかにしてください")


class Evaluator:
    """整数単位の配分 → 目的関数の値。評価した回数（= シミュレーションの回数）を数える

    合計が M 未満の配分（Greedy 法の途中）は、予算の一部だけを投資した状態として評価する。
    """

    def __init__(self, params, objective="final_gdp", years=None, gdp_weight=0.5):
        if objective not in OBJECTIVES:
            raise ValueError(f"目的関数 {objective!r} は {OBJECTIVES} のどれかにしてください")
        self.params = params
        self.objective = objective
        self.years = int(params["simulation_years"] if years is None else years)
        self.gdp_weight = gdp_weight
        self.evaluations = 0

    def __call__(self, units, m):
        if sum(units) > m:
            raise ValueError(f"予算制約違反：単位の合計 {sum(units)} が {m} を超えています")
        self.evaluations += 1
        recs = sim.simulate(shares_from_units(tuple(units), m), self.params, self.years, check=False)
        return objective_value(recs, self.params, self.objective, self.gdp_weight)

    def records(self, units, m):
        """（評価回数に数えずに）その配分のシミュレーション結果を返す"""
        return sim.simulate(shares_from_units(tuple(units), m), self.params, self.years)


def best_index(values):
    """最大値の位置（同点なら最初）。教科書の max_of と seq_search を使う"""
    return seq_search(values, max_of(values))


def _result(name, units, m, value, evaluator, start_eval, t0, iterations, guarantee, **extra):
    out = {"algorithm": name, "units": tuple(units), "shares": shares_from_units(tuple(units), m), "m": m,
           "objective": value, "objective_name": evaluator.objective,
           "evaluations": evaluator.evaluations - start_eval, "iterations": iterations,
           "runtime_s": time.perf_counter() - t0, "guarantee": guarantee}
    out.update(extra)
    return out


# ------------------------------------------------------------
# 全探索
# ------------------------------------------------------------
def count_allocations(m, k=K):
    """候補の数 C(m + k − 1, k − 1)"""
    return math.comb(m + k - 1, k - 1)


def enumerate_allocations(m, k=K):
    """合計 m になる k 個の 0 以上の整数の組をすべて列挙する（再帰）

    並び順：1 番目の分野の単位が多い順（(m, 0, 0, 0) → … → (0, 0, 0, m)）。これが同点時の優先順位になる。
    """
    if k == 1:
        return [(m,)]
    out = []
    for first in range(m, -1, -1):                     # 1 番目の分野に first 単位
        for rest in enumerate_allocations(m - first, k - 1):
            out.append((first,) + rest)
    return out


def rank_candidates(candidates, values, top=None):
    """候補を目的関数の大きい順に並べる（同点は列挙順）。教科書の insertion_sort（安定）を使う

    計算量 O(C²)（単純挿入ソート）。候補が多いときは top を小さくしても並べ替え自体の手間は変わらない。
    """
    keyed = [(-v, i) for i, v in enumerate(values)]
    insertion_sort(keyed)
    ranked = [(candidates[i], -nv) for nv, i in keyed]
    return ranked if top is None else ranked[:top]


def exhaustive(evaluator, m, keep_values=False):
    """全探索：すべての候補を評価し、目的関数が最大の配分を返す（離散探索空間の中で最適が保証される）"""
    t0, e0 = time.perf_counter(), evaluator.evaluations
    candidates = enumerate_allocations(m)
    values = [evaluator(c, m) for c in candidates]
    i = best_index(values)
    extra = {"candidates": candidates, "values": values} if keep_values else {}
    return _result("Exhaustive Search", candidates[i], m, values[i], evaluator, e0, t0, len(candidates),
                   "離散化した探索空間の中で最適（すべての候補を評価）", **extra)


# ------------------------------------------------------------
# Greedy 法
# ------------------------------------------------------------
def greedy(evaluator, m):
    """Greedy 法：予算を 1 単位ずつ、目的関数が最も大きくなる分野に足していく（m 回）

    各ステップで K 分野に 1 単位足した K 個の候補を評価する（同点は分野の順：教育 → 研究開発 → インフラ → 医療）。
    評価回数 m × K。一度足した単位は戻さないので、全体の最適は保証されない。
    """
    t0, e0 = time.perf_counter(), evaluator.evaluations
    units = [0] * K
    path = []
    for _step in range(m):
        trials = []
        for j in range(K):
            cand = units[:]
            cand[j] += 1
            trials.append(evaluator(cand, m))
        j = best_index(trials)
        units[j] += 1
        path.append((tuple(units), trials[j]))
    value = path[-1][1] if path else evaluator(units, m)
    return _result("Greedy", units, m, value, evaluator, e0, t0, m, "保証なし（一度決めた配分を戻さない）",
                   path=path)


# ------------------------------------------------------------
# 局所探索
# ------------------------------------------------------------
def neighbors(units):
    """近傍：ある分野 i から別の分野 j へ 1 単位移した配分（予算の合計は変わらない）。並び順は (i, j) の辞書順"""
    out = []
    for i in range(K):
        if units[i] == 0:
            continue
        for j in range(K):
            if i != j:
                cand = list(units)
                cand[i] -= 1
                cand[j] += 1
                out.append(tuple(cand))
    return out


def local_search(evaluator, m, start_units=None, max_iterations=100, tol=1e-12):
    """局所探索（山登り法）：近傍の中で最も良い配分に移る。改善がなくなるか max_iterations 回で終了

    最も良い近傍でも今の配分より良くならなければ止まる（局所最適解）。初期配分によって結果が変わることがある。
    """
    t0, e0 = time.perf_counter(), evaluator.evaluations
    current = tuple(start_units) if start_units is not None else units_from_shares(equal_allocation(), m)
    if sum(current) != m:
        raise ValueError(f"初期配分の単位の合計は {m} にしてください（{current}）")
    value = evaluator(current, m)
    path = [(current, value)]
    iterations = 0
    while iterations < max_iterations:
        cands = neighbors(current)
        if not cands:
            break
        values = [evaluator(c, m) for c in cands]
        i = best_index(values)
        if values[i] <= value + tol:            # 改善しない → 局所最適
            break
        current, value = cands[i], values[i]
        path.append((current, value))
        iterations += 1
    stopped = "改善なし（局所最適）" if iterations < max_iterations else "最大反復回数"
    return _result("Local Search", current, m, value, evaluator, e0, t0, iterations,
                   "保証なし（局所最適で止まることがある）", path=path, start=path[0][0], stopped=stopped)


# ------------------------------------------------------------
# アルゴリズムの比較
# ------------------------------------------------------------
def compare_algorithms(params, objective="final_gdp", step=0.1, years=None, start=None, gdp_weight=0.5):
    """同じ目的関数・同じ刻み・同じ評価期間で、全探索・Greedy 法・局所探索を実行する

    戻り値：{"exhaustive": 結果, "greedy": 結果, "local_search": 結果}。各結果に gap（全探索との差）を加える。
    """
    import evaluation as ev
    m = units_count(step)
    results = {}
    for key, run in (("exhaustive", lambda e: exhaustive(e, m)),
                     ("greedy", lambda e: greedy(e, m)),
                     ("local_search", lambda e: local_search(e, m, units_from_shares(start, m) if start else None))):
        results[key] = run(Evaluator(params, objective, years, gdp_weight))
    best = results["exhaustive"]["objective"]
    for r in results.values():
        r["gap"] = ev.optimization_gap(best, r["objective"])
    return results


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：刻み（step）を 0.2・0.1・0.05 と変えて、候補の数・実行時間・最良値を比べる（Notebook 03）。
# TODO 2：局所探索の初期配分を変える。複数の初期配分から始めて最良を取る（多スタート局所探索）。
# TODO 3：局所探索を「最初に見つかった改善に移る」方式（first improvement）にして評価回数を比べる。
# TODO 4：同じ配分を何度も評価しないよう、辞書で結果を記録する（メモ化）。評価回数はどう変わるか。
# TODO 5：Greedy 法で、1 単位ずつではなく 2 単位ずつ足すとどうなるか。
