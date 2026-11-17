# F3：3 種類のマッチングアルゴリズム（Python 標準ライブラリのみ）
#
# すべてのアルゴリズムは、同じ「希望順位（rankings）」を入力にする。
#   rankings = {参加者 ID: [受け入れ可能な相手の ID（希望順）]}（preferences.build_rankings の結果）
#   a_ids, b_ids = Group A・Group B の参加者 ID のリスト
# 結果のマッチングは {Group A の ID: Group B の ID} の辞書（未マッチングの人は含まれない）。
# どのアルゴリズムも、1 人は高々 1 人とマッチングし、相互承諾可能な組だけを成立させる。
#
#   Random       ：相互承諾可能な組をランダムな順に調べ、2 人とも空いていれば成立させる（乱数シードで再現）
#   Greedy       ：Group A を順番に処理し、相互承諾可能で空いている相手のうち希望順位が最も高い人と成立。変更しない
#   Gale-Shapley ：受け入れ保留方式（Deferred Acceptance）。提案側の最適な安定マッチングになる
#
# ■ 教科書のコード
#   ・Greedy の「希望順に見て、最初に条件を満たす相手」：第3章 seq_search（線形探索）
#   ・Gale-Shapley の「まだ相手のいない提案者」の管理：第4章 FixedQueue（キュー、先入れ先出し）
#   ・受け手の順位の比較：辞書（Python のハッシュ表。第3章 ハッシュ法の考え方）で平均 O(1)
#
# ■ Gale-Shapley の「安定」は、Blocking pair（互いに今の相手より好む 2 人）がないという数学的な性質。
#   結婚後の関係が長続きすること（relationship_stability.py）とは別の概念（README 7〜9章）。

import random

from textbook.fixed_queue import FixedQueue
from textbook.ssearch_while import seq_search

import preferences as pr

ALGORITHMS = ("random", "greedy", "gale_shapley")
LABELS = {"random": "Random", "greedy": "Greedy", "gale_shapley": "Gale-Shapley"}


def acceptable_pairs(rankings, a_ids, b_ids):
    """相互承諾可能な (a, b) の組のリスト（a・b の ID 順）。O(N^2)"""
    return [(a, b) for a in sorted(a_ids) for b in sorted(b_ids) if pr.mutually_acceptable(rankings, a, b)]


# ------------------------------------------------------------
# Algorithm A：Random Matching
# ------------------------------------------------------------
def random_matching(rankings, a_ids, b_ids, seed=0):
    """相互承諾可能な組をランダムに並べ、先頭から「2 人とも空いていれば成立」させる

    注意：これは「すべてのマッチングの中から一様に 1 つ選ぶ」方法ではなく、
    ランダムな順で組を選んでいく方法（結果は極大マッチング＝これ以上組を足せない状態になる）。
    """
    pairs = acceptable_pairs(rankings, a_ids, b_ids)
    random.Random(seed).shuffle(pairs)
    matching, used_b = {}, set()
    for a, b in pairs:
        if a not in matching and b not in used_b:
            matching[a] = b
            used_b.add(b)
    return matching


# ------------------------------------------------------------
# Algorithm B：Greedy Matching
# ------------------------------------------------------------
def greedy_order(a_ids, seed=None):
    """Greedy の処理順序。seed=None なら ID 順、整数ならその乱数シードでシャッフルした順"""
    order = sorted(a_ids)
    if seed is not None:
        random.Random(seed).shuffle(order)
    return order


def greedy_matching(rankings, a_ids, b_ids, order=None):
    """Group A を order の順に処理し、希望順に見て最初に「空いていて相互承諾可能」な相手と成立させる"""
    order = greedy_order(a_ids) if order is None else list(order)
    if sorted(order) != sorted(a_ids):
        raise ValueError("処理順序には Group A の全員を 1 回ずつ含めてください")
    matching, used_b = {}, set()
    for a in order:
        candidates = rankings.get(a, [])
        ok = [b not in used_b and pr.mutually_acceptable(rankings, a, b) for b in candidates]
        k = seq_search(ok, True)                     # 教科書：線形探索（最初に True になる位置）
        if k != -1:
            matching[a] = candidates[k]
            used_b.add(candidates[k])
    return matching


# ------------------------------------------------------------
# Algorithm C：Gale-Shapley Matching（受け入れ保留方式）
# ------------------------------------------------------------
def gale_shapley(rankings, a_ids, b_ids, record=False):
    """Group A が提案する Gale-Shapley 法

    1. 相手のいない提案者をキューに入れる
    2. キューから 1 人取り出し、まだ提案していない相手のうち希望順位が最も高い人に提案する
       （受け入れ可能な相手にだけ提案する。同じ相手には高々 1 回）
    3. 受け手は、提案者を受け入れ可能でなければ拒否。仮の相手がいなければ仮に受け入れる。
       仮の相手がいれば、順位辞書で比べて好む方を残し、もう一方を拒否する
    4. 拒否された人は、まだ提案できる相手がいればキューに戻る
    提案の回数は高々（各人の希望リストの長さの合計）≤ N^2。

    record=True のとき (matching, steps) を返す。steps は各提案の記録（Notebook 03 で表示）。
    """
    rank_b = pr.rank_index({b: rankings.get(b, []) for b in b_ids})    # 受け手の順位辞書
    next_choice = {a: 0 for a in a_ids}                                 # 次に提案する希望順位の位置
    engaged_to = {}                                                     # 受け手 → 仮の相手
    queue = FixedQueue(max(1, len(a_ids)))                              # 教科書：固定長キュー
    for a in sorted(a_ids):
        if rankings.get(a):
            queue.enque(a)
    steps = []

    while not queue.is_empty():
        a = queue.deque()
        prefs = rankings.get(a, [])
        b = prefs[next_choice[a]]
        next_choice[a] += 1
        current = engaged_to.get(b)
        if a not in rank_b[b]:
            action, rejected = "reject", a                              # 受け手が受け入れられない相手
        elif current is None:
            engaged_to[b] = a
            action, rejected = "accept", None
        elif rank_b[b][a] < rank_b[b][current]:
            engaged_to[b] = a
            action, rejected = "replace", current                       # 新しい提案者の方を好む
        else:
            action, rejected = "reject", a
        if rejected is not None and next_choice[rejected] < len(rankings.get(rejected, [])):
            queue.enque(rejected)                                       # まだ提案できる相手がいる
        if record:
            steps.append({"step": len(steps) + 1, "proposer": a, "receiver": b, "action": action,
                          "rejected": rejected, "tentative": dict(sorted((x, y) for y, x in engaged_to.items()))})

    matching = {a: b for b, a in engaged_to.items()}
    return (matching, steps) if record else matching


def swap_sides(rankings, a_ids, b_ids):
    """Group B を提案側にするための入れ替え（gale_shapley(rankings, b_ids, a_ids) の結果を A→B の形に戻す）"""
    m = gale_shapley(rankings, b_ids, a_ids)
    return {a: b for b, a in m.items()}


def run(name, rankings, a_ids, b_ids, seed=0, order=None):
    """アルゴリズム名で実行する（"random" / "greedy" / "gale_shapley"）"""
    if name == "random":
        return random_matching(rankings, a_ids, b_ids, seed)
    if name == "greedy":
        return greedy_matching(rankings, a_ids, b_ids, order)
    if name == "gale_shapley":
        return gale_shapley(rankings, a_ids, b_ids)
    raise ValueError(f"不明なアルゴリズム：{name}")


def validate_matching(matching, rankings):
    """1 人 1 ペア・相互承諾可能であることを確認する（違反があれば ValueError）"""
    if len(set(matching.values())) != len(matching):
        raise ValueError("Group B の 1 人が複数の相手とマッチングしています")
    for a, b in matching.items():
        if not pr.mutually_acceptable(rankings, a, b):
            raise ValueError(f"{a}–{b} は相互承諾可能ではありません")


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：Greedy の処理順序（greedy_order の seed）を変えて、成立率・満足度がどう変わるか調べる。
# TODO 2：Group B が提案する Gale-Shapley（swap_sides）と比べ、どちらのグループの満足度が高いか調べる（公平性）。
# TODO 3：「スコアの合計が最大になる組合せ」を全探索で求め（小さな N で）、他のアルゴリズムと比べる。
# TODO 4：提案の回数を数え、N を増やしたときの増え方（O(N^2)）を確かめる。
