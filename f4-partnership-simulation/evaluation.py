# F4：評価指標
#
# ・満足度は「平均」「最低」「差」を必ず並べて見る。平均だけで公平性を評価しない。
# ・公平性指標は教育用に定義したもの。「何を公平とみなすか（基準）」はモデル上の選択で、
#   基準を変えると同じ分担の評価が変わる（RQ1）。
# ・継続率・解消率・継続期間は、観測期間の終わりによる「打ち切り」と「解消」を区別する。

import statistics

import household_model as hm
import relationship_dynamics as rd
import decision_strategies as ds
from textbook.ssearch_while import seq_search

FAIRNESS_REFERENCES = ("workload", "equal", "income", "preference")


# ------------------------------------------------------------
# 14.1〜14.3 満足度
# ------------------------------------------------------------
def mean_satisfaction(sa, sb):
    return (sa + sb) / 2


def minimum_satisfaction(sa, sb):
    return min(sa, sb)


def satisfaction_difference(sa, sb):
    return abs(sa - sb)


# ------------------------------------------------------------
# 14.4 公平性指標（教育用）
# ------------------------------------------------------------
def reference_allocation(partners, household, reference="workload"):
    """公平とみなす「基準の分担」(x*, y*)

      workload  ：有償労働 + 家事 の合計時間が 2 人で等しい家事分担、生活費は所得比例
      equal     ：家事も生活費も 50:50
      income    ：家事は所得の少ない人が多く、生活費は所得比例（比較用。正当化するものではない）
      preference：2 人の希望の中間
    """
    if reference == "workload":
        return (hm.equal_workload_housework_share(partners, household["total_housework_hours"]),
                hm.income_share(partners))
    if reference == "equal":
        return 0.5, 0.5
    if reference == "income":
        return hm.income_housework_share(partners), hm.income_share(partners)
    if reference == "preference":
        return hm.preference_housework_share(partners), hm.preference_financial_share(partners)
    raise ValueError(f"公平性の基準 {reference!r} は {FAIRNESS_REFERENCES} のどれかにしてください")


def fairness_components(x, y, sa, sb, partners, household, reference="workload"):
    """公平性の 3 つの要素（それぞれ 0〜1、0 が最も公平）"""
    rx, ry = reference_allocation(partners, household, reference)
    return {"housework_gap": abs(x - rx), "financial_gap": abs(y - ry), "satisfaction_gap": abs(sa - sb)}


def fairness_index(x, y, sa, sb, partners, household, reference="workload", weights=(1, 1, 1)):
    """公平性指標 = 1 − 加重平均(家事のずれ, 生活費のずれ, 満足度の差)。1 が最も公平、0 が最も不公平"""
    c = fairness_components(x, y, sa, sb, partners, household, reference)
    w = weights
    total = w[0] + w[1] + w[2]
    if total <= 0:
        raise ValueError("weights の合計は正にしてください")
    return 1 - (w[0] * c["housework_gap"] + w[1] * c["financial_gap"] + w[2] * c["satisfaction_gap"]) / total


def record_fairness(record, partners, household, reference="workload"):
    return fairness_index(record["housework_share"], record["financial_share"], record["satisfaction_A"],
                          record["satisfaction_B"], partners, household, reference)


# ------------------------------------------------------------
# 14.5〜14.7 継続率・解消率・継続期間
# ------------------------------------------------------------
def continuation_rate(outcomes, t):
    """t 年後に継続している割合。結果がない・観測期間が t 年未満なら None"""
    flags = [rd.continued_at(o, t) for o in outcomes]
    flags = [f for f in flags if f is not None]
    return sum(flags) / len(flags) if flags else None


def dissolution_rate(outcomes):
    """観測期間内に関係が解消した割合"""
    return sum(o["dissolved"] for o in outcomes) / len(outcomes) if outcomes else None


def duration_summary(outcomes):
    """継続期間：解消した関係と、観測期間の終わりで打ち切った関係を分けて数える"""
    dissolved = [o["duration"] for o in outcomes if o["dissolved"]]
    return {"n": len(outcomes), "dissolved": len(dissolved), "censored": len(outcomes) - len(dissolved),
            "mean_duration_dissolved": statistics.mean(dissolved) if dissolved else None,
            "mean_observed_duration": statistics.mean(o["duration"] for o in outcomes) if outcomes else None}


def survival_curve(outcomes, years):
    """0〜years 年の継続率のリスト"""
    return [continuation_rate(outcomes, t) for t in range(years + 1)]


def dissolution_year_of(records):
    """記録の中で関係が解消した年（線形探索）。解消していなければ None"""
    flags = [r["continuing"] for r in records]
    idx = seq_search(flags, False)
    return None if idx == -1 else records[idx]["year"]


# ------------------------------------------------------------
# 満足度の軌跡のまとめ
# ------------------------------------------------------------
def trajectory_summary(records, partners, household, reference="workload", first_years=1):
    """継続した場合の軌跡（0 年目を除く）の要約"""
    rs = records[1:]
    if not rs:
        return None
    means = [mean_satisfaction(r["satisfaction_A"], r["satisfaction_B"]) for r in rs]
    mins = [minimum_satisfaction(r["satisfaction_A"], r["satisfaction_B"]) for r in rs]
    diffs = [satisfaction_difference(r["satisfaction_A"], r["satisfaction_B"]) for r in rs]
    fair = [record_fairness(r, partners, household, reference) for r in rs]
    return {"mean_satisfaction": statistics.mean(means), "min_satisfaction": statistics.mean(mins),
            "satisfaction_diff": statistics.mean(diffs), "fairness": statistics.mean(fair),
            "first_year_mean_utility": statistics.mean(
                (r["utility_A"] + r["utility_B"]) / 2 for r in rs[:first_years]),
            "final_relationship_satisfaction": rs[-1]["relationship_satisfaction"],
            "mean_dissolution_probability": statistics.mean(r["dissolution_probability"] for r in rs),
            "final_housework_share": rs[-1]["housework_share"], "final_financial_share": rs[-1]["financial_share"],
            "infeasible_years": sum(1 for r in rs if r["feasible"] is False)}


# ------------------------------------------------------------
# 14.8 ストレスへの頑健性
# ------------------------------------------------------------
def stress_response(records, event_year, window=2):
    """イベント前（window 年）とイベント後（window 年）の関係満足度の平均と、その変化"""
    before = [r["relationship_satisfaction"] for r in records if event_year - window <= r["year"] < event_year]
    after = [r["relationship_satisfaction"] for r in records if event_year <= r["year"] < event_year + window]
    if not before or not after:
        return None
    b, a = statistics.mean(before), statistics.mean(after)
    return {"before": b, "after": a, "change": a - b}


def robustness_to_stress(scenario, strategy, params, events, replicates=200, seeds=(0,), years=None, t=10):
    """ストレスなし／ありの継続率と満足度の差（ありの値 − なしの値）"""
    base = compare_strategies(scenario, params, (), [strategy], replicates, seeds, years)[strategy]
    hit = compare_strategies(scenario, params, events, [strategy], replicates, seeds, years)[strategy]
    key = f"continuation_{t}"
    return {"without": base, "with": hit,
            "continuation_change": None if base[key] is None or hit[key] is None else hit[key] - base[key],
            "satisfaction_change": hit["mean_satisfaction"] - base["mean_satisfaction"]}


# ------------------------------------------------------------
# 戦略の比較（複数シード × 反復）
# ------------------------------------------------------------
SUMMARY_KEYS = ("mean_satisfaction", "min_satisfaction", "satisfaction_diff", "fairness", "first_year_mean_utility",
                "continuation_5", "continuation_10", "continuation_20", "dissolution_rate")


def _mean_sd(values):
    values = [v for v in values if v is not None]
    if not values:
        return None, None
    return statistics.mean(values), (statistics.stdev(values) if len(values) > 1 else 0.0)


def evaluate_strategy(scenario, strategy, params, events=(), replicates=200, seeds=(0,), years=None,
                      reference="workload", candidates=None):
    """1 つの戦略の評価。満足度・公平性は「継続した場合の軌跡」から、継続率は シード × 反復 から計算する

    継続率は シードごとの継続率の平均（_sd はシード間の標準偏差）。
    """
    years = int(params["simulation_years"] if years is None else years)
    candidates = ds.candidate_grid(params["share_step"]) if candidates is None else candidates
    per_seed = []
    recs = None
    for s in seeds:
        mc = rd.monte_carlo(scenario, strategy, params, events, replicates, s, years, candidates)
        recs = mc["trajectory"]
        per_seed.append(mc["outcomes"])
    out = dict(trajectory_summary(recs, scenario["partners"], scenario["household"], reference))
    for t in rd.CHECKPOINTS:
        m, sd = _mean_sd([continuation_rate(o, t) for o in per_seed])
        out[f"continuation_{t}"], out[f"continuation_{t}_sd"] = m, sd
    out["dissolution_rate"], out["dissolution_rate_sd"] = _mean_sd([dissolution_rate(o) for o in per_seed])
    all_outcomes = [o for batch in per_seed for o in batch]
    out["duration"] = duration_summary(all_outcomes)
    out["survival"] = survival_curve(all_outcomes, years)
    out["theoretical_survival"] = rd.theoretical_survival(recs)
    out["trajectory"] = recs
    return out


def compare_strategies(scenario, params, events=(), strategies=ds.STRATEGIES, replicates=200, seeds=(0,),
                       years=None, reference="workload"):
    """{戦略: evaluate_strategy の結果}。同じ初期条件・同じイベント・同じ乱数（共通乱数）で比べる"""
    candidates = ds.candidate_grid(params["share_step"])
    return {s: evaluate_strategy(scenario, s, params, events, replicates, seeds, years, reference, candidates)
            for s in strategies}


def format_table(rows, columns):
    """文字の表。rows = [辞書]、columns = [(キー, 見出し, 書式)]。値が None なら "-" """
    cells = [[("-" if r.get(k) is None else f.format(r[k])) for k, _h, f in columns] for r in rows]
    heads = [h for _k, h, _f in columns]
    widths = [max(len(h), *(len(c[i]) for c in cells)) if cells else len(h) for i, h in enumerate(heads)]
    lines = ["  ".join(h.ljust(w) if i == 0 else h.rjust(w) for i, (h, w) in enumerate(zip(heads, widths)))]
    for c in cells:
        lines.append("  ".join(v.ljust(w) if i == 0 else v.rjust(w) for i, (v, w) in enumerate(zip(c, widths))))
    return "\n".join(lines)


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：公平性の基準（reference）を変えて、どの分担が「公平」と評価されるかを比べる（RQ1）。
# TODO 2：公平性指標の重み（weights）を変える。満足度の差だけで評価するとどうなるか。
# TODO 3：シード数・反復回数を増やして、継続率のばらつき（_sd）がどう変わるか調べる。
# TODO 4：平均満足度・最低満足度・公平性・継続率の 4 つを同時に評価する方法を考える（Advanced D）。
