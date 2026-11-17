# F4：学生向け研究実験の入口（Experiment 1〜7）
#
#   python3 experiments.py        … すべて実行
#   python3 experiments.py 4      … Experiment 4 だけ
#
# ここで出力するのは「最小限の観察」だけです。条件を広げた実験・考察はチームで行ってください。
# 実験上の注意：同じ初期条件・同じストレスイベント・複数の乱数シードで比べ、平均とばらつきを報告する。
# 単一試行の結果だけで結論を出さない。戦略の優劣はモデルの仮定に依存する。

import sys

import partners as pt
import household_model as hm
import decision_strategies as ds
import relationship_dynamics as rd
import evaluation as ev

SEEDS = range(5)          # 乱数シード（TODO：増やす）
REPLICATES = 200          # シードごとの反復回数（TODO：増やす）


def _setup():
    scenarios = pt.load_scenarios()
    return scenarios, rd.load_parameters(), pt.load_stress_events()


def _alloc_row(name, x, y, partners, cond, params):
    ua, ub = hm.utilities(x, y, partners, cond, params)
    row = {"name": name, "x": x, "y": y, "A": ua, "B": ub, "mean": ev.mean_satisfaction(ua, ub),
           "min": ev.minimum_satisfaction(ua, ub), "diff": ev.satisfaction_difference(ua, ub),
           "feasible": "yes" if hm.is_feasible(x, y, partners, cond) else "NO"}
    for ref in ev.FAIRNESS_REFERENCES:
        row["fair_" + ref] = ev.fairness_index(x, y, ua, ub, partners, cond, ref)
    return row


ALLOC_COLUMNS = [("name", "Rule", "{}"), ("x", "x(A hw)", "{:.2f}"), ("y", "y(A fin)", "{:.2f}"),
                 ("A", "U_A", "{:.3f}"), ("B", "U_B", "{:.3f}"), ("mean", "Mean", "{:.3f}"),
                 ("min", "Min", "{:.3f}"), ("diff", "Diff", "{:.3f}"), ("feasible", "Feasible", "{}")]
FAIR_COLUMNS = [("name", "Rule", "{}")] + [("fair_" + r, "fair:" + r, "{:.3f}") for r in ev.FAIRNESS_REFERENCES]


def experiment_1():
    """家事分担：分担ルールを変えて 2 人の満足度を比べる（生活費は 50:50 に固定）"""
    scenarios, params, _ = _setup()
    sc = pt.scenario_by_id(scenarios, "A")
    p, cond = sc["partners"], dict(sc["household"], stress=params["base_stress"])
    rules = [("50:50", 0.5), ("work hours", hm.work_hours_housework_share(p)),
             ("income", hm.income_housework_share(p)), ("concentrated 80:20", 0.8),
             ("concentrated 20:80", 0.2), ("preference", hm.preference_housework_share(p))]
    rows = [_alloc_row(name, x, 0.5, p, cond, params) for name, x in rules]
    print("== Experiment 1：家事分担（1 年目の満足度。生活費は 50:50）")
    print(ev.format_table(rows, ALLOC_COLUMNS))
    print("\n公平性指標（基準によって評価が変わる）")
    print(ev.format_table(rows, FAIR_COLUMNS))
    print("TODO：家事の総時間・希望分担・公平性の基準を変えて、評価の順位がどう変わるか調べる。\n")


def experiment_2():
    """経済的負担：50:50、所得比例、交渉（家事を固定して生活費だけを公平性つき目的関数で選ぶ）"""
    scenarios, params, _ = _setup()
    sc = pt.scenario_by_id(scenarios, "A")
    p, cond = sc["partners"], dict(sc["household"], stress=params["base_stress"])
    x = 0.5
    cands = ds.candidate_grid(params["share_step"], housework_shares=[x])
    negotiated = ds.fairness_allocation(p, cond, params, cands)
    rules = [("50:50", 0.5), ("income-proportional", hm.income_share(p)),
             ("preference", hm.preference_financial_share(p)),
             ("negotiated", negotiated[1] if negotiated else None)]
    rows = [_alloc_row(name, x, y, p, cond, params) for name, y in rules if y is not None]
    print("== Experiment 2：生活費の負担（1 年目の満足度。家事は 50:50）")
    print(ev.format_table(rows, ALLOC_COLUMNS))
    print("TODO：fairness_lambda を変えると「交渉」の結果がどう変わるか。所得が変わったら？\n")


def experiment_3():
    """コミュニケーション：指標を変えて満足度と継続率を比べる（Fixed 50:50 と Adaptive）"""
    scenarios, params, events = _setup()
    base = pt.scenario_by_id(scenarios, "C")       # 家事が A に集中している条件
    rows = []
    for level in (0.2, 0.5, 0.8):
        sc = pt.with_communication(base, level)
        for strategy in ("fixed", "adaptive"):
            r = ev.compare_strategies(sc, params, events["none"], [strategy], REPLICATES, SEEDS)[strategy]
            rows.append({"name": f"comm={level} {ds.LABELS[strategy]}", **r})
    print("== Experiment 3：コミュニケーション（Scenario C の分担から開始、ストレスイベントなし）")
    print(ev.format_table(rows, SUMMARY_COLUMNS))
    print("TODO：communication_buffer = 0 にすると差はどう変わるか（RQ3）。\n")


SUMMARY_COLUMNS = [("name", "Condition", "{}"), ("mean_satisfaction", "MeanSat", "{:.3f}"),
                   ("min_satisfaction", "MinSat", "{:.3f}"), ("satisfaction_diff", "Diff", "{:.3f}"),
                   ("fairness", "Fairness", "{:.3f}"), ("continuation_10", "10Y", "{:.1%}"),
                   ("continuation_10_sd", "10Y sd", "{:.1%}"), ("continuation_20", "20Y", "{:.1%}")]


def experiment_4():
    """意思決定戦略：Fixed、Greedy、Fairness-aware、Adaptive を同じ条件で比べる"""
    scenarios, params, events = _setup()
    sc = pt.scenario_by_id(scenarios, "A")
    res = ev.compare_strategies(sc, params, events["combined"], ds.STRATEGIES, REPLICATES, SEEDS)
    rows = [{"name": ds.LABELS[s], **r} for s, r in res.items()]
    print("== Experiment 4：意思決定戦略（Scenario A の初期条件、ストレスイベント combined）")
    print(ev.format_table(rows, SUMMARY_COLUMNS + [("first_year_mean_utility", "Year1 U", "{:.3f}")]))
    print("10 年継続率の順位：", [ds.LABELS[s] for s, _v in
                              ds.rank_strategies({s: r["continuation_10"] for s, r in res.items()})])
    print("TODO：順位の差は、シード間のばらつき（10Y sd）より大きいか？\n")


def experiment_5():
    """ストレスイベント：種類ごとに、イベント前後の関係満足度と継続率を比べる"""
    scenarios, params, events = _setup()
    sc = pt.scenario_by_id(scenarios, "A")
    rows = []
    for name in ("none", "income_drop", "work_increase", "housework_increase", "expense_increase", "combined"):
        for strategy in ("fixed", "adaptive"):
            r = ev.compare_strategies(sc, params, events[name], [strategy], REPLICATES, SEEDS)[strategy]
            resp = ev.stress_response(r["trajectory"], 5) if name != "none" else None
            rows.append({"name": f"{name} / {ds.LABELS[strategy]}", **r,
                         "change": None if resp is None else resp["change"]})
    print("== Experiment 5：ストレスイベント（Year 5 に発生。combined は Year 5 と Year 8）")
    print(ev.format_table(rows, SUMMARY_COLUMNS + [("change", "dR(Y5)", "{:+.3f}")]))
    print("dR(Y5)：イベント前 2 年とイベント後 2 年の関係満足度の差")
    print("TODO：イベントの年・大きさを変える。複数のイベントが重なると？\n")


def experiment_6():
    """長期継続：シナリオ A〜D の 5・10・20 年継続率"""
    scenarios, params, events = _setup()
    rows = []
    for sc in scenarios:
        r = ev.compare_strategies(sc, params, events["combined"], [sc["strategy"]], REPLICATES, SEEDS)[sc["strategy"]]
        rows.append({"name": sc["label"], **r})
    cols = [("name", "Scenario", "{}"), ("continuation_5", "5Y", "{:.1%}"), ("continuation_10", "10Y", "{:.1%}"),
            ("continuation_20", "20Y", "{:.1%}"), ("continuation_20_sd", "20Y sd", "{:.1%}"),
            ("dissolution_rate", "Dissolved", "{:.1%}"), ("mean_satisfaction", "MeanSat", "{:.3f}")]
    print("== Experiment 6：長期継続（ストレスイベント combined）")
    print(ev.format_table(rows, cols))
    print("TODO：シナリオのどの違い（分担・コミュニケーション・戦略）が効いているのか、1 つずつ変えて調べる。\n")


def experiment_7():
    """感度分析：満足度の重み・更新速度・基準解消確率を変えたときの 10 年継続率"""
    scenarios, params, events = _setup()
    sc = pt.scenario_by_id(scenarios, "A")
    changes = [("baseline", {}), ("alpha=0.1", {"alpha": 0.1}), ("alpha=0.6", {"alpha": 0.6}),
               ("baseline_hazard=0.03", {"baseline_hazard": 0.03}), ("beta=0.06", {"beta": 0.06}),
               ("w_housework=0.3", {"w_housework": 0.3}), ("w_fairness=0.6", {"w_fairness": 0.6}),
               ("min_weight=0", {"relationship_min_weight": 0.0})]
    rows = []
    for name, ch in changes:
        p = rd.with_changes(params, **ch)
        res = ev.compare_strategies(sc, p, events["combined"], ds.STRATEGIES, REPLICATES, SEEDS)
        row = {"name": name}
        for s in ds.STRATEGIES:
            row[s] = res[s]["continuation_10"]
        rows.append(row)
    cols = [("name", "Change", "{}")] + [(s, ds.LABELS[s], "{:.1%}") for s in ds.STRATEGIES]
    print("== Experiment 7：感度分析（10 年継続率、Scenario A の初期条件、combined）")
    print(ev.format_table(rows, cols))
    print("TODO：戦略の順位が入れ替わるパラメータはあるか？ 結論はどの仮定の下で成り立つか？\n")


EXPERIMENTS = {"1": experiment_1, "2": experiment_2, "3": experiment_3, "4": experiment_4,
               "5": experiment_5, "6": experiment_6, "7": experiment_7}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(EXPERIMENTS)
    for k in keys:
        if k not in EXPERIMENTS:
            raise SystemExit(f"Experiment {k} はありません（1〜7）")
        EXPERIMENTS[k]()
