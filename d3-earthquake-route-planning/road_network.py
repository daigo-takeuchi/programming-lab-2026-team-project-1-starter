# D3：道路ネットワーク（重み付き無向グラフ）の読み込み・検証
#
# ■ データの表し方（すべて架空）
#   network = {
#       "nodes": {"SJK": {"name": "Shinjuku", "x": 0, "y": 5}, ...},   ノードID → 地区名と架空の座標
#       "roads": [{"from": "SJK", "to": "IKB", "distance": 4.4,
#                  "status": "open", "cost_multiplier": 1.0}, ...],   道路（双方向に通行できる）
#   }
#
# ■ 通行状態（status）
#   "open"           … 一般車両・緊急車両とも通行できる
#   "closed"         … どちらも通行できない（物理的に通れない）
#   "emergency_only" … 緊急車両だけが通行できる
#   ※ 教育用に定義した架空の規則であり、実際の法令や災害時の交通規制を再現したものではない。
#
# ■ 移動コスト = distance × cost_multiplier（混雑などで通行に時間がかかる道路は倍率を大きくする）

import json
import math

STATUSES = ("open", "closed", "emergency_only")
VEHICLES = ("general", "emergency")


def _is_positive_finite(value):
    return (isinstance(value, (int, float)) and not isinstance(value, bool)
            and math.isfinite(value) and value > 0)


def road_key(u, v):
    """無向道路の識別子：両端のIDを小さい順に並べたタプル（u–v と v–u は同じ道路）"""
    return tuple(sorted((u, v)))


def validate_network(network):
    """道路ネットワークを検証する。不正なら ValueError

    - 道路の始点・終点が存在する
    - 自己ループ（始点 = 終点）がない
    - 同じ無向道路が重複していない
    - 距離・コスト倍率が正の有限数
    - 通行状態が定義済みの値
    孤立ノード（道路がつながっていないノード）は許可する。
    （ノードIDの一意性は辞書のキーなので保証される。JSON の重複キーは load_network で検出する）
    """
    nodes = network["nodes"]
    for node_id, node in nodes.items():
        for axis in ("x", "y"):
            value = node.get(axis)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not math.isfinite(value):
                raise ValueError(f"ノード {node_id} の座標 {axis} が不正です（{value!r}）")
    seen = set()
    for road in network["roads"]:
        u, v = road["from"], road["to"]
        for endpoint in (u, v):
            if endpoint not in nodes:
                raise ValueError(f"道路 {u}–{v} の端点 {endpoint!r} は存在しないノードです")
        if u == v:
            raise ValueError(f"自己ループの道路があります（{u}–{v}）")
        if road_key(u, v) in seen:
            raise ValueError(f"道路 {u}–{v} が重複しています")
        seen.add(road_key(u, v))
        if not _is_positive_finite(road["distance"]):
            raise ValueError(f"道路 {u}–{v} の距離は正の有限数である必要があります（{road['distance']!r}）")
        if not _is_positive_finite(road["cost_multiplier"]):
            raise ValueError(f"道路 {u}–{v} のコスト倍率は正の有限数である必要があります（{road['cost_multiplier']!r}）")
        if road["status"] not in STATUSES:
            raise ValueError(f"道路 {u}–{v} の通行状態 {road['status']!r} は定義されていません")


def load_network(path):
    """JSON ファイルから道路ネットワークを読み込み、検証する

    同じ階層に重複したキー（同じノードIDが2回など）があれば ValueError にする
    （Python の json は、重複キーを黙って上書きしてしまうため）。
    """
    def reject_duplicates(pairs):
        keys = [key for key, _ in pairs]
        duplicates = sorted({key for key in keys if keys.count(key) > 1})
        if duplicates:
            raise ValueError(f"JSON に重複したキーがあります：{duplicates}")
        return dict(pairs)

    with open(path, encoding="utf-8") as f:
        network = json.load(f, object_pairs_hook=reject_duplicates)
    validate_network(network)
    return network


def node_ids(network):
    """ノードIDのリスト（昇順）"""
    return sorted(network["nodes"])


def roads(network):
    """道路のリスト"""
    return network["roads"]


def node_name(network, node_id):
    """ノードの地区名"""
    return network["nodes"][node_id]["name"]


def find_road(network, u, v):
    """u–v の道路を返す（なければ None）"""
    key = road_key(u, v)
    for road in network["roads"]:
        if road_key(road["from"], road["to"]) == key:
            return road
    return None


def can_pass(road, vehicle):
    """車両 vehicle（"general" または "emergency"）がその道路を通行できるか"""
    if vehicle not in VEHICLES:
        raise ValueError(f"車両の種類は {VEHICLES} のどれかです（{vehicle!r}）")
    if road["status"] == "open":
        return True
    if road["status"] == "emergency_only":
        return vehicle == "emergency"
    return False                        # closed は緊急車両も通行できない


def road_distance(road):
    """道路の距離"""
    return road["distance"]


def road_cost(road):
    """道路の移動コスト = 距離 × コスト倍率"""
    return road["distance"] * road["cost_multiplier"]


def adjacency(network, vehicle):
    """車両 vehicle が通行できる道路だけを使った隣接リスト {ノード: [(隣のノード, 道路), ...]}

    無向道路なので、1本の道路を両方向に登録する。孤立ノードは空のリストになる。
    隣のノードはIDの昇順に並べる（探索の順序が毎回同じになる）。
    """
    adj = {node_id: [] for node_id in network["nodes"]}
    for road in network["roads"]:
        if can_pass(road, vehicle):
            adj[road["from"]].append((road["to"], road))
            adj[road["to"]].append((road["from"], road))
    for node_id in adj:
        adj[node_id].sort(key=lambda pair: pair[0])
    return adj


def neighbors(network, node_id, vehicle):
    """車両 vehicle が node_id から1本の道路で行けるノードのリスト"""
    return [other for other, _ in adjacency(network, vehicle)[node_id]]


def euclidean_lower_bound_violations(network):
    """道路の距離が、両端ノードの直線距離（ユークリッド距離）より短い道路のリスト

    空なら、すべての道路で「距離 ≥ 直線距離」が成り立つ。
    さらにコスト倍率がすべて 1 以上なら、直線距離を移動コストの下界として使える（A* の許容性）。
    """
    result = []
    for road in network["roads"]:
        a, b = network["nodes"][road["from"]], network["nodes"][road["to"]]
        if road["distance"] < math.hypot(a["x"] - b["x"], a["y"] - b["y"]) - 1e-9:
            result.append(road)
    return result
