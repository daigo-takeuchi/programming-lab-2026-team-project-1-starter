# D2：距離の計算
#
# ■ ルートの表し方（すべてのアルゴリズムで共通）
#   route = ["A", "B", "C", "D"]  … 配送先IDを訪問する順に並べたリスト
#   配送拠点はリストに含めない。総距離を計算するときに、出発点と帰着点として前後に付け足す。
#     Depot → A → B → C → D → Depot

import math

from locations import delivery_ids


def distance(locations, a, b):
    """2地点 a, b 間のユークリッド距離 sqrt((xa − xb)² + (ya − yb)²)"""
    for location_id in (a, b):
        if location_id not in locations:
            raise ValueError(f"地点 {location_id!r} は存在しません")
    (xa, ya), (xb, yb) = locations[a], locations[b]
    return math.hypot(xa - xb, ya - yb)


def check_route(locations, depot, route):
    """ルートが「すべての配送先をちょうど1回ずつ訪問する」ものか検証する。不正なら ValueError

    - 存在しない地点IDを含まない
    - 配送拠点を配送先として含まない
    - 同じ配送先を2回訪問しない
    - すべての配送先を含む
    """
    for location_id in route:
        if location_id == depot:
            raise ValueError("配送拠点はルートに含めません（出発・帰着として自動で付け足します）")
        if location_id not in locations:
            raise ValueError(f"地点 {location_id!r} は存在しません")
    if len(set(route)) != len(route):
        raise ValueError(f"同じ配送先を2回以上訪問しています：{list(route)}")
    missing = set(delivery_ids(locations, depot)) - set(route)
    if missing:
        raise ValueError(f"訪問していない配送先があります：{sorted(missing)}")


def route_distance(locations, depot, route):
    """ルートの総距離：配送拠点 → route の順に配送先 → 配送拠点

    配送先が0件（route = []）なら 0.0。
    """
    check_route(locations, depot, route)
    path = [depot] + list(route) + [depot]
    return sum(distance(locations, path[i], path[i + 1]) for i in range(len(path) - 1))


def format_route(depot, route):
    """表示用：Depot → A → B → Depot"""
    return " → ".join([depot] + list(route) + [depot])
