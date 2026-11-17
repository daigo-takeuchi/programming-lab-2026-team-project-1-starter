# F2：リタイア後の資産の取り崩し
#
#   Assets[t+1] = Assets[t] × (1 + r) − Annual Expenses
#
# ■ この教材での約束（README 9章）
#   ・年初資産に収益率を適用し、年末に生活費を取り崩す。
#   ・資産が足りない年は、あるだけを取り崩して資産は 0 になる（負にはしない＝「0 で打ち切る」方式）。
#     足りなかった額は shortfall に記録する。資産が 0 になった後の年も記録を続ける（収益 0、取り崩し 0）。
#   ・資産枯渇年齢：年末資産が 0 以下になった最初の年の年齢。最後まで残れば None。
#   ・生活費・収益率は毎年一定（インフレ・税・年金は扱わない）。

import financial_model as fm


def simulate_withdrawal(start_age, end_age, initial_assets, annual_expenses, annual_return):
    """リタイア後の年ごとの記録（辞書のリスト）。O(T)

    各要素：age, start_assets, investment_return, withdrawal, shortfall, end_assets, depleted
    """
    fm._check_age("start_age", start_age)
    fm._check_age("end_age", end_age)
    if not start_age < end_age:
        raise ValueError("リタイア開始年齢は、シミュレーション終了年齢より小さくしてください")
    for name, v in [("initial_assets", initial_assets), ("annual_expenses", annual_expenses),
                    ("annual_return", annual_return)]:
        fm._check_number(name, v)
    if initial_assets < 0 or annual_expenses < 0:
        raise ValueError("資産・生活費は 0 以上にしてください")
    if annual_return < -1:
        raise ValueError("収益率は -1 以上にしてください")

    rows = []
    assets = float(initial_assets)
    for age in range(start_age, end_age):
        gain = assets * annual_return
        available = assets + gain
        withdrawal = min(annual_expenses, available)      # あるだけしか取り崩せない
        end = available - withdrawal
        if end < 1e-9:                                     # 浮動小数点の誤差で負やごく小さい値になるのを防ぐ
            end = 0.0
        rows.append({"age": age, "start_assets": assets, "investment_return": gain, "withdrawal": withdrawal,
                     "shortfall": annual_expenses - withdrawal, "end_assets": end,
                     "depleted": end <= 0 and annual_expenses > 0})
        assets = end
    return rows


def depletion_age(rows):
    """資産が枯渇した（年末資産が 0 以下になった）最初の年の年齢。最後まで枯渇しなければ None"""
    for r in rows:
        if r["depleted"]:
            return r["age"]
    return None


def years_sustained(rows):
    """生活費を全額まかなえた年数（枯渇した年は、全額まかなえていれば数える）"""
    n = 0
    for r in rows:
        if r["shortfall"] > 1e-9:
            break
        n += 1
    return n


def is_sustainable(rows):
    """シミュレーション終了まで、毎年の生活費を全額まかなえたか（RQ5 の「持続」の定義の 1 つ）"""
    return years_sustained(rows) == len(rows)


def total_shortfall(rows):
    """まかなえなかった生活費の合計"""
    s = 0.0
    for r in rows:
        s += r["shortfall"]
    return s


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：リタイア開始年齢を変更する。
# TODO 2：リタイア時点の資産を変更する。
# TODO 3：生活費を変更する（年齢とともに変わる生活費のリストにする）。
# TODO 4：投資収益率を変更する（リタイア後は低めにする、など）。
# TODO 5：資産枯渇年齢を比較する。年金（一定年齢から毎年 xx 万円の収入）を加える（Advanced D）。
