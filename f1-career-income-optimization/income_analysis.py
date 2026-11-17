# F1：生涯所得・累積純収入・割引現在価値（NPV）・投資回収年齢
#
#   Lifetime Gross Income  = Σ_a 年収(a)
#   Cumulative Net Income  = Σ_a 年収(a) − Σ_a キャリア関連費用(a)      ← 税・社会保険料を引いた「手取り」ではない
#   NPV                    = Σ_t CashFlow_t / (1 + r)^t                  （t = 年齢 − base_age。base_age の年は t = 0）
#
# どれも年齢別のリストを 1 回ずつたどるので O(T)（T = 計算する年数）。

import career_model as cm
import scenarios as sc

DEFAULT_DISCOUNT_RATE = 0.03   # 架空の例（README 8章）


def total(values):
    """リストの合計（ループで累積する。空なら 0）"""
    s = 0.0
    for v in values:
        s += v
    return s


def cumulative(values):
    """累積和のリスト：[v0, v0+v1, v0+v1+v2, ...]"""
    out, s = [], 0.0
    for v in values:
        s += v
        out.append(s)
    return out


def lifetime_gross_income(scenario, base_age=cm.BASE_AGE):
    """生涯所得（額面の年収の合計、万円）"""
    return total(sc.incomes(scenario, base_age))


def career_costs(scenario, base_age=cm.BASE_AGE):
    """キャリア関連費用（進学・資格取得・転職）の合計（万円）"""
    return total(sc.costs(scenario, base_age))


def cumulative_net_income(scenario, base_age=cm.BASE_AGE):
    """累積純収入 = 生涯所得 − キャリア関連費用（万円）。手取りではない"""
    return total(sc.cashflows(scenario, base_age))


def npv(cashflows, rate=DEFAULT_DISCOUNT_RATE):
    """割引現在価値：Σ CashFlow_t / (1 + rate)^t（t = 0, 1, 2, ...）"""
    if isinstance(rate, bool) or not isinstance(rate, (int, float)):
        raise TypeError("割引率は数値で指定してください")
    if rate <= -1:
        raise ValueError("割引率は -1 より大きくしてください")
    value = 0.0
    for t, cf in enumerate(cashflows):
        value += cf / (1 + rate) ** t
    return value


def scenario_npv(scenario, rate=DEFAULT_DISCOUNT_RATE, base_age=cm.BASE_AGE):
    """シナリオのキャッシュフロー（年収 − 費用）の NPV（base_age 歳の時点の価値、万円）"""
    return npv(sc.cashflows(scenario, base_age), rate)


def evaluate(scenario, rate=DEFAULT_DISCOUNT_RATE, base_age=cm.BASE_AGE):
    """1 つのシナリオの評価指標をまとめた辞書"""
    gross = lifetime_gross_income(scenario, base_age)
    cost = career_costs(scenario, base_age)
    return {"name": scenario["name"], "label": scenario.get("label", scenario["name"]),
            "gross": gross, "costs": cost, "net": gross - cost,
            "npv": scenario_npv(scenario, rate, base_age), "discount_rate": rate}


def payback_age(scenario, baseline, base_age=cm.BASE_AGE):
    """scenario の累積純収入が、比較対象 baseline に追いつく（以上になる）最初の年齢

    返り値（辞書）
      status       : "recovered"（回収できた）、"not_recovered"（退職までに回収できない）、
                     "never_behind"（一度も baseline を下回らない＝回収すべき差がない）
      payback_age  : 回収できた年齢（それ以外は None）
      behind_from  : 初めて baseline を下回った年齢（never_behind なら None）
      final_gap    : 退職時の累積純収入の差（scenario − baseline、万円）

    差は単調に増えるとは限らない（転職などで途中で逆転し得る）ので、二分探索ではなく先頭から線形探索する。
    """
    a = cumulative(sc.cashflows(scenario, base_age))
    b = cumulative(sc.cashflows(baseline, base_age))
    if len(a) != len(b):
        raise ValueError("比較する 2 つのシナリオの計算期間（退職年齢）をそろえてください")
    gap = [x - y for x, y in zip(a, b)]

    behind = next((i for i, g in enumerate(gap) if g < 0), None)
    result = {"payback_age": None, "behind_from": None, "final_gap": gap[-1] if gap else 0.0}
    if behind is None:
        result["status"] = "never_behind"
        return result
    result["behind_from"] = base_age + behind
    for i in range(behind, len(gap)):
        if gap[i] >= 0:
            result.update(status="recovered", payback_age=base_age + i)
            return result
    result["status"] = "not_recovered"
    return result


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：割引後の累積キャッシュフローで投資回収年齢を求める（割引回収期間）。
# TODO 2：基準年齢を 18 歳ではなく、今の自分の年齢にした NPV を計算する。
# TODO 3：回収した「あと」に再び追い抜かれる場合（gap が再び負になる）を検出する。
