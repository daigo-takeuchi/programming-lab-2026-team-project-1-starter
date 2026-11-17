# G2：学生向け研究実験の入口（Experiment 1〜7）
#
#   python3 experiments.py        … すべて実行
#   python3 experiments.py 6      … Experiment 6 だけ
#
# 出力するのは「最小限の観察」だけです。条件を広げた実験・考察はチームで行ってください。
# 結果はすべて教育用の架空モデルの計算値で、モデルの仮定（利得行列・遷移確率・信頼度の係数）に依存します。

import sys
import time

import agents as ag
import game_theory as gt
import simulation as sim
import network_model as nm
import cooperation_policies as cp
import evaluation as ev

RUNS = 100          # モンテカルロの反復回数（TODO：増やす）
YEARS = 50

SUMMARY_COLUMNS = [("name", "Condition", "{}"), ("cooperation_rate", "Coop", "{:.3f}"),
                   ("cooperation_rate_sd", "sd", "{:.3f}"), ("mutual_cooperation_rate", "Mutual", "{:.3f}"),
                   ("cooperation_state_rate", "CoopState", "{:.3f}"), ("tension_rate", "Tension", "{:.3f}"),
                   ("conflict_rate", "Conflict", "{:.3f}"), ("conflict_rate_sd", "sd", "{:.3f}"),
                   ("average_payoff", "Payoff", "{:.2f}")]


def _setup():
    return ag.load_countries(), sim.load_parameters(), gt.load_payoff_matrix()


def _pair(strategy_a="conditional", strategy_b="conditional", trust=0.5):
    a = ag.make_country("A", 0.6, trust, 0.5, strategy_a)
    b = ag.make_country("B", 0.6, trust, 0.5, strategy_b)
    return a, b


def experiment_1():
    """戦略比較：同じ相手（Tit-for-Tat と Conditional）・同じ初期条件で 4 戦略を比べる（2 国、繰り返しゲーム）"""
    _cs, params, m = _setup()
    print("== Experiment 1：戦略比較（2 国の繰り返しゲーム 50 回、相手と初期条件は同じ）")
    print("   一回限りのゲームの Nash 均衡:", gt.nash_equilibria(m), "（囚人のジレンマ型:", gt.is_prisoners_dilemma(m), "）")
    for opp_strategy in ("tit_for_tat", "conditional"):
        rows = []
        for s in ag.STRATEGIES:
            me, opp = _pair(s, opp_strategy)
            r = gt.tournament([(s, me)], YEARS, m, params, seed=params["random_seed"], opponent=opp)[s]
            mc = sim.monte_carlo([me, opp], [("A", "B")], params, m, RUNS, years=YEARS)["summary"]
            rows.append({"name": gt.label(s), **r, "coop_mc": mc["cooperation_rate"],
                         "conflict_mc": mc["conflict_rate"]})
        print(f"-- 相手：{gt.label(opp_strategy)}")
        print(ev.format_table(rows, [("name", "Strategy", "{}"), ("first_round_payoff", "1st payoff", "{:.1f}"),
                                     ("average_payoff", "Avg payoff", "{:.2f}"),
                                     ("cooperation_rate", "Coop", "{:.2f}"),
                                     ("mutual_cooperation_rate", "Mutual", "{:.2f}"),
                                     ("coop_mc", f"Coop (MC {RUNS})", "{:.3f}"),
                                     ("conflict_mc", "Conflict (MC)", "{:.3f}")]))
    print("Coop・Mutual：1 回の繰り返しゲーム。MC：状態遷移を含むモンテカルロ平均")
    print("TODO：短期の利得（1st payoff）が大きい戦略は、長期の協調率も高いか（RQ5）。\n")


def experiment_2():
    """信頼度：初期信頼度を変える（5 国・リング）"""
    cs, params, m = _setup()
    edges = nm.make_network("ring", [c["id"] for c in cs])
    rows = []
    for trust in (0.1, 0.3, 0.5, 0.7, 0.9):
        s = sim.monte_carlo(ag.with_trust(cs, trust), edges, params, m, RUNS, years=YEARS)["summary"]
        rows.append({"name": f"initial trust {trust}", **s})
    print("== Experiment 2：初期信頼度（5 国・リング、モンテカルロ平均）")
    print(ev.format_table(rows, SUMMARY_COLUMNS + [("tension_duration", "TensionDur", "{:.2f}")]))
    print("TODO：信頼度の更新係数（trust.*）も変える。初期信頼度の影響は何年続くか（Notebook 02）。\n")


def experiment_3():
    """対話：対話・協定の有無。対照条件（対話が遷移確率に影響しないモデル）も比べる"""
    cs, params, m = _setup()
    edges = nm.make_network("ring", [c["id"] for c in cs])
    control = sim.with_changes(params, **{"transition.dialogue_affects_transitions": False})
    conds = [("no dialogue, no agreement", params, {}), ("dialogue", params, {"dialogue": True}),
             ("dialogue (control: no effect on transitions)", control, {"dialogue": True}),
             ("agreement", params, {"agreement": True}),
             ("dialogue + agreement", params, {"dialogue": True, "agreement": True})]
    rows = []
    for name, p, kw in conds:
        s = sim.monte_carlo(cs, edges, p, m, RUNS, years=YEARS, **kw)["summary"]
        rows.append({"name": name, **s})
    print("== Experiment 3：対話と協定（5 国・リング）")
    print(ev.format_table(rows, SUMMARY_COLUMNS + [("tension_duration", "TensionDur", "{:.2f}")]))
    print("対照条件では、対話は信頼度の更新だけに効く（遷移確率には直接効かない）。")
    print("TODO：対話の効果のうち、モデルに直接組み込んだ部分と、信頼度を通じた部分を分けて考察する（RQ3）。\n")


def experiment_4():
    """外部ショック：確率を変える"""
    cs, params, m = _setup()
    edges = nm.make_network("ring", [c["id"] for c in cs])
    rows = []
    for q in (0.0, 0.05, 0.1, 0.2):
        p = sim.with_changes(params, **{"transition.external_shock_probability": q})
        s = sim.monte_carlo(cs, edges, p, m, RUNS, years=YEARS)["summary"]
        rows.append({"name": f"shock probability {q}", **s})
    print("== Experiment 4：外部ショック（5 国・リング）")
    print(ev.format_table(rows, SUMMARY_COLUMNS))
    print("TODO：ショックの大きさ（1 段階 → 2 段階）や、特定の年だけのショックを試す（Advanced E）。\n")


def experiment_5():
    """ネットワーク構造：Line・Ring・Star・Random（サンプルの 5 国と、全員同じ属性の 5 国）"""
    cs, params, m = _setup()
    ids = [c["id"] for c in cs]
    same = [ag.make_country(i, 0.6, 0.5, 0.5, "conditional") for i in ids]
    rows = []
    for label, group in (("sample countries", cs), ("identical countries", same)):
        for kind in nm.NETWORK_TYPES:
            edges = nm.make_network(kind, ids, params["network"]["random_edge_probability"],
                                    params["network"]["random_seed"])
            s = sim.monte_carlo(group, edges, params, m, RUNS, years=YEARS)["summary"]
            met = nm.network_metrics(ids, edges)
            rows.append({"name": f"{kind} / {label}", "edges": met["edges"], "avg_degree": met["average_degree"], **s})
    print("== Experiment 5：ネットワーク構造")
    print(ev.format_table(rows, [("name", "Network / countries", "{}"), ("edges", "E", "{}"),
                                 ("avg_degree", "AvgDeg", "{:.1f}")] + SUMMARY_COLUMNS[1:]))
    print("サンプルの国家では、どの国どうしがつながるかも構造によって変わる（構造の効果と国家の属性の効果が混ざる）。")
    print("全員同じ属性の場合、構造の違いは「隣の関係からの波及」（spillover_effect）を通じてだけ現れる。")
    print("TODO：spillover_effect を 0・0.2・0.5 と変え、ノード数を増やして、構造の違いが現れるか調べる（RQ4）。\n")


def experiment_6():
    """協調支援の最適化：全探索と Greedy 法を、同じ候補集合・予算・評価関数で比べる"""
    cs, params, m = _setup()
    ids = [c["id"] for c in cs]
    print("== Experiment 6：協調支援の最適化（目的関数：stability = 1 − 緊張率 − 紛争状態率）")
    rows = []
    for kind, k in (("ring", 1), ("ring", 2), ("random", 2), ("random", 3)):
        edges = nm.make_network(kind, ids, params["network"]["random_edge_probability"], params["network"]["random_seed"])
        r = cp.compare(cs, edges, params, m, k)
        for key in ("exhaustive", "greedy"):
            x = r[key]
            rows.append({"name": f"{kind} E={len(edges)} K={k} / {x['algorithm']}", "objective": x["objective"],
                         "baseline": r["baseline"], "gap": x["gap"], "evaluations": x["evaluations"],
                         "runtime_ms": x["runtime_s"] * 1e3, "selected": " ".join(f"{u}-{v}" for u, v in x["selected"])})
    print(ev.format_table(rows, [("name", "Network / algorithm", "{}"), ("baseline", "No support", "{:.4f}"),
                                 ("objective", "Objective", "{:.4f}"), ("gap", "Gap", "{:.4f}"),
                                 ("evaluations", "Evals", "{}"), ("runtime_ms", "Runtime ms", "{:.0f}"),
                                 ("selected", "Supported edges", "{}")]))
    print("-- 例：8 国のランダムネットワーク、隣からの波及を強くした場合（spillover_effect 0.5、評価は 15 回 × 20 年）")
    rng = __import__("random").Random(2)
    ids8 = nm.node_names(8)
    cs8 = [ag.make_country(i, round(rng.uniform(0.3, 0.8), 2), round(rng.uniform(0.2, 0.8), 2),
                           round(rng.uniform(0.2, 0.8), 2), rng.choice(["conditional", "tit_for_tat"])) for i in ids8]
    p8 = sim.with_changes(params, **{"transition.spillover_effect": 0.5})
    edges8 = nm.make_network("random", ids8, 0.4, 2)
    r = cp.compare(cs8, edges8, p8, m, 3, runs=15, years=20)
    rows = [{"name": f"random 8 nodes E={len(edges8)} K=3 / {x['algorithm']}", "objective": x["objective"],
             "baseline": r["baseline"], "gap": x["gap"], "evaluations": x["evaluations"],
             "runtime_ms": x["runtime_s"] * 1e3, "selected": " ".join(f"{u}-{v}" for u, v in x["selected"])}
            for x in (r["exhaustive"], r["greedy"])]
    print(ev.format_table(rows, [("name", "Network / algorithm", "{}"), ("baseline", "No support", "{:.4f}"),
                                 ("objective", "Objective", "{:.4f}"), ("gap", "Gap", "{:.4f}"),
                                 ("evaluations", "Evals", "{}"), ("runtime_ms", "Runtime ms", "{:.0f}"),
                                 ("selected", "Supported edges", "{}")]))
    print("Gap = 全探索の値 − その値。評価は毎回モンテカルロ（共通乱数）")
    print("隣からの波及がないと、各エッジの支援効果は足し算になり、Greedy 法でも最適になりやすい。")
    print("TODO：ノード数を増やしたとき（8・10 国）、候補数 C(E, K) と実行時間はどう増えるか。\n")


def experiment_7():
    """感度分析：遷移確率・信頼度の更新係数・協調支援の効果を変える"""
    cs, params, m = _setup()
    edges = nm.make_network("ring", [c["id"] for c in cs])
    changes = [("baseline", {}), ("trust_effect 0.4", {"transition.trust_effect": 0.4}),
               ("trust_effect 0.0", {"transition.trust_effect": 0.0}),
               ("trust mutual coop +0.10", {"trust.mutual_cooperation": 0.10}),
               ("trust exploited -0.20", {"trust.exploited": -0.20}),
               ("action noise 0.0", {"action_noise": 0.0}), ("action noise 0.1", {"action_noise": 0.1}),
               ("dialogue_effect 0.30", {"transition.dialogue_effect": 0.30})]
    rows = []
    for name, ch in changes:
        p = sim.with_changes(params, **ch)
        s = sim.monte_carlo(cs, edges, p, m, RUNS, years=YEARS)["summary"]
        r = cp.compare(cs, edges, p, m, 2)
        rows.append({"name": name, **s, "best": " ".join(f"{u}-{v}" for u, v in r["exhaustive"]["selected"]),
                     "gain": r["exhaustive"]["improvement"]})
    print("== Experiment 7：感度分析（5 国・リング）")
    print(ev.format_table(rows, SUMMARY_COLUMNS[:2] + SUMMARY_COLUMNS[4:7]
                          + [("best", "Best 2 edges", "{}"), ("gain", "Gain", "{:.4f}")]))
    print("Best 2 edges・Gain：対話支援を 2 本に行うときの全探索の結果と、支援なしからの改善")
    print("TODO：結論（どのエッジを支援すべきか）が、どのパラメータに敏感か調べる。\n")


EXPERIMENTS = {"1": experiment_1, "2": experiment_2, "3": experiment_3, "4": experiment_4,
               "5": experiment_5, "6": experiment_6, "7": experiment_7}

if __name__ == "__main__":
    keys = sys.argv[1:] or list(EXPERIMENTS)
    for k in keys:
        if k not in EXPERIMENTS:
            raise SystemExit(f"Experiment {k} はありません（1〜7）")
        t0 = time.perf_counter()
        EXPERIMENTS[k]()
