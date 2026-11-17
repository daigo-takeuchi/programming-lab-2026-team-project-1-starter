# D2：配送ルートの探索（ランダム探索・最近傍法・全探索）
#
# どの関数も同じ形の辞書を返す。
#   route     : 配送先IDの訪問順のリスト（配送拠点は含めない）
#   distance  : 総移動距離（配送拠点からの出発・帰着を含む）
#   evaluated : 総距離を計算した候補ルートの数
#
# 2-opt は two_opt.py（学生の課題）。

import random
from itertools import permutations

from distance import distance, route_distance
from locations import delivery_ids

MAX_BRUTE_FORCE = 8         # 全探索で扱う配送先数の上限（8! = 40,320 通り）


def random_search(locations, depot, trials, seed=None):
    """ランダム探索：ランダムな訪問順を trials 個作り、最も短いルートを返す

    同じルートが何度も生成されることもある（重複を除いていない）。
    seed を指定すると、同じ結果を再現できる。
    """
    if not isinstance(trials, int) or isinstance(trials, bool) or trials < 1:
        raise ValueError(f"試行回数は1以上の整数である必要があります（{trials!r}）")
    rng = random.Random(seed)
    deliveries = delivery_ids(locations, depot)
    best_route, best_distance = None, None
    for _ in range(trials):
        route = rng.sample(deliveries, len(deliveries))
        d = route_distance(locations, depot, route)
        if best_distance is None or d < best_distance:
            best_route, best_distance = route, d
    return {"route": best_route, "distance": best_distance, "evaluated": trials}


def nearest_neighbor(locations, depot):
    """最近傍法：今いる地点から最も近い未訪問の配送先へ移動することを繰り返す

    1. 配送拠点から出発する
    2. 未訪問の配送先の中で、今いる地点から最も近いものを選ぶ（同じ距離なら ID の小さい方）
    3. その地点へ移動する
    4. すべての配送先を訪問するまで繰り返し、最後に配送拠点へ戻る
    """
    unvisited = set(delivery_ids(locations, depot))
    current = depot
    route = []
    while unvisited:
        current = min(unvisited, key=lambda location_id: (distance(locations, current, location_id), location_id))
        route.append(current)
        unvisited.remove(current)
    return {"route": route, "distance": route_distance(locations, depot, route), "evaluated": 1}


def brute_force(locations, depot, max_deliveries=MAX_BRUTE_FORCE):
    """全探索：すべての訪問順（N! 通り）を調べ、総距離が最小のルートを返す

    配送先数が max_deliveries を超える場合は、時間がかかりすぎるので ValueError にする。
    同じ距離のルートが複数あれば、列挙した順で最初のもの（ID の辞書順）を返す。
    （逆向きのルートも別の候補として数えている。対称な TSP では同じ距離になる）
    """
    deliveries = delivery_ids(locations, depot)
    if len(deliveries) > max_deliveries:
        raise ValueError(f"配送先数 {len(deliveries)} が全探索の上限 {max_deliveries} を超えています")
    best_route, best_distance = None, None
    evaluated = 0
    for route in permutations(deliveries):
        evaluated += 1
        d = route_distance(locations, depot, route)
        if best_distance is None or d < best_distance:
            best_route, best_distance = list(route), d
    return {"route": best_route, "distance": best_distance, "evaluated": evaluated}


def optimality_gap(value, optimum):
    """最適解との差（%）= (アルゴリズムの距離 − OPT) / OPT × 100

    OPT が 0 のとき（すべての配送先が配送拠点と同じ位置など）は、比が定義できないので None を返す。
    """
    if optimum == 0:
        return None
    return (value - optimum) / optimum * 100
