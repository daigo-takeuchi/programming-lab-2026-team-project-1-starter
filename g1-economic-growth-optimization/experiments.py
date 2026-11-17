# G1：学生向け研究実験の入口（Experiment 1〜7）
#
#   python3 experiments.py        … すべて実行
#   python3 experiments.py 2      … Experiment 2 だけ
#
# ここで出力するのは「最小限の観察」だけです。条件を広げた実験・考察はチームで行ってください。
# 結果はすべて教育用の架空モデルの計算値で、モデルの仮定・目的関数・制約条件によって変わります。

import sys

import economic_model as em
import simulation as sim
import allocation_strategies as al
import optimization as op
import evaluation as ev

STEP = 0.1         # 配分の刻み（TODO：0.2・0.05 に変える）


def _setup():
    return em.load_economy(), al.load_scenarios()


def _alloc_cols(prefix=""):
    return [(f"{prefix}{s}", em.SECTOR_LABELS[s][:5], "{:.0%}") for s in em.SECTORS]


def _flat(shares, prefix=""):
    return {f"{prefix}{s}": shares[s] for s in em.SECTORS}


def experiment_1():
    """投資配分：均等配分と重点配分を比べる（20 年）"""
    params, scenarios = _setup()
    rows = []
    for sc in scenarios:
        s = ev.summarize_run(sim.simulate(sc["shares"], params))
        rows.append({"name": sc["label"], **s})
    print("== Experiment 1：投資配分（20 年、架空モデル）")
    print(ev.format_table(rows, [("name", "Scenario", "{}"), ("final_gdp", "Final GDP", "{:.1f}"),
                                 ("gdp_growth_annual", "GDP/yr", "{:.2%}"), ("cumulative_gdp", "Cum. GDP", "{:.0f}"),
                                 ("final_living_standard", "Living Std", "{:.3f}"),
                                 ("final_health", "Health", "{:.2f}"), ("final_human_capital", "HumanCap", "{:.2f}"),
                                 ("final_technology", "Tech", "{:.2f}"), ("final_infrastructure", "Infra", "{:.2f}")]))
    for key, label in (("final_gdp", "Final GDP"), ("final_living_standard", "Living standard")):
        order = op.rank_candidates([r["name"] for r in rows], [r[key] for r in rows])
        print(f"  {label} の順位: " + " > ".join(name for name, _v in order))
    print("TODO：配分率を変えた新しいシナリオを追加する。GDP と生活水準の順位は同じか？\n")


def _algo_rows(results):
    rows = []
    for r in results.values():
        rows.append({"name": r["algorithm"], "objective": r["objective"], "gap": r["gap"]["absolute"],
                     "runtime_ms": r["runtime_s"] * 1e3, "evaluations": r["evaluations"],
                     "iterations": r["iterations"], **_flat(r["shares"])})
    return rows


ALGO_COLUMNS = ([("name", "Algorithm", "{}"), ("objective", "Objective", "{:.4f}"), ("gap", "Gap", "{:.4f}"),
                 ("runtime_ms", "Runtime ms", "{:.1f}"), ("evaluations", "Evals", "{}"), ("iterations", "Iter", "{}")]
                + _alloc_cols())


def experiment_2():
    """最適化アルゴリズム：全探索・Greedy 法・局所探索を同じ探索空間で比べる"""
    params, _ = _setup()
    print("== Experiment 2：最適化アルゴリズム（刻み 10%、20 年）")
    for objective in ("final_gdp", "final_living_standard"):
        res = op.compare_algorithms(params, objective, STEP)
        print(f"-- 目的関数：{op.OBJECTIVE_LABELS[objective]}（候補 {op.count_allocations(al.units_count(STEP))} 通り）")
        print(ev.format_table(_algo_rows(res), ALGO_COLUMNS))
    print("-- 条件を変えた例：returns_exponent = 0.8（収穫逓減が弱い）、目的関数 = 最終年の生活水準")
    p2 = em.with_changes(params, returns_exponent=0.8)
    for start_name, start in (("均等配分に近い点", None),
                              ("教育 100%", {"education": 1.0, "rd": 0.0, "infrastructure": 0.0, "healthcare": 0.0})):
        res = op.compare_algorithms(p2, "final_living_standard", STEP, start=start)
        print(f"   局所探索の初期配分：{start_name}（{res['local_search']['start']}）")
        print(ev.format_table(_algo_rows(res), ALGO_COLUMNS))
    print("Gap = 全探索の最良値 − その値（同じ離散探索空間）。0 なら全探索と同じ値")
    print("TODO：Greedy 法・局所探索が全探索に届かない条件を探し、その理由を説明する。\n")


def experiment_3():
    """評価期間：5・10・20・30 年で最適配分（全探索）が変わるか"""
    params, _ = _setup()
    rows = []
    for objective in ("final_gdp", "final_living_standard"):
        for years in sim.HORIZONS:
            r = op.exhaustive(op.Evaluator(params, objective, years), al.units_count(STEP))
            rows.append({"name": f"{op.OBJECTIVE_LABELS[objective]} / {years}y", "objective": r["objective"],
                         **_flat(r["shares"])})
    print("== Experiment 3：評価期間と最適配分（全探索、刻み 10%）")
    print(ev.format_table(rows, [("name", "Objective / horizon", "{}"), ("objective", "Best", "{:.3f}")] + _alloc_cols()))
    print("TODO：短期と長期で最適配分が違うなら、どの仮定（遅延・減耗）がその違いを生むか調べる。\n")


def experiment_4():
    """目的関数：GDP 最大化と生活水準最大化を比べる"""
    params, _ = _setup()
    m = al.units_count(STEP)
    rows = []
    best = {}
    for objective in op.OBJECTIVES:
        r = op.exhaustive(op.Evaluator(params, objective), m)
        best[objective] = r["shares"]
    for objective, shares in best.items():
        s = ev.summarize_run(sim.simulate(shares, params))
        rows.append({"name": f"max {op.OBJECTIVE_LABELS[objective]}", **_flat(shares), **s})
    print("== Experiment 4：目的関数ごとの最適配分と、その配分での各指標（20 年、刻み 10%）")
    print(ev.format_table(rows, [("name", "Optimized for", "{}")] + _alloc_cols()
                          + [("final_gdp", "Final GDP", "{:.1f}"), ("final_gdp_per_capita", "GDP/cap", "{:.2f}"),
                             ("final_living_standard", "Living Std", "{:.3f}"), ("final_health", "Health", "{:.2f}"),
                             ("final_human_capital", "HumanCap", "{:.2f}")]))
    print("TODO：生活水準の重み（living_standard_weight_*）や weighted の gdp_weight を変える。\n")


def experiment_5():
    """投資効果の遅延：教育・研究開発の遅延を変える"""
    params, _ = _setup()
    rows = []
    for edu, rd in ((0, 0), (3, 2), (5, 5), (8, 8)):
        p = em.with_changes(params, education_delay=edu, rd_delay=rd)
        for years in (10, 20):
            eq = ev.summarize_run(sim.simulate(al.equal_allocation(), p, years))
            r = op.exhaustive(op.Evaluator(p, "final_gdp", years), al.units_count(STEP))
            rows.append({"name": f"delay edu {edu} / R&D {rd}, {years}y", "equal_gdp": eq["final_gdp"],
                         "best": r["objective"], **_flat(r["shares"])})
    print("== Experiment 5：投資効果の遅延（目的関数：最終年の GDP、全探索）")
    print(ev.format_table(rows, [("name", "Condition", "{}"), ("equal_gdp", "Equal-alloc GDP", "{:.1f}"),
                                 ("best", "Best GDP", "{:.1f}")] + _alloc_cols()))
    print("TODO：遅延が長いと、短い評価期間で教育・研究開発への配分はどうなるか。\n")


def experiment_6():
    """収穫逓減：returns_exponent（1 = 逓減なし、0.5 = 平方根）を変える"""
    params, _ = _setup()
    rows = []
    for r_exp in (0.3, 0.5, 0.8, 1.0):
        p = em.with_changes(params, returns_exponent=r_exp)
        res = op.compare_algorithms(p, "final_gdp", STEP)
        r = res["exhaustive"]
        rows.append({"name": f"exponent {r_exp}", "best": r["objective"], "greedy_gap": res["greedy"]["gap"]["absolute"],
                     "local_gap": res["local_search"]["gap"]["absolute"], **_flat(r["shares"])})
    print("== Experiment 6：収穫逓減（目的関数：最終年の GDP、20 年）")
    print(ev.format_table(rows, [("name", "Returns", "{}"), ("best", "Best GDP", "{:.1f}"),
                                 ("greedy_gap", "Greedy gap", "{:.3f}"), ("local_gap", "Local gap", "{:.3f}")]
                          + _alloc_cols()))
    print("TODO：収穫逓減がないと、配分が 1 分野に集中しやすくなるか？ 投資額と効果のグラフで確かめる。\n")


def experiment_7():
    """感度分析：投資効率・減耗率・生活水準の重みを変える"""
    params, _ = _setup()
    changes = [("baseline", {}), ("rd_efficiency x1.5", {"rd_efficiency": params["rd_efficiency"] * 1.5}),
               ("education_efficiency x1.5", {"education_efficiency": params["education_efficiency"] * 1.5}),
               ("infra depreciation 0.10", {"infrastructure_depreciation": 0.10}),
               ("health depreciation 0.06", {"health_depreciation": 0.06}),
               ("LS weight GDP/cap 0.7", {"living_standard_weight_gdp_per_capita": 0.7,
                                          "living_standard_weight_health": 0.15,
                                          "living_standard_weight_human_capital": 0.15}),
               ("budget 50", {"annual_investment_budget": 50.0}), ("budget 200", {"annual_investment_budget": 200.0})]
    rows = []
    for name, ch in changes:
        p = em.with_changes(params, **ch)
        for objective in ("final_gdp", "final_living_standard"):
            r = op.exhaustive(op.Evaluator(p, objective), al.units_count(STEP))
            rows.append({"name": f"{name} / {'GDP' if objective == 'final_gdp' else 'LS'}", "best": r["objective"],
                         **_flat(r["shares"])})
    print("== Experiment 7：感度分析（全探索、20 年）")
    print(ev.format_table(rows, [("name", "Change / objective", "{}"), ("best", "Best", "{:.3f}")] + _alloc_cols()))
    print("TODO：最適配分が大きく変わるパラメータはどれか。結論はどの仮定の下で成り立つか。\n")


EXPERIMENTS = {"1": experiment_1, "2": experiment_2, "3": experiment_3, "4": experiment_4,
               "5": experiment_5, "6": experiment_6, "7": experiment_7}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(EXPERIMENTS)
    for k in keys:
        if k not in EXPERIMENTS:
            raise SystemExit(f"Experiment {k} はありません（1〜7）")
        EXPERIMENTS[k]()
