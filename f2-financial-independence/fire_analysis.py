# F2：FIRE 目標資産と FIRE 達成年齢
#
#   FIRE Target = Annual Expenses / Withdrawal Rate        （例：300 万円 / 0.04 = 7,500 万円）
#   FIRE 達成年齢 = 年齢別資産を若い順に調べて、初めて FIRE Target 以上になった年齢
#
# ■ 2 つの探索方法（README 10章）
#   fire_age        ：線形探索（教科書 第3章 seq_search）。どんな資産推移でも使える。O(T)
#   fire_age_binary ：二分探索。資産が年齢とともに「減らない」（単調非減少）場合だけ使える。O(log T)
#       ・収益率 ≥ 0 かつ貯蓄 ≥ 0 なら、資産は必ず単調非減少になる。
#       ・収益率が負の年がある（Advanced A・B）と単調でなくなり、二分探索は誤った答えを返し得る。
#       ・教科書の bin_search（第3章）は「キーと等しい要素」を探す関数で、
#         「条件を満たす最初の位置」は返さないので、ここでは境界を探す形に書き直している。
#
# ■ 注意：FIRE 目標に到達しても、その後の生活費を賄い続けられるとは限らない（retirement_model.py、RQ5）。

from textbook.ssearch_while import seq_search

import financial_model as fm

DEFAULT_WITHDRAWAL_RATE = 0.04   # 教育用の初期仮定（README 7章：4% ルールは保証ではない）


def fire_target(annual_expenses, withdrawal_rate=DEFAULT_WITHDRAWAL_RATE):
    """FIRE 目標資産 = 年間生活費 / 取り崩し率"""
    fm._check_number("annual_expenses", annual_expenses)
    fm._check_number("withdrawal_rate", withdrawal_rate)
    if annual_expenses < 0:
        raise ValueError("年間生活費は 0 以上にしてください")
    if not 0 < withdrawal_rate <= 1:
        raise ValueError(f"取り崩し率は 0 より大きく 1 以下にしてください（0 では目標が無限大）：{withdrawal_rate}")
    return annual_expenses / withdrawal_rate


def reached_flags(assets, target):
    """各年齢で目標に到達しているか（True / False のリスト）"""
    return [a >= target for a in assets]


def fire_age(rows, target):
    """FIRE 達成年齢（年齢別資産の線形探索）。達成できなければ None

    初期資産がすでに目標以上なら、開始年齢を返す。
    """
    ages, assets = fm.assets_by_age(rows)
    index = seq_search(reached_flags(assets, target), True)   # 教科書：最初に True が現れる位置
    return None if index == -1 else ages[index]


def is_nondecreasing(values):
    """単調非減少か（二分探索の前提）。O(T)"""
    return all(values[i] <= values[i + 1] for i in range(len(values) - 1))


def fire_age_binary(rows, target, check=True):
    """FIRE 達成年齢（二分探索）。資産が単調非減少でなければ ValueError

    check=False にすると前提の確認（O(T)）を省く。収益率 ≥ 0 と分かっているときだけ使う。
    """
    ages, assets = fm.assets_by_age(rows)
    if check and not is_nondecreasing(assets):
        raise ValueError("資産が単調非減少ではないので、二分探索は使えません（fire_age を使ってください）")
    lo, hi = 0, len(assets)                    # 答えの添字は [lo, hi) の中。hi = len は「未達成」
    while lo < hi:
        mid = (lo + hi) // 2
        if assets[mid] >= target:
            hi = mid                           # mid で到達 → 答えは mid 以前
        else:
            lo = mid + 1                       # mid で未到達 → 答えは mid より後
    return None if lo == len(assets) else ages[lo]


def years_to_fire(rows, target):
    """開始年齢から FIRE 達成までの年数（未達成なら None）"""
    age = fire_age(rows, target)
    return None if age is None else age - rows[0]["age"]


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：生活費を変更して、FIRE 目標資産と達成年齢を比べる。
# TODO 2：貯蓄率を変更する（生活費も変わる場合と、生活費は固定の場合を区別する）。
# TODO 3：投資収益率を変更する。
# TODO 4：取り崩し率を 3%・3.5%・4%・5% に変える。
# TODO 5：fire_age と fire_age_binary の結果・比較回数を比べる。収益率が負の年があるとどうなるか。
