# F4：パートナーモデル（2人の意思決定主体）と、架空データの読み込み・検証
#
# ・2人を Partner A・Partner B と呼ぶ。A・B は区別のための名前で、性別や役割を意味しない。
# ・データはすべて教育用の架空の値（data/sample_partnerships.json）。
# ・パートナー 1 人は辞書 1 つで表す。2 人は {"A": {...}, "B": {...}} の辞書にまとめる。

import copy
import json
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent / "data" / "sample_partnerships.json"

PARTNERS = ("A", "B")
FIELDS = (
    "id",
    "annual_income",              # 年収（万円・架空）
    "weekly_work_hours",          # 1 週間の労働時間
    "available_housework_hours",  # 1 週間に家事に使える時間の上限
    "preferred_housework_share",  # 自分が担当したい家事の割合（0〜1）
    "preferred_financial_share",  # 自分が負担したい生活費の割合（0〜1）
    "communication_score",        # コミュニケーションの架空の指標（0〜1）
    "fairness_weight",            # 公平性を重視する程度（0〜1）
    "satisfaction",               # 関係満足度（0〜1）。シミュレーションの初期値
)
NON_NEGATIVE = ("annual_income", "weekly_work_hours", "available_housework_hours")
UNIT_INTERVAL = ("preferred_housework_share", "preferred_financial_share", "communication_score",
                 "fairness_weight", "satisfaction")
HOUSEWORK_RULES = ("equal", "work_hours", "income", "preference")   # 数値（0〜1）なら固定の分担率
FINANCIAL_RULES = ("equal", "income", "preference")


def other(pid):
    """相手の ID（"A" ↔ "B"）"""
    return "B" if pid == "A" else "A"


# ------------------------------------------------------------
# 入力検証
# ------------------------------------------------------------
def validate_partner(p):
    """パートナー 1 人分を検証する。問題があれば ValueError"""
    missing = [k for k in FIELDS if k not in p]
    if missing:
        raise ValueError(f"パートナー {p.get('id', '?')}：項目がありません {missing}")
    for k in NON_NEGATIVE:
        v = p[k]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
            raise ValueError(f"パートナー {p['id']}：{k} は 0 以上の数値にしてください（{v!r}）")
    for k in UNIT_INTERVAL:
        v = p[k]
        if not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 1:
            raise ValueError(f"パートナー {p['id']}：{k} は 0〜1 にしてください（{v!r}）")
    if p["weekly_work_hours"] > 168 or p["available_housework_hours"] > 168:
        raise ValueError(f"パートナー {p['id']}：1 週間は 168 時間です")
    return True


def validate_partners(partners):
    """2 人分 {"A": {...}, "B": {...}} を検証する"""
    if set(partners) != set(PARTNERS):
        raise ValueError(f"パートナーは A と B の 2 人にしてください（{sorted(partners)}）")
    for pid in PARTNERS:
        validate_partner(partners[pid])
    return True


def validate_household(household):
    for k in ("total_housework_hours", "annual_expenses"):
        v = household.get(k)
        if not isinstance(v, (int, float)) or isinstance(v, bool) or v < 0:
            raise ValueError(f"household.{k} は 0 以上の数値にしてください（{v!r}）")
    return True


def validate_rule(rule, allowed):
    if isinstance(rule, (int, float)) and not isinstance(rule, bool):
        if not 0 <= rule <= 1:
            raise ValueError(f"分担率は 0〜1 にしてください（{rule!r}）")
        return True
    if rule not in allowed:
        raise ValueError(f"分担ルール {rule!r} は {allowed} か 0〜1 の数値にしてください")
    return True


def validate_scenario(sc):
    for k in ("id", "label", "housework_rule", "financial_rule", "strategy", "partners", "household"):
        if k not in sc:
            raise ValueError(f"シナリオ {sc.get('id', '?')}：項目 {k} がありません")
    validate_partners(sc["partners"])
    validate_household(sc["household"])
    validate_rule(sc["housework_rule"], HOUSEWORK_RULES)
    validate_rule(sc["financial_rule"], FINANCIAL_RULES)
    return True


# ------------------------------------------------------------
# 読み込み
# ------------------------------------------------------------
def load_data(path=DATA_PATH):
    with open(path, encoding="utf-8") as f:
        return json.load(f)


def build_scenario(data, spec):
    """base_partners と household に、シナリオの指定（コミュニケーションなど）を重ねた完全なシナリオを作る"""
    partners = copy.deepcopy(data["base_partners"])
    for pid, value in spec.get("communication", {}).items():
        partners[pid]["communication_score"] = value
    for pid, changes in spec.get("partner_overrides", {}).items():
        partners[pid].update(changes)
    household = dict(data["household"])
    household.update(spec.get("household_overrides", {}))
    sc = {k: v for k, v in spec.items() if k not in ("communication", "partner_overrides", "household_overrides")}
    sc["partners"] = partners
    sc["household"] = household
    validate_scenario(sc)
    return sc


def load_scenarios(path=DATA_PATH):
    """シナリオ A〜D を、パートナー・家計の値を埋めた完全な形で返す（リスト）"""
    data = load_data(path)
    validate_partners(data["base_partners"])
    validate_household(data["household"])
    return [build_scenario(data, spec) for spec in data["scenarios"]]


def load_stress_events(path=DATA_PATH):
    """ストレスイベントの組 {名前: [イベント, ...]}"""
    return copy.deepcopy(load_data(path)["stress_event_sets"])


def scenario_by_id(scenarios, sid):
    for sc in scenarios:
        if sc["id"] == sid:
            return sc
    raise KeyError(f"シナリオ {sid!r} がありません")


def with_partner_changes(scenario, pid, **changes):
    """1 人の値だけを変えたシナリオのコピー（元のシナリオは変えない）"""
    sc = copy.deepcopy(scenario)
    sc["partners"][pid].update(changes)
    validate_scenario(sc)
    return sc


def with_communication(scenario, level):
    """2 人のコミュニケーション指標を level にしたコピー"""
    sc = copy.deepcopy(scenario)
    for pid in PARTNERS:
        sc["partners"][pid]["communication_score"] = level
    validate_scenario(sc)
    return sc


# ------------------------------------------------------------
# Advanced E：F3 で成立したペアを F4 の初期条件にする（最小限の入口）
# ------------------------------------------------------------
F3_FORMAT_VERSION = "f3-to-f4/1"
F3_PAIR_FIELDS = ("pair_id", "participant_ids", "initial_compatibility", "initial_satisfaction",
                  "matching_algorithm")


def validate_f3_export(data):
    """F3 の export_pairs_for_f4 が出力する形式（f3-to-f4/1）かを確認する。F3 のコードは import しない"""
    if data.get("format") != F3_FORMAT_VERSION:
        raise ValueError(f"形式 {data.get('format')!r} は {F3_FORMAT_VERSION!r} ではありません")
    for pair in data.get("pairs", []):
        missing = [k for k in F3_PAIR_FIELDS if k not in pair]
        if missing:
            raise ValueError(f"ペア {pair.get('pair_id', '?')}：項目がありません {missing}")
        if len(pair["participant_ids"]) != 2:
            raise ValueError(f"ペア {pair['pair_id']}：参加者は 2 人にしてください")
        if not 0 <= pair["initial_compatibility"] <= 1:
            raise ValueError(f"ペア {pair['pair_id']}：initial_compatibility は 0〜1 にしてください")
    return True


def load_f3_pairs(path):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    validate_f3_export(data)
    return data


def scenario_from_f3_pair(pair, template):
    """F3 のペア 1 組から F4 のシナリオを作る

    ・家事・所得などの条件は F3 にないので template（F4 のシナリオ）から借りる。
    ・2 人の初期満足度 = F3 の initial_satisfaction（なければ initial_compatibility）。
    TODO（Advanced E）：初期適合度を、希望分担やコミュニケーションにも反映させる。
    """
    sc = copy.deepcopy(template)
    init = pair.get("initial_satisfaction")
    if init is None:
        init = pair["initial_compatibility"]
    for pid, participant in zip(PARTNERS, pair["participant_ids"]):
        sc["partners"][pid]["satisfaction"] = round(float(init), 4)
        sc["partners"][pid]["source_participant"] = participant
    sc["id"] = f"F3-{pair['pair_id']}"
    sc["label"] = f"F3 pair {pair['pair_id']} ({pair['matching_algorithm']})"
    sc["f3"] = {k: pair[k] for k in F3_PAIR_FIELDS}
    validate_scenario(sc)
    return sc
