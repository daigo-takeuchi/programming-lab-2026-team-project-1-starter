# F2：貯蓄と複利による資産形成モデル（Python 標準ライブラリのみ）
#
#   Annual Savings = Annual Income × Savings Rate
#   Assets[t+1]    = Assets[t] × (1 + r) + Savings[t]
#
# ■ この教材での約束（README 8章）
#   ・金額の単位はすべて「万円」、年齢は「歳」（整数）。1 年 = 1 ステップ。
#   ・「a 歳の年」は、a 歳の誕生日から a+1 歳の誕生日までの 1 年間。
#       年初資産（start_assets）に収益率 r を適用し（investment_return = start_assets × r）、
#       年末に貯蓄額を拠出する（end_assets = start_assets × (1 + r) + savings）。
#   ・start_age の年から end_age − 1 歳の年までを計算する（T = end_age − start_age 年）。
#     end_age 歳の時点の資産は、最後の年（end_age − 1 歳）の年末資産。
#   ・「a 歳時点の資産」は a 歳の年の年初資産（= a − 1 歳の年の年末資産）とする（assets_by_age）。
#   ・所得・貯蓄率・収益率は毎年一定。税・社会保険料・インフレ・手数料は扱わない（README 19章）。

RATE_WARNING = 0.15   # これを超える収益率は教育用の仮定としても大きいので、README で注意している（例外にはしない）


def _check_age(name, value):
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} は整数（歳）で指定してください：{value!r}")
    if value < 0:
        raise ValueError(f"{name} は 0 以上にしてください：{value}")


def _check_number(name, value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError(f"{name} は数値で指定してください：{value!r}")


def validate(start_age, end_age, initial_assets, annual_income, savings_rate, annual_return):
    """入力を確認する（不正なら TypeError / ValueError）"""
    _check_age("start_age", start_age)
    _check_age("end_age", end_age)
    if not start_age < end_age:
        raise ValueError(f"開始年齢 {start_age} は終了年齢 {end_age} より小さくしてください")
    for name, v in [("initial_assets", initial_assets), ("annual_income", annual_income),
                    ("savings_rate", savings_rate), ("annual_return", annual_return)]:
        _check_number(name, v)
    if initial_assets < 0:
        raise ValueError(f"初期資産は 0 以上にしてください：{initial_assets}")
    if annual_income < 0:
        raise ValueError(f"年間所得は 0 以上にしてください：{annual_income}")
    if not 0 <= savings_rate <= 1:
        raise ValueError(f"貯蓄率は 0〜1 にしてください（0.2 = 20%）：{savings_rate}")
    if annual_return < -1:
        raise ValueError(f"収益率は -1 以上にしてください（-1 = 資産がすべて失われる）：{annual_return}")


def annual_savings(annual_income, savings_rate):
    """年間貯蓄額 = 年間所得 × 貯蓄率"""
    _check_number("annual_income", annual_income)
    _check_number("savings_rate", savings_rate)
    if annual_income < 0 or not 0 <= savings_rate <= 1:
        raise ValueError("年間所得は 0 以上、貯蓄率は 0〜1 にしてください")
    return annual_income * savings_rate


def living_expenses(annual_income, savings_rate):
    """所得のうち貯蓄しなかった分を、その年の生活費とみなす（税・社会保険料は考えない単純化）"""
    return annual_income - annual_savings(annual_income, savings_rate)


def savings_rate_for_expenses(annual_income, annual_expenses):
    """生活費を固定したときの貯蓄率 = (所得 − 生活費) / 所得"""
    if annual_income <= 0:
        raise ValueError("年間所得は正の値にしてください")
    if not 0 <= annual_expenses <= annual_income:
        raise ValueError("生活費は 0 以上、所得以下にしてください")
    return (annual_income - annual_expenses) / annual_income


def simulate_accumulation(start_age, end_age, initial_assets, annual_income, savings_rate, annual_return):
    """資産形成の年ごとの記録（辞書のリスト）。O(T)

    各要素：age, start_assets, income, savings, investment_return, end_assets
    """
    validate(start_age, end_age, initial_assets, annual_income, savings_rate, annual_return)
    savings = annual_savings(annual_income, savings_rate)
    rows = []
    assets = float(initial_assets)
    for age in range(start_age, end_age):                 # T 回のループ
        gain = assets * annual_return                      # 年初資産に収益率を適用（複利）
        end = assets + gain + savings                      # 年末に貯蓄を拠出
        rows.append({"age": age, "start_assets": assets, "income": annual_income, "savings": savings,
                     "investment_return": gain, "end_assets": end})
        assets = end
    return rows


def assets_by_age(rows):
    """年齢 → その年齢「時点」（年初）の資産 の対応を、2 つのリストで返す：(ages, assets)

    ages = [start_age, ..., end_age]（T + 1 個）。最後の値は end_age 時点（最後の年の年末）の資産。
    """
    if not rows:
        return [], []
    ages = [r["age"] for r in rows] + [rows[-1]["age"] + 1]
    assets = [r["start_assets"] for r in rows] + [rows[-1]["end_assets"]]
    return ages, assets


def assets_at(rows, age):
    """age 歳時点の資産（計算期間外なら ValueError）"""
    ages, assets = assets_by_age(rows)
    if not ages or not ages[0] <= age <= ages[-1]:
        raise ValueError(f"{age} 歳は計算期間の外です")
    return assets[age - ages[0]]


def total_contributions(rows):
    """拠出した貯蓄の合計（初期資産を除く）"""
    s = 0.0
    for r in rows:
        s += r["savings"]
    return s


def total_investment_return(rows):
    """投資収益の合計（複利の効果）"""
    s = 0.0
    for r in rows:
        s += r["investment_return"]
    return s


# ------------------------------------------------------------
# シナリオ（data/sample_scenarios.json）
# ------------------------------------------------------------
import copy
import json
import os
import warnings

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_scenarios.json")
SCENARIO_KEYS = ["start_age", "initial_assets", "annual_income", "savings_rate", "annual_return", "annual_expenses"]


def load_scenarios(path=DATA_FILE):
    """(シナリオのリスト, 共通条件の辞書) を返す。各シナリオの値を検証する"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    settings = data["settings"]
    for s in data["scenarios"]:
        validate_scenario(s, settings)
    return data["scenarios"], settings


def validate_scenario(s, settings):
    for key in SCENARIO_KEYS:
        if key not in s:
            raise KeyError(f"シナリオ {s.get('name')} に {key} がありません")
    validate(s["start_age"], settings["accumulation_end_age"], s["initial_assets"], s["annual_income"],
             s["savings_rate"], s["annual_return"])
    _check_number("annual_expenses", s["annual_expenses"])
    if s["annual_expenses"] < 0:
        raise ValueError("年間生活費は 0 以上にしてください")
    current = living_expenses(s["annual_income"], s["savings_rate"])
    if abs(current - s["annual_expenses"]) > 1e-6:
        warnings.warn(f"{s.get('name')}: 生活費 {s['annual_expenses']} が 所得 × (1 − 貯蓄率) = {current:g} と一致しません"
                      "（リタイア後の生活費を現役時と変える仮定なら問題ありません）", UserWarning, stacklevel=2)


def with_changes(scenario, **changes):
    """シナリオのコピーを作り、一部の値を変える（元のシナリオは変更しない）"""
    s = copy.deepcopy(scenario)
    s.update(changes)
    return s


def accumulate(scenario, end_age):
    """シナリオの資産形成を end_age まで計算する"""
    return simulate_accumulation(scenario["start_age"], end_age, scenario["initial_assets"],
                                 scenario["annual_income"], scenario["savings_rate"], scenario["annual_return"])


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：所得を毎年 g% 上昇させる（F1 の年齢別所得モデルとの連携は Advanced E）。
# TODO 2：収益を年初ではなく、年の途中で拠出した分にも一部付くようにする（拠出のタイミングの違い）。
# TODO 3：年ごとに違う収益率のリストを受け取れるようにする（Advanced A・B の準備）。
