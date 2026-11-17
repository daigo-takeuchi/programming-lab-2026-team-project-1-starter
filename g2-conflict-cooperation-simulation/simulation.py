# G2：反復シミュレーション（1 ステップ = 1 年）とモンテカルロ法
#
#   各年、ネットワークのすべてのエッジ（国家ペア）について、エッジの順に：
#     1. 2 国がそれぞれ、そのペアの履歴にもとづいて行動を選ぶ（戦略）
#     2. 利得を計算し、各国の累積利得に足す
#     3. ペアの信頼度を更新する（trust_model）
#     4. ペアの関係状態を確率的に更新する（state_transitions）
#     5. 結果を記録する
#
# ・隣の関係からの波及：あるペアの状態遷移は、そのペアと国家を共有する「隣のペア」の前年の状態に影響される
#   （spillover_effect。0 なら各ペアは独立に変化し、ネットワーク構造は結果にほとんど影響しない）。
# ・2 国モデル = エッジが 1 本のネットワーク。
# ・乱数は (シード, 反復番号) で決まる。同じシードなら必ず同じ結果になる。
# ・協調支援政策（対話・協定など）は乱数の使い方を変えないので、政策が違っても同じ乱数列で比べられる（共通乱数）。

import copy
import json
import random
import statistics

import agents as ag
import game_theory as gt
import state_transitions as st
import trust_model as tm

PARAMS_PATH = ag.DATA_DIR / "simulation_parameters.json"
HORIZONS = (10, 20, 50)
POLICY_TYPES = ("dialogue", "agreement", "trust_building", "economic_cooperation")


def load_parameters(path=PARAMS_PATH):
    with open(path, encoding="utf-8") as f:
        p = json.load(f)
    validate_parameters(p)
    return p


def validate_parameters(p):
    for k in ("simulation_years", "monte_carlo_runs", "random_seed", "action_noise", "conditional", "trust",
              "transition", "policy"):
        if k not in p:
            raise ValueError(f"パラメータ {k} がありません")
    if not 0 <= p["action_noise"] <= 1:
        raise ValueError("action_noise は 0〜1 にしてください")
    st.validate_transition_params(p["transition"])
    return True


def with_changes(params, **changes):
    """一部を変えたコピー。入れ子は "transition.dialogue_effect" のように "." で指定する（感度分析用）"""
    p = copy.deepcopy(params)
    for key, value in changes.items():
        target = p
        parts = key.split(".")
        for part in parts[:-1]:
            target = target[part]
        if parts[-1] not in target:
            raise KeyError(f"パラメータ {key} がありません")
        target[parts[-1]] = value
    validate_parameters(p)
    return p


def edge_neighbors(edges):
    """各エッジについて、国家を共有する他のエッジのリスト"""
    out = {}
    for e in edges:
        out[e] = [f for f in edges if f != e and (f[0] in e or f[1] in e)]
    return out


def neighbor_spillover(states, neighbors):
    """隣のエッジの状態の平均：(協調の数 − 緊張の数 − 紛争状態の数) ÷ 隣の数（−1〜1。隣がなければ 0）"""
    if not neighbors:
        return 0.0
    score = sum(1 if states[f] == "Cooperation" else -1 if states[f] in ("Tension", "Conflict") else 0
                for f in neighbors)
    return score / len(neighbors)


def apply_policy(relation, policy, params):
    """協調支援政策を国家ペアに適用する（仮想的な政策操作）"""
    pp = params["policy"]
    if policy == "dialogue":
        relation["dialogue"] = True
    elif policy == "agreement":
        relation["agreement"] = True
    elif policy == "trust_building":
        relation["trust"] = tm.clip(relation["trust"] + pp["trust_building_bonus"])
    elif policy == "economic_cooperation":
        relation["interdependence_bonus"] = pp["economic_cooperation_bonus"]
    else:
        raise ValueError(f"政策 {policy!r} は {POLICY_TYPES} のどれかにしてください")
    return relation


def simulate(countries, edges, params, payoff, years=None, seed=None, run=0, dialogue=False, agreement=False,
             supported=(), policy=None):
    """ネットワーク上の反復シミュレーション

    dialogue / agreement：True なら全ペアで対話・協定がある
    supported           ：協調支援政策を行うエッジ。policy（省略時は params["policy"]["type"]）を適用する
    戻り値：{"records": [年ごとの記録（0 年目 = 初期状態）], "payoff": {国家: 累積利得}, "edges": edges}
    """
    years = int(params["simulation_years"] if years is None else years)
    seed = params["random_seed"] if seed is None else seed
    rng = random.Random(f"{seed}|{run}")
    cs = {c["id"]: copy.deepcopy(c) for c in countries}
    for c in cs.values():
        c["cumulative_payoff"], c["last_action"] = 0.0, None
    tp = params["transition"]
    edges = sorted(edges)
    rel = {}
    for u, v in edges:
        rel[(u, v)] = ag.make_relation(cs[u], cs[v], tp["initial_state"], dialogue, agreement)
    policy = policy or params["policy"]["type"]
    for e in supported:
        apply_policy(rel[e], policy, params)
    hist = {(u, v): ([], []) for u, v in edges}           # (u の行動の履歴, v の行動の履歴)
    nbrs = edge_neighbors(edges)
    spill = tp.get("spillover_effect", 0.0)
    records = [_record(0, rel, {}, {}, 0)]
    for t in range(1, years + 1):
        actions, pays, shocks = {}, {}, 0
        prev_states = {e: rel[e]["state"] for e in edges}     # 波及は前年の状態から（エッジの処理順に依存しない）
        for e in edges:
            u, v = e
            r = rel[e]
            hu, hv = hist[e]
            a = gt.choose_action(cs[u]["strategy"], cs[u], hu, hv, r["trust"], rng, params, r["interdependence_bonus"])
            b = gt.choose_action(cs[v]["strategy"], cs[v], hv, hu, r["trust"], rng, params, r["interdependence_bonus"])
            pa, pb = gt.payoffs(payoff, a, b)
            cs[u]["cumulative_payoff"] += pa
            cs[v]["cumulative_payoff"] += pb
            cs[u]["last_action"], cs[v]["last_action"] = a, b
            hu.append(a)
            hv.append(b)
            r["history"].append((a, b))
            extra = spill * neighbor_spillover(prev_states, nbrs[e]) if spill else 0.0
            r["state"], shock = st.next_state(r["state"], a, b, r["trust"], r["dialogue"], r["agreement"], tp, rng,
                                              extra)
            r["trust"] = tm.update_trust(r["trust"], a, b, params["trust"], r["dialogue"], r["agreement"])
            r["tension"] = st.update_tension(r["tension"], r["state"], params["tension_smoothing"])
            shocks += shock
            actions[e], pays[e] = (a, b), (pa, pb)
        records.append(_record(t, rel, actions, pays, shocks))
    return {"records": records, "payoff": {k: c["cumulative_payoff"] for k, c in cs.items()}, "edges": edges,
            "years": years}


def _record(year, rel, actions, pays, shocks):
    edges = list(rel)
    n = len(edges)
    states = {e: rel[e]["state"] for e in edges}
    acts = list(actions.values())
    return {"year": year, "actions": dict(actions), "payoffs": dict(pays),
            "trust": {e: rel[e]["trust"] for e in edges}, "states": states,
            "tension": {e: rel[e]["tension"] for e in edges}, "shocks": shocks,
            "cooperation_rate": (sum((a == "C") + (b == "C") for a, b in acts) / (2 * len(acts))) if acts else None,
            "mutual_cooperation_rate": (sum(a == "C" and b == "C" for a, b in acts) / len(acts)) if acts else None,
            "cooperation_state_rate": sum(s == "Cooperation" for s in states.values()) / n if n else None,
            "tension_rate": sum(s == "Tension" for s in states.values()) / n if n else None,
            "conflict_rate": sum(s == "Conflict" for s in states.values()) / n if n else None,
            "mean_trust": sum(rel[e]["trust"] for e in edges) / n if n else None}


def simulate_pair(c1, c2, params, payoff, years=None, seed=None, run=0, **kw):
    """2 国モデル（エッジ 1 本）"""
    return simulate([c1, c2], [tuple(sorted((c1["id"], c2["id"])))], params, payoff, years, seed, run, **kw)


def monte_carlo(countries, edges, params, payoff, runs=None, seed=None, years=None, **kw):
    """runs 回の反復。戻り値：{"runs": [各回の要約], "summary": 平均とばらつき, "yearly": 年ごとの平均}"""
    import evaluation as ev
    runs = int(params["monte_carlo_runs"] if runs is None else runs)
    if runs < 1:
        raise ValueError("runs は 1 以上にしてください")
    summaries, yearly = [], None
    for r in range(runs):
        out = simulate(countries, edges, params, payoff, years, seed, r, **kw)
        summaries.append(ev.summarize_run(out))
        ys = [(rec["cooperation_rate"], rec["tension_rate"], rec["conflict_rate"], rec["cooperation_state_rate"])
              for rec in out["records"][1:]]
        yearly = [[0.0] * 4 for _ in ys] if yearly is None else yearly
        for i, row in enumerate(ys):
            for j in range(4):
                yearly[i][j] += row[j] / runs
    keys = [k for k, v in summaries[0].items() if isinstance(v, (int, float))]   # True/False は割合として平均する
    summary = {}
    for k in keys:
        vals = [float(s[k]) for s in summaries if s[k] is not None]
        summary[k] = statistics.mean(vals) if vals else None
        summary[k + "_sd"] = statistics.stdev(vals) if len(vals) > 1 else 0.0
    summary["runs"] = runs
    return {"runs": summaries, "summary": summary,
            "yearly": [{"year": i + 1, "cooperation_rate": y[0], "tension_rate": y[1], "conflict_rate": y[2],
                        "cooperation_state_rate": y[3]} for i, y in enumerate(yearly or [])]}


# TODO 1：シミュレーション年数（10・20・50）と反復回数（monte_carlo_runs）を変える。
# TODO 2：国家が戦略を途中で変える（適応的戦略、Advanced B）。
