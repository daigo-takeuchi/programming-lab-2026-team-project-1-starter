# F2：条件の全探索と「最適」の選び方
#
# ■ 全探索
#   候補条件 K 個それぞれについて、T 年分のシミュレーションを行う → O(K T)
#   2 つのパラメータの組合せ（K1 × K2 個）なら O(K1 K2 T)
#
# ■ 「最適」は 1 つではない（README 11章）
#   ・FIRE 達成年齢を最小化（minimize=True）
#   ・一定年齢（例：65 歳）での資産を最大化
#   ・現役時の生活費を最大化（貯蓄率を下げるほど大きい）
#   ・リタイア後の資産持続年数を最大化
#   貯蓄率を上げると FIRE は早まり得るが、今の生活費は減る。貯蓄率 100%（生活費 0）は現実の答えではない。
#   どの指標で選ぶか、どんな制約（最低生活費など）を置くかを、研究の中で決めること（Advanced C）。
#
# ■ 最大値・最小値の選び方（教科書のコードを直接使う）
#   1. FIRE 未達成（None）の候補を除く
#   2. 教科書 第2章 max_of で最大値を求める（最小化のときは値の符号を反転してから最大値を求める）
#   3. 教科書 第3章 seq_search で、その値が最初に現れる位置を探す
#   → 同順位なら「候補リストで最初に現れる条件」を選ぶ。
#
# ■ 順位付け：教科書 第6章 insertion_sort（安定）。未達成（None）は最後。

from textbook.insertion_sort import insertion_sort
from textbook.max import max_of
from textbook.ssearch_while import seq_search

import fire_analysis as fa
import financial_model as fm
import retirement_model as rm

DEFAULT_SAVINGS_RATES = [0.1, 0.2, 0.3, 0.4, 0.5]
DEFAULT_RETURNS = [0.0, 0.02, 0.04, 0.06, 0.08]


# ------------------------------------------------------------
# 1 つのシナリオの評価
# ------------------------------------------------------------
def evaluate_scenario(s, settings):
    """資産形成 → FIRE 目標・達成年齢 → （達成したら）その年齢でリタイアした場合の取り崩し

    返り値の主なキー：target, fire_age, assets_at_report, current_expenses,
                      depletion_age, years_sustained, sustainable（未達成ならリタイア関連は None）
    """
    acc = fm.accumulate(s, settings["accumulation_end_age"])
    target = fa.fire_target(s["annual_expenses"], settings["withdrawal_rate"])
    age = fa.fire_age(acc, target)
    result = {
        "name": s.get("name"), "label": s.get("label", s.get("name")),
        "savings_rate": s["savings_rate"], "annual_return": s["annual_return"],
        "annual_income": s["annual_income"], "annual_expenses": s["annual_expenses"],
        "current_expenses": fm.living_expenses(s["annual_income"], s["savings_rate"]),
        "target": target, "fire_age": age,
        "assets_at_report": fm.assets_at(acc, settings["report_age"]),
        "retire_assets": None, "depletion_age": None, "years_sustained": None, "sustainable": None,
    }
    if age is not None and age < settings["retirement_end_age"]:
        r = settings.get("retirement_return")
        ret = rm.simulate_withdrawal(age, settings["retirement_end_age"], fm.assets_at(acc, age),
                                     s["annual_expenses"], s["annual_return"] if r is None else r)
        result.update(retire_assets=fm.assets_at(acc, age), depletion_age=rm.depletion_age(ret),
                      years_sustained=rm.years_sustained(ret), sustainable=rm.is_sustainable(ret))
    return result


# ------------------------------------------------------------
# 候補の列挙と全探索
# ------------------------------------------------------------
def savings_rate_candidates(values=None):
    """貯蓄率の候補（0〜1 の範囲を確認し、新しいリストで返す）"""
    values = list(DEFAULT_SAVINGS_RATES if values is None else values)
    for v in values:
        if not 0 <= v <= 1:
            raise ValueError(f"貯蓄率の候補 {v} が 0〜1 の範囲外です")
    return values


def return_candidates(values=None):
    """収益率の候補（-1 以上を確認し、新しいリストで返す）"""
    values = list(DEFAULT_RETURNS if values is None else values)
    for v in values:
        if v < -1:
            raise ValueError(f"収益率の候補 {v} が -1 より小さいです")
    return values


def sweep_savings_rate(s, rates, settings, keep="income"):
    """貯蓄率を変えて評価する（O(K T)）

    keep="income"   ：所得を固定。生活費 = 所得 × (1 − 貯蓄率) も変わる（＝ FIRE 目標も変わる）
    keep="expenses" ：生活費を固定。所得 = 生活費 / (1 − 貯蓄率) が変わる（貯蓄率 1 は不可）
    """
    rows = []
    for rate in savings_rate_candidates(rates):
        if keep == "income":
            t = fm.with_changes(s, savings_rate=rate, annual_expenses=fm.living_expenses(s["annual_income"], rate))
        elif keep == "expenses":
            if rate >= 1:
                raise ValueError("生活費を固定する場合、貯蓄率 1 は計算できません")
            t = fm.with_changes(s, savings_rate=rate, annual_income=s["annual_expenses"] / (1 - rate))
        else:
            raise ValueError("keep は 'income' か 'expenses' です")
        r = evaluate_scenario(t, settings)
        r["param"] = rate
        rows.append(r)
    return rows


def sweep_return(s, returns, settings):
    """収益率を変えて評価する（貯蓄率・生活費は固定）"""
    rows = []
    for ret in return_candidates(returns):
        r = evaluate_scenario(fm.with_changes(s, annual_return=ret), settings)
        r["param"] = ret
        rows.append(r)
    return rows


def sweep_expenses(s, expenses_list, settings, keep="income"):
    """生活費を変えて評価する

    keep="income"       ：所得を固定。貯蓄率 = (所得 − 生活費) / 所得 が変わる
    keep="savings_rate" ：貯蓄率を固定。所得 = 生活費 / (1 − 貯蓄率) が変わる
    """
    rows = []
    for e in expenses_list:
        if keep == "income":
            t = fm.with_changes(s, annual_expenses=e, savings_rate=fm.savings_rate_for_expenses(s["annual_income"], e))
        elif keep == "savings_rate":
            t = fm.with_changes(s, annual_expenses=e, annual_income=e / (1 - s["savings_rate"]))
        else:
            raise ValueError("keep は 'income' か 'savings_rate' です")
        r = evaluate_scenario(t, settings)
        r["param"] = e
        rows.append(r)
    return rows


def grid_fire_age(s, rates, returns, settings, keep="income"):
    """貯蓄率 × 収益率の全組合せの FIRE 達成年齢（未達成は None）。matrix[i][j] = rates[i], returns[j]

    O(K1 K2 T)
    """
    matrix = []
    for rate in savings_rate_candidates(rates):
        row = []
        for ret in return_candidates(returns):
            base = fm.with_changes(s, annual_return=ret)
            row.append(sweep_savings_rate(base, [rate], settings, keep)[0]["fire_age"])
        matrix.append(row)
    return matrix


# ------------------------------------------------------------
# 最適な条件の選択と順位付け
# ------------------------------------------------------------
def best(rows, key, minimize=False):
    """key の値が最大（minimize=True なら最小）の行。None の行は除く。候補がなければ None。同順位は最初の行"""
    valid = [r for r in rows if r.get(key) is not None]
    if not valid:
        return None
    values = [-r[key] if minimize else r[key] for r in valid]
    index = seq_search(values, max_of(values))      # 教科書：最大値 → その最初の位置
    return valid[index]


def rank(rows, key, minimize=False):
    """key で並べた新しいリスト（None は最後、同順位は元の順番。元のリストは変更しない）"""
    keys = []
    for i, r in enumerate(rows):
        v = r.get(key)
        if v is None:
            keys.append((1, 0, i))
        else:
            keys.append((0, v if minimize else -v, i))
    insertion_sort(keys)                             # 教科書：単純挿入ソート（安定）
    return [rows[i] for _missing, _v, i in keys]


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：最低生活費（例：年 250 万円）を下回る貯蓄率を候補から除いて、FIRE 達成年齢を最小化する（Advanced C）。
# TODO 2：「FIRE 達成年齢」と「現役時の生活費」の両方を表にして、トレードオフを考える。
# TODO 3：FIRE 達成年齢が x 歳以下になる最小の貯蓄率を、全探索と二分探索で求めて比べる
#         （貯蓄率に対して FIRE 達成年齢が単調かどうかを先に確かめる）。
# TODO 4：リタイア後の持続年数（years_sustained）を最大化する条件を探す。
