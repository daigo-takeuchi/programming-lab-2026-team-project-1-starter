# G2：意思決定主体（Agent）としての架空の国家と、国家ペアの関係
#
# ・国家単位の属性（agents.make_country）と、国家ペア単位の属性（agents.make_relation）を区別する。
# ・国家はすべて架空（Country A〜E）。実在の国家・実際の外交や安全保障のデータは使わない。
#
# ■ 国家単位の属性
#   id                       国家の ID
#   cooperation_preference   協調を好む程度（0〜1）
#   trust                    他国一般への初期信頼度（0〜1）
#   economic_interdependence 経済的相互依存の程度（0〜1）
#   strategy                 意思決定戦略（STRATEGIES のどれか）
#   last_action              直前の行動（"C" / "N" / None）
#   cumulative_payoff        累積利得
#
# ■ 国家ペア単位の属性（関係）
#   trust      ペアの信頼度（0〜1。初期値は 2 国の trust の平均）
#   history    協調履歴 [(a の行動, b の行動), ...]
#   tension    緊張度（0〜1。状態の深刻度の移動平均）
#   state      現在の関係状態（Cooperation / Neutral / Tension / Conflict。抽象的なラベル）
#   dialogue   対話の有無、agreement 協定の有無、interdependence_bonus 経済協力による上乗せ

import copy
import json
from pathlib import Path

DATA_DIR = Path(__file__).resolve().parent / "data"
COUNTRIES_PATH = DATA_DIR / "sample_countries.json"

STRATEGIES = ("always_cooperate", "always_noncooperate", "tit_for_tat", "conditional")
STRATEGY_LABELS = {"always_cooperate": "Always Cooperate", "always_noncooperate": "Always Non-cooperate",
                   "tit_for_tat": "Tit-for-Tat", "conditional": "Conditional"}
UNIT_FIELDS = ("cooperation_preference", "trust", "economic_interdependence")


def validate_country(c):
    for k in ("id",) + UNIT_FIELDS + ("strategy",):
        if k not in c:
            raise ValueError(f"国家 {c.get('id', '?')}：項目 {k} がありません")
    for k in UNIT_FIELDS:
        v = c[k]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not 0 <= v <= 1:
            raise ValueError(f"国家 {c['id']}：{k} は 0〜1 にしてください（{v!r}）")
    if c["strategy"] not in STRATEGIES:
        raise ValueError(f"国家 {c['id']}：戦略 {c['strategy']!r} は {STRATEGIES} のどれかにしてください")
    return True


def make_country(cid, cooperation_preference=0.5, trust=0.5, economic_interdependence=0.5, strategy="conditional",
                 name=None):
    c = {"id": cid, "name": name or f"Country {cid}", "cooperation_preference": cooperation_preference,
         "trust": trust, "economic_interdependence": economic_interdependence, "strategy": strategy,
         "last_action": None, "cumulative_payoff": 0.0}
    validate_country(c)
    return c


def load_countries(path=COUNTRIES_PATH):
    """架空の国家のリスト（last_action・cumulative_payoff を初期化して返す）"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    out = []
    ids = set()
    for c in data["countries"]:
        validate_country(c)
        if c["id"] in ids:
            raise ValueError(f"国家 ID {c['id']} が重複しています")
        ids.add(c["id"])
        out.append(dict(c, last_action=None, cumulative_payoff=0.0))
    return out


def by_id(countries):
    return {c["id"]: c for c in countries}


def with_strategy(countries, strategy):
    """全国家の戦略を strategy にしたコピー"""
    if strategy not in STRATEGIES:
        raise ValueError(f"戦略 {strategy!r} がありません")
    return [dict(copy.deepcopy(c), strategy=strategy) for c in countries]


def with_trust(countries, trust):
    """全国家の初期信頼度を trust にしたコピー"""
    out = [dict(copy.deepcopy(c), trust=trust) for c in countries]
    for c in out:
        validate_country(c)
    return out


def make_relation(a, b, initial_state="Neutral", dialogue=False, agreement=False):
    """国家ペア (a, b) の関係。信頼度の初期値は 2 国の trust の平均"""
    return {"pair": (a["id"], b["id"]), "trust": (a["trust"] + b["trust"]) / 2, "history": [], "tension": 0.0,
            "state": initial_state, "dialogue": dialogue, "agreement": agreement, "interdependence_bonus": 0.0}


# TODO：国家に「交渉力」「国内の支持」など、新しい属性を追加する（Advanced）。
