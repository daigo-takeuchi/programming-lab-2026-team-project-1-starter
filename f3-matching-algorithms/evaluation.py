# F3：評価指標（マッチング成立時点 ＋ 長期継続）
#
#   Matching Rate              = 2 × 成立ペア数 / 全参加者数
#   Initial Satisfaction       = 希望順位にもとづく満足度（下の定義）
#   Blocking Pair Count        = 互いに今の相手より好み、相互に受け入れ可能な 2 人の組の数
#   Continuation Rate(T)       = T 年後も継続しているペア数 / 最初に成立したペア数（成立 0 組なら未定義 = None）
#   Long-term Matching Rate(T) = 2 × T 年後も継続しているペア数 / 全参加者数
#
# ■ 初期満足度の定義（この教材での約束）
#   受け入れ可能な相手が L 人いる参加者が、その k 番目（k = 1 が第 1 希望）の相手とマッチングしたとき
#       satisfaction = 1 − (k − 1) / L        （第 1 希望 = 1.0、最下位の受け入れ可能な相手 = 1/L）
#   未マッチングの参加者は 0。受け入れ可能な相手が 1 人もいない参加者も 0（未マッチング）。
#   平均は「全参加者」で取る（未マッチングを含む）。「マッチングした人だけ」の平均も別に出す。

import statistics
import time

import participants as pt
import preferences as pr
import relationship_stability as rs


# ------------------------------------------------------------
# マッチング成立時点
# ------------------------------------------------------------
def matching_rate(matching, total_participants):
    """成立率 = 2 × 成立ペア数 / 全参加者数（参加者 0 人なら None）"""
    if total_participants <= 0:
        return None
    if 2 * len(matching) > total_participants:
        raise ValueError("成立ペア数が全参加者数と整合しません")
    return 2 * len(matching) / total_participants


def partner_map(matching):
    """{参加者 ID: 相手の ID}（両方向）"""
    m = dict(matching)
    m.update({b: a for a, b in matching.items()})
    return m


def satisfaction_by_participant(matching, rankings):
    """{参加者 ID: 初期満足度（0〜1）}。rankings に含まれる全員について計算する"""
    partner = partner_map(matching)
    out = {}
    for pid, lst in rankings.items():
        q = partner.get(pid)
        if q is None or not lst:
            out[pid] = 0.0
        else:
            k = lst.index(q) + 1
            out[pid] = 1 - (k - 1) / len(lst)
    return out


def rank_of_partner(matching, rankings):
    """{参加者 ID: 相手が何番目の希望か（1 始まり）。未マッチングは None}"""
    partner = partner_map(matching)
    return {pid: (rankings[pid].index(partner[pid]) + 1 if pid in partner else None) for pid in rankings}


def satisfaction_summary(matching, rankings, a_ids, b_ids):
    """満足度・公平性の指標の辞書"""
    s = satisfaction_by_participant(matching, rankings)
    ranks = rank_of_partner(matching, rankings)
    partner = partner_map(matching)

    def mean(ids, matched_only=False):
        vals = [s[i] for i in ids if (not matched_only or i in partner)]
        return statistics.mean(vals) if vals else None

    all_ids = list(a_ids) + list(b_ids)
    return {
        "mean_all": mean(all_ids), "mean_matched": mean(all_ids, True),
        "mean_A": mean(a_ids), "mean_B": mean(b_ids),
        "min": min(s[i] for i in all_ids) if all_ids else None,
        "min_matched": min((s[i] for i in all_ids if i in partner), default=None),
        "unmatched_A": sum(1 for i in a_ids if i not in partner) / len(a_ids) if a_ids else None,
        "unmatched_B": sum(1 for i in b_ids if i not in partner) / len(b_ids) if b_ids else None,
        "rank_distribution": rank_distribution(ranks),
        "by_participant": s,
    }


def rank_distribution(ranks):
    """{1: 第 1 希望とマッチングした人数, 2: ..., "unmatched": 人数}"""
    dist = {}
    for r in ranks.values():
        key = "unmatched" if r is None else r
        dist[key] = dist.get(key, 0) + 1
    return dist


def blocking_pairs(matching, rankings, a_ids, b_ids):
    """Blocking pair のリスト。O(N^2)（順位の比較は辞書で O(1)）

    (a, b) が blocking pair：相互承諾可能で、a・b は今ペアではなく、
      a は b を今の相手より好む（未マッチングなら受け入れ可能な相手は誰でも好む）、かつ b も a を同様に好む。
    """
    rank = pr.rank_index(rankings)
    partner = partner_map(matching)

    def prefers(x, y):
        cur = partner.get(x)
        return cur is None or rank[x][y] < rank[x][cur]

    out = []
    for a in sorted(a_ids):
        for b in sorted(b_ids):
            if partner.get(a) == b or not pr.mutually_acceptable(rankings, a, b):
                continue
            if prefers(a, b) and prefers(b, a):
                out.append((a, b))
    return out


def is_stable(matching, rankings, a_ids, b_ids):
    """Blocking pair が 1 つもないか（数学的な安定性。関係が長続きするかとは別）"""
    return not blocking_pairs(matching, rankings, a_ids, b_ids)


def mean_pair_compatibility(matching, scores):
    """成立したペアの初期適合度の平均（成立 0 組なら None）"""
    vals = [pr.pair_compatibility(a, b, scores) for a, b in matching.items()]
    return statistics.mean(vals) if vals else None


def time_algorithm(func, repeats=200):
    """func() の実行時間の中央値（秒）"""
    times = []
    for _ in range(repeats):
        t0 = time.perf_counter()
        func()
        times.append(time.perf_counter() - t0)
    return statistics.median(times)


# ------------------------------------------------------------
# 長期継続
# ------------------------------------------------------------
def continuation_rate(records, t):
    """t 年後の継続率 = t 年後も継続しているペア数 / 成立したペア数。成立 0 組なら None（0% とは断定しない）"""
    if not records:
        return None
    if any(t > r["observed_years"] for r in records):
        raise ValueError(f"{t} 年後は観測期間の外です（分からない）")
    return sum(1 for r in records if rs.status_at(r, t)) / len(records)


def continuing_pairs(records, t):
    return sum(1 for r in records if rs.status_at(r, t))


def long_term_matching_rate(records, t, total_participants):
    """長期成立率 = 2 × t 年後も継続しているペア数 / 全参加者数"""
    if total_participants <= 0:
        return None
    return 2 * continuing_pairs(records, t) / total_participants


def survival_curve(records, years=None):
    """[0 年後, 1 年後, ..., years 年後] の継続率（成立 0 組なら None）"""
    if not records:
        return None
    years = records[0]["observed_years"] if years is None else years
    return [continuation_rate(records, t) for t in range(0, years + 1)]


def duration_summary(records):
    """継続期間のまとめ。解消したペアと、観測終了まで継続した（打ち切りの）ペアを分けて数える

    mean_observed_years : 観測期間内に継続した年数の平均（打ち切りのペアは観測期間の長さ。解消までの年数を推測しない）
    mean_years_dissolved: 解消したペアだけの、解消までに継続した年数の平均
    """
    dissolved = [r for r in records if r["dissolved"]]
    censored = [r for r in records if r["censored"]]
    return {
        "pairs": len(records), "dissolved": len(dissolved), "censored": len(censored),
        "mean_observed_years": statistics.mean(r["years_continued"] for r in records) if records else None,
        "mean_years_dissolved": statistics.mean(r["years_continued"] for r in dissolved) if dissolved else None,
    }


def mean_over_replicates(runs, func):
    """反復ごとの値（None を除く）の平均と標準偏差。runs = monte_carlo の結果"""
    vals = [v for v in (func(rec) for rec in runs) if v is not None]
    if not vals:
        return None, None
    return statistics.mean(vals), (statistics.stdev(vals) if len(vals) > 1 else 0.0)


# ------------------------------------------------------------
# アルゴリズムの統合評価（Stage 3）
# ------------------------------------------------------------
def evaluate_algorithm(name, matching, groups, rankings, scores, params, replicates=200, years=None, seed=None,
                       **sim_kw):
    """1 つのマッチング結果を、成立時点と長期継続の両方で評価する（辞書）"""
    a_ids = [p["id"] for p in groups["A"]]
    b_ids = [p["id"] for p in groups["B"]]
    n = pt.total_participants(groups)
    sat = satisfaction_summary(matching, rankings, a_ids, b_ids)
    pairs = rs.make_pairs(matching, name, lambda a, b: pr.pair_compatibility(a, b, scores), sat["by_participant"])
    runs = rs.monte_carlo(pairs, params, replicates, years, seed, **sim_kw)
    out = {
        "algorithm": name, "pairs": len(matching), "participants": n,
        "matching_rate": matching_rate(matching, n),
        "satisfaction": sat["mean_all"], "satisfaction_A": sat["mean_A"], "satisfaction_B": sat["mean_B"],
        "min_satisfaction": sat["min"], "blocking_pairs": len(blocking_pairs(matching, rankings, a_ids, b_ids)),
        "mean_compatibility": mean_pair_compatibility(matching, scores),
        "replicates": replicates, "matching": dict(matching), "pair_list": pairs,
    }
    for t in rs.CHECKPOINTS:
        if t <= (params["simulation_years"] if years is None else years):
            out[f"continuation_{t}y"], out[f"continuation_{t}y_sd"] = mean_over_replicates(
                runs, lambda rec: continuation_rate(rec, t))
            out[f"long_term_{t}y"], out[f"long_term_{t}y_sd"] = mean_over_replicates(
                runs, lambda rec: long_term_matching_rate(rec, t, n))
    out["survival_curve"] = [mean_over_replicates(runs, lambda rec: continuation_rate(rec, t))[0]
                             for t in range(0, (params["simulation_years"] if years is None else years) + 1)]
    return out


SUMMARY_KEYS = ["pairs", "matching_rate", "satisfaction", "satisfaction_A", "satisfaction_B", "min_satisfaction",
                "blocking_pairs", "mean_compatibility", "continuation_5y", "continuation_10y", "continuation_20y",
                "long_term_5y", "long_term_10y", "long_term_20y"]


def compare_algorithms(groups, rankings, scores, params, matching_seeds=range(20), replicates=200,
                       algorithms=("random", "greedy", "gale_shapley"), **sim_kw):
    """3 つのアルゴリズムを同じ条件で比べる（Stage 3）

    ・Random はマッチング自体が乱数で変わるので、matching_seeds の各シードで実行して平均する
    ・Greedy（ID 順）と Gale-Shapley は決定的なので 1 回だけ実行する
    ・関係継続はどのアルゴリズムも同じパラメータ・同じ観測期間・同じ反復回数・共通乱数で計算する
    返り値：{アルゴリズム名: 指標の辞書}。Random の指標は各シードの平均（*_seed_sd にシード間の標準偏差）
    """
    import matching_algorithms as ma
    a_ids = [p["id"] for p in groups["A"]]
    b_ids = [p["id"] for p in groups["B"]]
    out = {}
    for name in algorithms:
        seeds = list(matching_seeds) if name == "random" else [None]
        evals = [evaluate_algorithm(name, ma.run(name, rankings, a_ids, b_ids, seed=s or 0), groups, rankings,
                                    scores, params, replicates, **sim_kw) for s in seeds]
        summary = {"algorithm": name, "label": ma.LABELS[name], "matching_runs": len(evals), "replicates": replicates}
        for k in SUMMARY_KEYS:
            vals = [e[k] for e in evals if e.get(k) is not None]
            summary[k] = statistics.mean(vals) if vals else None
            summary[k + "_seed_sd"] = statistics.stdev(vals) if len(vals) > 1 else 0.0
        curves = [e["survival_curve"] for e in evals if e["survival_curve"] and None not in e["survival_curve"]]
        summary["survival_curve"] = [statistics.mean(c[t] for c in curves) for t in range(len(curves[0]))] if curves else None
        summary["runs"] = evals
        out[name] = summary
    return out


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：満足度の定義を変える（例：順位ではなく希望スコアそのもの）。定義によって結論が変わるか調べる。
# TODO 2：公平性の指標を増やす（例：Group A と B の平均満足度の差、最も満足度の低い人の値）。
# TODO 3：長期継続率だけでなく、初期満足度・未マッチング率と合わせて公平性を考える（Advanced E）。
