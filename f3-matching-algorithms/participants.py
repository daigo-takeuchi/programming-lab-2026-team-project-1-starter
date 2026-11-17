# F3：参加者モデル（Python 標準ライブラリのみ）
#
# 1 人の参加者は次のキーを持つ辞書（data/sample_participants.json と同じ形）。すべて架空のデータ。
#
#   id                    : 参加者 ID（"A1"、"B3" など。全体で重複しない）
#   group                 : "A" または "B"（アルゴリズム上の区分。性別や性的指向を意味しない）
#   age                   : 年齢（整数）
#   interests             : 趣味・関心のタグのリスト（例：["hiking", "music"]）
#   lifestyle             : 生活スタイルの指標（各 0〜1）。例：{"morning": 0.8, "social": 0.3, "tidy": 0.6}
#   values                : 価値観の指標（各 0〜1）。例：{"family": 0.9, "career": 0.4, "adventure": 0.2}
#   preferences           : 希望条件
#       weights           :   重み {"interest", "lifestyle", "values", "age"}（合計 1）
#       age_range         :   希望する相手の年齢 [下限, 上限]
#       min_score         :   この希望スコア以上の相手だけを受け入れる（閾値、0〜1）
#   acceptable_candidates : 会ってみてもよい相手の ID のリスト（相手のグループのみ）。
#                           最終的に受け入れるのは「このリストにいて、かつ希望スコア ≥ min_score」の相手。
#
# ■ 実在の人物の情報は使わない。個人の結婚適性を評価するためのものではない（README 22章）。

import json
import os

GROUPS = ("A", "B")
WEIGHT_KEYS = ("interest", "lifestyle", "values", "age")
DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_participants.json")


def other_group(group):
    return "B" if group == "A" else "A"


def load_participants(path=DATA_FILE):
    """参加者データを読み込み、検証してから {"A": [...], "B": [...]} を返す（各グループは ID 順）"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    people = data["participants"]
    validate_participants(people)
    groups = {g: sorted([p for p in people if p["group"] == g], key=lambda p: p["id"]) for g in GROUPS}
    return groups


def validate_participants(people):
    """参加者のリストを検証する（問題があれば ValueError）"""
    ids = [p["id"] for p in people]
    seen = set()
    for i in ids:
        if i in seen:
            raise ValueError(f"参加者 ID {i} が重複しています")
        seen.add(i)
    by_id = {p["id"]: p for p in people}
    for p in people:
        if p.get("group") not in GROUPS:
            raise ValueError(f"{p['id']} のグループ {p.get('group')!r} が不正です（'A' か 'B'）")
        if isinstance(p.get("age"), bool) or not isinstance(p.get("age"), int) or p["age"] < 0:
            raise ValueError(f"{p['id']} の年齢は 0 以上の整数にしてください")
        for key in ("lifestyle", "values"):
            for k, v in p.get(key, {}).items():
                if not 0 <= v <= 1:
                    raise ValueError(f"{p['id']} の {key}.{k} = {v} は 0〜1 の範囲外です")
        pref = p.get("preferences", {})
        weights = pref.get("weights", {})
        if set(weights) != set(WEIGHT_KEYS):
            raise ValueError(f"{p['id']} の重みは {WEIGHT_KEYS} の 4 つを指定してください")
        if any(w < 0 for w in weights.values()) or abs(sum(weights.values()) - 1) > 1e-9:
            raise ValueError(f"{p['id']} の重みは 0 以上で、合計 1 にしてください（合計 {sum(weights.values())}）")
        lo, hi = pref.get("age_range", [0, 200])
        if lo > hi:
            raise ValueError(f"{p['id']} の希望年齢の範囲が逆です")
        if not 0 <= pref.get("min_score", 0) <= 1:
            raise ValueError(f"{p['id']} の min_score は 0〜1 にしてください")
        validate_candidate_list(p, p.get("acceptable_candidates", []), by_id)


def validate_candidate_list(p, candidates, by_id):
    """希望候補者のリストを検証する：存在する・相手のグループ・重複なし"""
    seen = set()
    for c in candidates:
        if c not in by_id:
            raise ValueError(f"{p['id']} の候補 {c} は存在しない参加者です")
        if by_id[c]["group"] == p["group"]:
            raise ValueError(f"{p['id']} の候補 {c} は同じグループです（相手のグループだけを候補にできます）")
        if c in seen:
            raise ValueError(f"{p['id']} の候補 {c} が重複しています")
        seen.add(c)


def by_id(groups):
    """{id: 参加者} の辞書（ハッシュ表）。O(N) で作り、検索は平均 O(1)"""
    return {p["id"]: p for g in GROUPS for p in groups[g]}


def total_participants(groups):
    return len(groups["A"]) + len(groups["B"])


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：架空の参加者を増やす（各グループ 20 人など）。乱数で作る関数を書き、乱数シードを記録する。
# TODO 2：lifestyle・values の項目を変える・増やす（項目の意味を README に書く）。
# TODO 3：Group A と Group B の人数が違う場合を試す。
