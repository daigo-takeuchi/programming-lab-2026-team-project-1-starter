# D2：配送拠点・配送先データの読み込みと検証
#
# ■ データの表し方（すべて架空の地点）
#   locations = {"Depot": (0, 0), "A": (2, 3), "B": (5, 1), ...}   地点ID → (x, y) 座標
#   depot     = "Depot"                                              配送拠点のID
#
#   配送先は locations のうち、配送拠点以外のすべての地点。

import json
import math


def validate_locations(locations, depot):
    """地点データを検証する。不正なら ValueError

    - 配送拠点が存在する
    - 各座標が (x, y) の2つの数値で、NaN や無限大ではない
    （地点IDの一意性は辞書のキーなので保証される。JSON の重複キーは load_scenarios で検出する）
    """
    if depot not in locations:
        raise ValueError(f"配送拠点 {depot!r} が地点データにありません")
    for location_id, point in locations.items():
        if not isinstance(point, (tuple, list)) or len(point) != 2:
            raise ValueError(f"地点 {location_id} の座標は (x, y) の2つの値である必要があります（{point!r}）")
        for value in point:
            if not isinstance(value, (int, float)) or isinstance(value, bool):
                raise ValueError(f"地点 {location_id} の座標が数値ではありません（{point!r}）")
            if not math.isfinite(value):
                raise ValueError(f"地点 {location_id} の座標に NaN や無限大は使えません（{point!r}）")


def delivery_ids(locations, depot):
    """配送先のIDのリスト（配送拠点を除き、ID の昇順）"""
    return sorted(location_id for location_id in locations if location_id != depot)


def load_scenarios(path):
    """JSON ファイルからシナリオのリストを読み込む

    各シナリオは {"name", "description", "depot", "locations"} の辞書で、
    locations の座標はタプルに変換する。
    同じ階層に重複したキー（同じ地点IDが2回など）があれば ValueError にする
    （Python の json は、重複キーを黙って上書きしてしまうため）。
    """
    def reject_duplicates(pairs):
        keys = [key for key, _ in pairs]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        if duplicates:
            raise ValueError(f"JSON に重複したキーがあります：{duplicates}")
        return dict(pairs)

    with open(path, encoding="utf-8") as f:
        data = json.load(f, object_pairs_hook=reject_duplicates)

    scenarios = []
    for scenario in data["scenarios"]:
        validate_locations(scenario["locations"], scenario["depot"])
        points = {location_id: tuple(point) for location_id, point in scenario["locations"].items()}
        scenarios.append({**scenario, "locations": points})
    return scenarios
