# D1：カバー人口・人口カバー率の計算
#
# ■ データの表し方（すべて架空の地域）
#   areas  = {"A": 1200, "B": 800, ...}             居住エリアID → 人口
#   towers = {"T1": {"A", "B"}, "T2": {"B", "C"}, ...}  基地局候補ID → カバーできるエリアの集合
#
# 同じエリアを複数の基地局がカバーしても、その人口は1回だけ数える（集合の和集合を使う）。

import json


def validate_region(areas, towers):
    """地域データを検証する。不正なら ValueError

    - 人口は 0 以上の整数
    - 各基地局のカバー範囲は、定義済みのエリアだけからなる
    （基地局IDの一意性は、辞書のキーなので保証される。JSON の重複キーは load_scenarios で検出する）
    """
    for area, population in areas.items():
        if not isinstance(population, int) or isinstance(population, bool) or population < 0:
            raise ValueError(f"エリア {area} の人口が不正です（{population!r}）")
    for tower, covered in towers.items():
        unknown = set(covered) - set(areas)
        if unknown:
            raise ValueError(f"基地局 {tower} が未定義のエリアをカバーしています：{sorted(unknown)}")


def check_k(k, towers):
    """設置できる基地局数 K を検証する（0 以上の整数で、候補数 M 以下）"""
    if not isinstance(k, int) or isinstance(k, bool) or k < 0:
        raise ValueError(f"K は 0 以上の整数である必要があります（{k!r}）")
    if k > len(towers):
        raise ValueError(f"K = {k} が基地局候補数 M = {len(towers)} を超えています")


def covered_areas(towers, selected):
    """選んだ基地局がカバーするエリアの集合（和集合）

    存在しない基地局ID、同じ基地局の重複選択は ValueError。
    """
    if len(set(selected)) != len(selected):
        raise ValueError(f"同じ基地局が複数回選ばれています：{list(selected)}")
    result = set()
    for tower in selected:
        if tower not in towers:
            raise ValueError(f"基地局 {tower} は存在しません")
        result |= towers[tower]
    return result


def total_population(areas):
    """総人口"""
    return sum(areas.values())


def covered_population(areas, towers, selected):
    """カバー人口：カバーされたエリアの人口の合計（重複して数えない）"""
    return sum(areas[area] for area in covered_areas(towers, selected))


def coverage_rate(areas, towers, selected):
    """人口カバー率 = カバー人口 / 総人口（総人口が 0 のときは 0.0 とする）"""
    total = total_population(areas)
    if total == 0:
        return 0.0
    return covered_population(areas, towers, selected) / total


def load_scenarios(path):
    """JSON ファイルから地域データ（シナリオ）のリストを読み込む

    各シナリオは {"name", "description", "k", "areas", "towers"} の辞書。
    towers のカバー範囲はリストから集合に変換する。
    同じ階層に重複したキー（例：同じ基地局IDが2回）があれば ValueError にする
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
        towers = {tower: set(covered) for tower, covered in scenario["towers"].items()}
        validate_region(scenario["areas"], towers)
        check_k(scenario["k"], towers)
        scenarios.append({**scenario, "towers": towers})
    return scenarios
