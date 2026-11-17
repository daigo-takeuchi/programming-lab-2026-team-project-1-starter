# D3：地震シナリオ（道路閉鎖・交通規制・通行コストの増加）
#
# Core Research では、シナリオをあらかじめ決めた固定データとして定義する（毎回同じ結果になる）。
# 道路は両端のノードIDの組で指定する（順序は問わない）。
# ※ すべて架空の設定であり、実際の災害時の通行可否や交通規制を示すものではない。
#
# シナリオを適用すると、元のネットワークは変更せず、独立したコピーを返す。

import copy

from road_network import find_road

SCENARIOS = {
    "before": {
        "title": "Before Earthquake（地震発生前：すべての道路が通常通行可能）",
        "closed": [],
        "emergency_only": [],
        "cost_multipliers": {},
    },
    "closure": {
        "title": "After Earthquake: Road Closure（一部道路の完全閉鎖）",
        "closed": [("UEN", "KOT"), ("TKY", "KOT")],
        "emergency_only": [],
        "cost_multipliers": {},
    },
    "regulation": {
        "title": "After Earthquake: Traffic Regulation（緊急車両のみ通行可能な道路）",
        "closed": [],
        "emergency_only": [("IKB", "UEN")],
        "cost_multipliers": {},
    },
    "congestion": {
        "title": "After Earthquake: Congestion（通行コストの増加）",
        "closed": [],
        "emergency_only": [],
        "cost_multipliers": {("UEN", "KOT"): 2.0, ("SJK", "TKY"): 1.5},
    },
}


def apply_changes(network, closed=(), emergency_only=(), cost_multipliers=None):
    """道路の状態を変更したネットワークのコピーを返す（元のネットワークは変更しない）

    closed           : 完全閉鎖にする道路 [(u, v), ...]
    emergency_only   : 緊急車両のみ通行可能にする道路 [(u, v), ...]
    cost_multipliers : コスト倍率を変更する道路 {(u, v): 倍率, ...}（正の数）
    存在しない道路を指定したら KeyError。
    """
    new_network = copy.deepcopy(network)

    def road_of(u, v):
        road = find_road(new_network, u, v)
        if road is None:
            raise KeyError(f"道路 {u}–{v} は存在しません")
        return road

    for u, v in emergency_only:
        road_of(u, v)["status"] = "emergency_only"
    for u, v in closed:
        road_of(u, v)["status"] = "closed"          # 閉鎖は規制より優先する
    for (u, v), multiplier in (cost_multipliers or {}).items():
        if not isinstance(multiplier, (int, float)) or isinstance(multiplier, bool) or not multiplier > 0:
            raise ValueError(f"コスト倍率は正の数である必要があります（{multiplier!r}）")
        road_of(u, v)["cost_multiplier"] = multiplier
    return new_network


def apply_scenario(network, name):
    """定義済みのシナリオ（SCENARIOS のキー）を適用したネットワークのコピーを返す"""
    scenario = SCENARIOS[name]
    return apply_changes(network, scenario["closed"], scenario["emergency_only"], scenario["cost_multipliers"])


# ------------------------------------------------------------
# 学生が取り組む課題（Advanced A・C）
# ------------------------------------------------------------
# TODO（Advanced A）：閉鎖率 p と乱数シードを指定して、ランダムに道路を閉鎖する関数を作る。
# TODO（Advanced C）：時刻ごとに道路の状態が変わる（閉鎖・復旧）シナリオを表現する。
