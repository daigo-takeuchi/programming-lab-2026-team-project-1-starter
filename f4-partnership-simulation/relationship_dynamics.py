# F4：関係状態の時間変化（本研究の中心）
#
# 1 年 = 1 ステップ。毎年、次の順に計算する（ループ・状態遷移）。
#
#   1. その年の生活条件を求める（ストレスイベントを反映：所得・労働時間・家事の総時間・生活費・ストレス）
#   2. 意思決定戦略が分担 (x, y) を決める（decision_strategies）
#   3. その年の満足度（効用）U_i を計算する（household_model）
#   4. 満足度を更新する     S_i(t) = clip((1 − alpha) × S_i(t−1) + alpha × U_i(t), 0, 1)
#   5. 関係全体の満足度     R(t) = (1 − m) × 平均(S_A, S_B) + m × 最低(S_A, S_B)
#   6. 関係解消確率         p(t) = clip(baseline + beta × (1 − R(t)) + gamma × Stress(t), 0, 1)
#   7. 一様乱数 u < p(t) なら関係解消（Core では再開しない。以後の意思決定・更新は止める）
#
# ・F3 では解消確率を外から与えたが、F4 では「関係状態（満足度）とストレス」から毎年計算する。
# ・係数はすべて教育用の架空の値。実際の離婚率や特定の関係の将来を予測しない。
# ・観測期間の終わりまで解消しなかった関係は「打ち切り」（その後どうなるかは分からない）として扱う。
# ・乱数は解消の判定だけに使う。乱数列は (シード, シナリオ, 反復番号) で決まり、戦略によらない
#   （共通乱数：戦略の違いだけを比べられる）。

import copy
import json
import random

import household_model as hm
import decision_strategies as ds
from partners import DATA_PATH, PARTNERS
from textbook.ssearch_while import seq_search

EVENT_TYPES = ("income_change", "work_hours_change", "housework_change", "expense_change")
CHECKPOINTS = (5, 10, 20)
PARAM_KEYS = ("base_satisfaction", "w_housework", "w_financial", "w_communication", "w_stress", "w_free_time",
              "w_overload", "w_fairness", "w_financial_strain", "strain_threshold", "communication_buffer", "discretionary_hours", "overload_scale_hours",
              "workload_scale_hours", "alpha", "relationship_min_weight", "baseline_hazard", "beta", "gamma",
              "base_stress", "stress_duration", "fairness_lambda", "share_step", "review_interval",
              "review_threshold", "simulation_years", "random_seed")


# ------------------------------------------------------------
# パラメータ
# ------------------------------------------------------------
def load_parameters(path=DATA_PATH):
    with open(path, encoding="utf-8") as f:
        params = json.load(f)["model_parameters"]
    validate_parameters(params)
    return params


def validate_parameters(params):
    missing = [k for k in PARAM_KEYS if k not in params]
    if missing:
        raise ValueError(f"パラメータがありません：{missing}")
    for k in ("alpha", "relationship_min_weight", "baseline_hazard", "communication_buffer", "base_stress"):
        if not 0 <= params[k] <= 1:
            raise ValueError(f"{k} は 0〜1 にしてください（{params[k]!r}）")
    if not 0 <= params["strain_threshold"] < 1:
        raise ValueError(f"strain_threshold は 0 以上 1 未満にしてください（{params['strain_threshold']!r}）")
    for k in ("discretionary_hours", "overload_scale_hours", "workload_scale_hours"):
        if params[k] <= 0:
            raise ValueError(f"{k} は正の値にしてください（{params[k]!r}）")
    if int(params["simulation_years"]) < 1:
        raise ValueError("simulation_years は 1 以上にしてください")
    return True


def with_changes(params, **changes):
    """一部のパラメータだけを変えたコピー（感度分析用）"""
    p = dict(params)
    p.update(changes)
    validate_parameters(p)
    return p


# ------------------------------------------------------------
# 満足度の更新と解消確率
# ------------------------------------------------------------
def update_satisfaction(previous, current_utility, alpha):
    """S(t) = clip((1 − alpha) × S(t−1) + alpha × U(t), 0, 1)。alpha が大きいほど今年の条件にすぐ反応する"""
    return hm.clip((1 - alpha) * previous + alpha * current_utility)


def relationship_satisfaction(sa, sb, params):
    """関係全体の満足度：平均と最低の加重平均（m = relationship_min_weight。m = 0 なら平均だけ）"""
    m = params["relationship_min_weight"]
    return (1 - m) * (sa + sb) / 2 + m * min(sa, sb)


def dissolution_probability(rel_satisfaction, stress, params):
    """p(t) = clip(baseline + beta × (1 − R(t)) + gamma × Stress(t), 0, 1)"""
    return hm.clip(params["baseline_hazard"] + params["beta"] * (1 - rel_satisfaction) + params["gamma"] * stress)


# ------------------------------------------------------------
# 12 ストレスイベント
# ------------------------------------------------------------
def validate_event(ev):
    if ev.get("type") not in EVENT_TYPES:
        raise ValueError(f"イベントの種類 {ev.get('type')!r} は {EVENT_TYPES} のどれかにしてください")
    if not isinstance(ev.get("year"), int) or ev["year"] < 1:
        raise ValueError(f"イベントの年 {ev.get('year')!r} は 1 以上の整数にしてください")
    if ev["type"] in ("income_change", "work_hours_change") and ev.get("partner") not in PARTNERS:
        raise ValueError(f"{ev['type']} には partner（A または B）が必要です")
    if "change" not in ev:
        raise ValueError("イベントには change（変化量）が必要です")
    return True


def is_active(ev, year, length=None):
    """year 年にイベントが効いているか。length = None なら発生年以降ずっと"""
    if year < ev["year"]:
        return False
    return length is None or year < ev["year"] + length


def conditions_at(scenario, events, year, params):
    """year 年の (パートナー, 生活条件)。元のシナリオは変えない

    生活条件 = {"total_housework_hours", "annual_expenses", "stress"}
      ・所得の変化（income_change）       ：所得 × (1 + change)
      ・労働時間の変化（work_hours_change）：労働時間 + change、家事に使える時間 − change（0 未満にしない）
      ・家事の変化（housework_change）     ：家事の総時間 + change
      ・生活費の変化（expense_change）     ：生活費 × (1 + change)
    条件の変化は duration 年（指定がなければずっと）続く。ストレスは発生から stress_duration 年だけ加わる。
    """
    partners = copy.deepcopy(scenario["partners"])
    cond = dict(scenario["household"])
    stress = params["base_stress"]
    for ev in events:
        validate_event(ev)
        if is_active(ev, year, ev.get("duration")):
            t, c = ev["type"], ev["change"]
            if t == "income_change":
                partners[ev["partner"]]["annual_income"] = max(0.0, partners[ev["partner"]]["annual_income"] * (1 + c))
            elif t == "work_hours_change":
                p = partners[ev["partner"]]
                p["weekly_work_hours"] = max(0.0, p["weekly_work_hours"] + c)
                p["available_housework_hours"] = max(0.0, p["available_housework_hours"] - c)
            elif t == "housework_change":
                cond["total_housework_hours"] = max(0.0, cond["total_housework_hours"] + c)
            elif t == "expense_change":
                cond["annual_expenses"] = max(0.0, cond["annual_expenses"] * (1 + c))
        if is_active(ev, year, ev.get("stress_duration", params["stress_duration"])):
            stress += ev.get("stress", 0.0)
    cond["stress"] = hm.clip(stress)
    return partners, cond


def event_years(events):
    return sorted({ev["year"] for ev in events})


# ------------------------------------------------------------
# 1 回のシミュレーション
# ------------------------------------------------------------
def pair_rng(seed, scenario_id, replicate):
    """(シード, シナリオ, 反復番号) ごとの乱数。戦略は含めない（共通乱数）"""
    return random.Random(f"{seed}|{scenario_id}|{replicate}")


def initial_record(scenario, params):
    x, y = hm.initial_allocation(scenario)
    sa, sb = scenario["partners"]["A"]["satisfaction"], scenario["partners"]["B"]["satisfaction"]
    return {"year": 0, "housework_share": x, "financial_share": y, "utility_A": None, "utility_B": None,
            "satisfaction_A": sa, "satisfaction_B": sb,
            "relationship_satisfaction": relationship_satisfaction(sa, sb, params),
            "stress": params["base_stress"], "dissolution_probability": None, "continuing": True,
            "feasible": None, "reviewed": False, "event": False}


def simulate(scenario, strategy, params, events=(), years=None, seed=None, replicate=0, dissolution=True,
             candidates=None):
    """1 組の関係を years 年シミュレーションする

    戻り値：{"records": [年ごとの記録（0 年目 = 初期状態）], "dissolved", "dissolution_year",
             "duration"（継続した年数）, "censored"（観測期間の終わりまで継続）, "observed_years"}
    dissolution=False なら解消の判定をしない（「続いた場合の」満足度の軌跡を見るとき）。
    """
    years = int(params["simulation_years"] if years is None else years)
    seed = params["random_seed"] if seed is None else seed
    candidates = ds.candidate_grid(params["share_step"]) if candidates is None else candidates
    rng = pair_rng(seed, scenario["id"], replicate)
    ev_years = set(event_years(events))

    rec0 = initial_record(scenario, params)
    history = [rec0]
    alloc = (rec0["housework_share"], rec0["financial_share"])
    sa, sb = rec0["satisfaction_A"], rec0["satisfaction_B"]
    dissolved_year = None
    for t in range(1, years + 1):
        partners, cond = conditions_at(scenario, events, t, params)
        review = strategy == "adaptive" and ds.needs_review(t, history, params, t in ev_years)
        new = ds.decide(strategy, alloc, partners, cond, params, candidates, review)
        if new is not None:            # 選べる候補がなければ前年の分担を続ける
            alloc = new
        x, y = alloc
        ua, ub = hm.utilities(x, y, partners, cond, params)
        sa = update_satisfaction(sa, ua, params["alpha"])
        sb = update_satisfaction(sb, ub, params["alpha"])
        rel = relationship_satisfaction(sa, sb, params)
        p = dissolution_probability(rel, cond["stress"], params)
        u = rng.random()               # 解消しない設定でも乱数は毎年 1 つ使う（乱数列をそろえる）
        ended = dissolution and u < p
        history.append({"year": t, "housework_share": x, "financial_share": y, "utility_A": ua, "utility_B": ub,
                        "satisfaction_A": sa, "satisfaction_B": sb, "relationship_satisfaction": rel,
                        "stress": cond["stress"], "dissolution_probability": p, "continuing": not ended,
                        "feasible": hm.is_feasible(x, y, partners, cond), "reviewed": review,
                        "event": t in ev_years, "no_candidate": new is None})
        if ended:                      # 解消後は意思決定も満足度の更新もしない
            dissolved_year = t
            break
    return {"scenario": scenario["id"], "strategy": strategy, "replicate": replicate, "seed": seed,
            "records": history, "dissolved": dissolved_year is not None, "dissolution_year": dissolved_year,
            "duration": dissolved_year if dissolved_year is not None else years,
            "censored": dissolved_year is None, "observed_years": years}


def trajectory(scenario, strategy, params, events=(), years=None, candidates=None):
    """関係が続いた場合の年ごとの記録（解消の判定なし）。この Core モデルでは乱数によらず決まる"""
    return simulate(scenario, strategy, params, events, years, dissolution=False, candidates=candidates)["records"]


def theoretical_survival(records):
    """記録の解消確率 p(t) から、t 年後まで継続している確率 Π(1 − p) を計算する（0 年目 = 1）"""
    out, s = [1.0], 1.0
    for r in records[1:]:
        s *= 1 - r["dissolution_probability"]
        out.append(s)
    return out


# ------------------------------------------------------------
# モンテカルロ（多数回の反復）
# ------------------------------------------------------------
def monte_carlo(scenario, strategy, params, events=(), replicates=200, seed=None, years=None, candidates=None):
    """replicates 回反復した結果（records を除いた要約のリスト）と、継続した場合の軌跡

    Core モデルでは乱数を解消の判定だけに使い、満足度の軌跡は乱数によらない。そこで
    軌跡を 1 回だけ計算し、反復ごとには「u(t) < p(t) となる最初の年」だけを線形探索で探す。
    simulate() を replicates 回呼ぶのと同じ結果になる（tests で確認）。計算量 O(候補数 × T + M × T)。
    """
    years = int(params["simulation_years"] if years is None else years)
    seed = params["random_seed"] if seed is None else seed
    recs = trajectory(scenario, strategy, params, events, years, candidates)
    probs = [r["dissolution_probability"] for r in recs[1:]]
    outcomes = []
    for rep in range(replicates):
        rng = pair_rng(seed, scenario["id"], rep)
        ended = [rng.random() < p for p in probs]
        idx = seq_search(ended, True)           # 関係解消年の検出（教科書の線形探索）
        year = None if idx == -1 else idx + 1
        outcomes.append({"scenario": scenario["id"], "strategy": strategy, "replicate": rep, "seed": seed,
                         "dissolved": year is not None, "dissolution_year": year,
                         "duration": year if year is not None else years, "censored": year is None,
                         "observed_years": years})
    return {"outcomes": outcomes, "trajectory": recs}


def continued_at(outcome, t):
    """t 年後に継続していれば True、解消していれば False、観測期間外なら None"""
    if t > outcome["observed_years"]:
        return None
    return outcome["dissolution_year"] is None or outcome["dissolution_year"] > t


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：alpha（満足度の更新速度）を 0.1、0.3、0.6 と変えて、満足度の軌跡と継続率を比べる。
# TODO 2：ストレスイベントの年・大きさ・種類を変える（data/sample_partnerships.json の stress_event_sets）。
# TODO 3：baseline_hazard・beta・gamma を変えて、継続率がどれだけ変わるか（感度分析）。
# TODO 4：関係全体の満足度を「平均だけ」（relationship_min_weight = 0）にして結果を比べる。
# TODO 5：ストレスを毎年確率的に発生させる（Advanced C）。
