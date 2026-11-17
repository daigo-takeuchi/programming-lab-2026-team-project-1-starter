# F1：最適な転職年齢の全探索と、キャリアの順位付け
#
# ■ 全探索
#   転職年齢の候補 K 個それぞれについて、T 年分の所得を計算する → O(K T)
#   （各候補で incomes・costs・NPV を 1 回ずつ計算するので、正確には定数倍 × K × T）
#
# ■ 最大値の選び方（教科書のコードを直接使う）
#   1. 教科書 第2章 max_of（textbook/max.py）で、評価値のリストの最大値を求める          O(K)
#   2. 教科書 第3章 seq_search（textbook/ssearch_while.py）で、その値が最初に現れる位置を探す O(K)
#   → 同じ最大値が複数あるときは、「候補リストで最初に現れるもの」＝ 昇順の候補なら「最も若い転職年齢」を選ぶ。
#
# ■ 順位付け
#   教科書 第6章 insertion_sort（textbook/insertion_sort.py、安定なソート）で、評価値の大きい順に並べる。
#   (−評価値, 元の順番) の組を並べるので、評価値が同じなら元の順番が保たれる。

from textbook.insertion_sort import insertion_sort
from textbook.max import max_of
from textbook.ssearch_while import seq_search

import career_model as cm
import income_analysis as ia
import scenarios as sc

CRITERIA = {"gross": "Lifetime Gross Income", "net": "Cumulative Net Income", "npv": "NPV"}


def switch_age_candidates(scenario, first=22, last=60):
    """転職年齢の候補 [first, ..., last] のうち、そのシナリオで転職できる年齢（就職後・退職前）だけを返す"""
    retirement = scenario.get("retirement_age", cm.RETIREMENT_AGE)
    return [a for a in range(first, last + 1) if scenario["start_age"] < a < retirement]


def evaluate_switch_ages(scenario, candidate_ages, rate=ia.DEFAULT_DISCOUNT_RATE):
    """各転職年齢について、生涯所得・累積純収入・NPV を計算する（元のシナリオは変更しない）"""
    if scenario.get("job_change") is None:
        raise ValueError("job_change を持つシナリオを指定してください")
    rows = []
    for age in candidate_ages:                                    # K 回
        s = sc.with_changes(scenario, **{"job_change.age": age})  # コピーを作って転職年齢だけ変える
        r = ia.evaluate(s, rate)                                  # O(T)
        r["switch_age"] = age
        rows.append(r)
    return rows


def best_by(rows, key):
    """rows の中で key の値が最大の行を返す（候補が空なら None）。同点なら rows の中で最初の行"""
    if not rows:
        return None
    values = [r[key] for r in rows]
    maximum = max_of(values)               # 教科書：最大値
    index = seq_search(values, maximum)    # 教科書：線形探索（最初に現れる位置）
    return rows[index]


def optimal_switch_ages(rows):
    """評価基準（生涯所得・累積純収入・NPV）ごとの最適な転職年齢。候補が空なら各値は None"""
    out = {}
    for key in CRITERIA:
        best = best_by(rows, key)
        out[key] = None if best is None else {"switch_age": best["switch_age"], "value": best[key]}
    return out


def rank(results, key):
    """評価値 key の大きい順に並べた新しいリスト（同点なら元の順番。元のリストは変更しない）"""
    pairs = [(-r[key], i) for i, r in enumerate(results)]
    insertion_sort(pairs)                  # 教科書：単純挿入ソート（安定、O(N^2)）
    return [results[i] for _neg, i in pairs]


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：転職年齢の範囲（first・last）を変更する。
# TODO 2：転職後の年収 new_salary を変更する（例：with_changes(s, **{"job_change.new_salary": 380})）。
# TODO 3：転職費用 cost を変更する。
# TODO 4：転職前・転職後の昇給率を変更する。
# TODO 5：最適な転職年齢を再計算する。
# TODO 6：評価基準（gross・net・npv）で最適な転職年齢が違う条件を探す。
# TODO 7：転職を 2 回する場合の全探索（候補の組 K^2 個）を書き、計算量を考える（→ 動的計画法、Advanced B）。
