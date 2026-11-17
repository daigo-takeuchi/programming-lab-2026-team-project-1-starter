# F3：希望スコア（Compatibility Score）と希望順位
#
#   Compatibility Score(p → q)
#     = w1 × Interest Similarity + w2 × Lifestyle Similarity + w3 × Value Similarity + w4 × Age Compatibility
#
#   ・各項目は 0〜1、重み w1〜w4 は p 自身の希望条件（合計 1）。p から見た q の評価なので、向きによって値が違う。
#   ・希望順位：受け入れ可能な相手（acceptable_candidates にいて、かつスコア ≥ min_score）を、
#     スコアの高い順に並べる。同点なら ID の昇順（決定的な規則）。教科書 第6章 insertion_sort（安定）を使う。
#   ・相互承諾可能：p が q を受け入れ、q も p を受け入れる。
#
# ■ 希望スコアは教育用の人工的な指標であり、実際の結婚適性を表すものではない。

from textbook.insertion_sort import insertion_sort

import participants as pt

AGE_DECAY_YEARS = 10   # 希望年齢の範囲から 10 歳離れると、年齢の適合度は 0 になる（教育用の仮定）


# ------------------------------------------------------------
# 各項目（0〜1）
# ------------------------------------------------------------
def interest_similarity(p, q):
    """趣味・関心のタグの Jaccard 係数 = 共通のタグ数 / どちらかが持つタグ数（両方空なら 0）"""
    a, b = set(p.get("interests", [])), set(q.get("interests", []))
    union = a | b
    return len(a & b) / len(union) if union else 0.0


def _profile_similarity(x, y):
    """共通の項目について 1 − |差| の平均（項目が 1 つもなければ 0）"""
    keys = sorted(set(x) & set(y))
    if not keys:
        return 0.0
    return sum(1 - abs(x[k] - y[k]) for k in keys) / len(keys)


def lifestyle_similarity(p, q):
    return _profile_similarity(p.get("lifestyle", {}), q.get("lifestyle", {}))


def value_similarity(p, q):
    return _profile_similarity(p.get("values", {}), q.get("values", {}))


def age_compatibility(p, q):
    """q の年齢が p の希望範囲内なら 1。範囲から d 歳離れると 1 − d/10（0 未満は 0）"""
    lo, hi = p["preferences"].get("age_range", [0, 200])
    d = 0 if lo <= q["age"] <= hi else min(abs(q["age"] - lo), abs(q["age"] - hi))
    return max(0.0, 1 - d / AGE_DECAY_YEARS)


def components(p, q):
    """p から見た q の 4 項目（辞書）"""
    return {"interest": interest_similarity(p, q), "lifestyle": lifestyle_similarity(p, q),
            "values": value_similarity(p, q), "age": age_compatibility(p, q)}


def compatibility_score(p, q, weights=None):
    """p から見た q の希望スコア（0〜1）。weights を省略すると p 自身の重みを使う"""
    w = weights or p["preferences"]["weights"]
    if abs(sum(w.values()) - 1) > 1e-9 or any(v < 0 for v in w.values()):
        raise ValueError("重みは 0 以上で合計 1 にしてください")
    c = components(p, q)
    return sum(w[k] * c[k] for k in pt.WEIGHT_KEYS)


# ------------------------------------------------------------
# スコア表・希望順位・相互承諾
# ------------------------------------------------------------
def score_table(groups, weights_override=None):
    """{(p_id, q_id): p から見た q のスコア} をすべての異なるグループの組について作る（O(N^2)）

    weights_override = {"A": 重み, "B": 重み} などで、グループ全員の重みを一時的に置き換えられる（実験用）。
    """
    table = {}
    for g in pt.GROUPS:
        for p in groups[g]:
            w = (weights_override or {}).get(g)
            for q in groups[pt.other_group(g)]:
                table[(p["id"], q["id"])] = compatibility_score(p, q, w)
    return table


def is_acceptable(p, q, scores):
    """p が q を受け入れるか：q が acceptable_candidates にいて、かつスコア ≥ min_score"""
    allowed = p.get("acceptable_candidates")
    if allowed is not None and q["id"] not in allowed:
        return False
    return scores[(p["id"], q["id"])] >= p["preferences"].get("min_score", 0)


def build_rankings(groups, scores):
    """{p_id: [受け入れ可能な相手の ID（希望順）]}。同点は ID の昇順"""
    rankings = {}
    for g in pt.GROUPS:
        for p in groups[g]:
            keyed = [(-scores[(p["id"], q["id"])], q["id"]) for q in groups[pt.other_group(g)]
                     if is_acceptable(p, q, scores)]
            insertion_sort(keyed)                      # 教科書：単純挿入ソート（(−スコア, ID) の昇順）
            rankings[p["id"]] = [qid for _neg, qid in keyed]
    return rankings


def rank_index(rankings):
    """{p_id: {q_id: 順位（0 が第 1 希望）}}。順位の比較を辞書（ハッシュ表）で平均 O(1) にする"""
    return {pid: {qid: k for k, qid in enumerate(lst)} for pid, lst in rankings.items()}


def mutually_acceptable(rankings, a_id, b_id):
    """a が b を、b が a を、どちらも受け入れているか"""
    return b_id in rankings.get(a_id, []) and a_id in rankings.get(b_id, [])


def pair_compatibility(a_id, b_id, scores):
    """ペアの初期適合度 = 2 方向の希望スコアの平均（0〜1）。関係継続モデルで使う"""
    return (scores[(a_id, b_id)] + scores[(b_id, a_id)]) / 2


def validate_rankings(rankings, groups):
    """希望順位を検証する：候補が存在する・相手のグループ・重複なし"""
    people = pt.by_id(groups)
    for pid, lst in rankings.items():
        pt.validate_candidate_list(people[pid], lst, people)


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：重みを変更する（例：価値観を重視する {"interest": 0.1, "lifestyle": 0.2, "values": 0.6, "age": 0.1}）。
# TODO 2：min_score（希望条件の厳しさ）を変えて、受け入れ可能な相手の数と成立率を調べる（RQ2）。
# TODO 3：年齢の適合度の式（10 歳で 0 になる）を変えてみる。
# TODO 4：希望順位を「上位 k 人だけ」にする（候補者数の制限、RQ2）。
