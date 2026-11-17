# G2：国際紛争の抑止と協調戦略のシミュレーション ― 全体の流れを確認するデモ（補遺トピック）
#
#   python3 starter.py
#
# 教育用の抽象的な仮想モデルです。国家はすべて架空で、現実の国際関係・紛争や特定国家の行動を予測しません。
# 扱うのは協調・対話・信頼形成・緊張緩和だけです。

import agents as ag
import game_theory as gt
import trust_model as tm
import state_transitions as st
import simulation as sim
import network_model as nm
import cooperation_policies as cp
import evaluation as ev

TODOS = [
    "利得行列を変えて、戦略ごとの協調率と利得を比べる（RQ1・RQ5、Notebook 01）",
    "初期信頼度・信頼度の更新係数を変える（RQ2、experiments.py 2）",
    "対話・協定の有無と、対話が遷移確率に影響しない対照条件を比べる（RQ3、experiments.py 3）",
    "Line・Ring・Star・Random と隣からの波及（spillover_effect）を変えて比べる（RQ4、Notebook 04）",
    "支援予算・目的関数・ネットワークの大きさを変えて、全探索と Greedy 法を比べる（RQ6、Notebook 05）",
    "試行回数・乱数シードを変え、平均とばらつきを報告する（Notebook 03）",
    "結論が、どのモデルの仮定（利得・遷移確率・係数）の下で成り立つかを書く",
]


def main():
    print("G2: Conflict Prevention and Cooperation Simulation")
    print("（補遺トピック。教育用の抽象的な仮想モデルで、現実の国際関係を予測しません）\n")

    # 1. 架空国家データ
    countries = ag.load_countries()
    params = sim.load_parameters()
    m = gt.load_payoff_matrix()
    print("[1] 架空の国家:", ", ".join(f"{c['id']}({gt.label(c['strategy'])}, trust {c['trust']})" for c in countries))
    print(f"    利得行列（自分, 相手）: CC={gt.payoffs(m, 'C', 'C')} CN={gt.payoffs(m, 'C', 'N')} "
          f"NC={gt.payoffs(m, 'N', 'C')} NN={gt.payoffs(m, 'N', 'N')}")
    print(f"    一回限りのゲームの Nash 均衡: {gt.nash_equilibria(m)}（Nash 均衡と長期的な協調の維持は別の話）\n")

    # 2〜3. 2 国ゲーム：戦略別の協調率と利得（同じ相手 = Tit-for-Tat、同じ初期条件）
    years = 50
    opp = ag.make_country("O", 0.6, 0.5, 0.5, "tit_for_tat")
    rows = []
    for s in ag.STRATEGIES:
        me = ag.make_country("S", 0.6, 0.5, 0.5, s)
        g = gt.tournament([(s, me)], years, m, params, params["random_seed"], opponent=opp)[s]
        mc = sim.monte_carlo([me, opp], [("O", "S")], params, m, params["monte_carlo_runs"], years=years)["summary"]
        rows.append({"name": gt.label(s), **g, "coop_mc": mc["cooperation_rate"], "conflict_mc": mc["conflict_rate"]})
    print(f"[2-3] 2 国の繰り返しゲーム（相手 Tit-for-Tat、{years} 回）")
    print(f"{'Strategy':<22}{'Cooperation Rate':>17}{'Average Payoff':>16}{'1st Payoff':>12}"
          f"{'Coop (MC)':>11}{'Conflict (MC)':>15}")
    for r in rows:
        print(f"{r['name']:<22}{r['cooperation_rate']:>17.2f}{r['average_payoff']:>16.2f}{r['first_round_payoff']:>12.1f}"
              f"{r['coop_mc']:>11.3f}{r['conflict_mc']:>15.3f}")
    print(f"  MC：信頼度と状態遷移を含むモンテカルロ（{params['monte_carlo_runs']} 回の平均）\n")

    # 4. 信頼度の更新
    t = 0.5
    print("[4] 信頼度の更新（0.5 から）:", end=" ")
    for a, b in (("C", "C"), ("C", "C"), ("C", "N"), ("N", "N")):
        t = tm.update_trust(t, a, b, params["trust"])
        print(f"{a}{b}→{t:.2f}", end=" ")
    print("\n")

    # 5. 状態遷移シミュレーション（2 国、1 回）
    a, b = countries[0], countries[1]
    out = sim.simulate_pair(a, b, params, m, years=20)
    print(f"[5] 状態遷移（Country {a['id']} と {b['id']}、1 回、20 年）")
    print("    " + " ".join(r["states"][(a["id"], b["id"])][:4] for r in out["records"][1:]))
    print(f"    信頼度 {out['records'][0]['mean_trust']:.2f} → {out['records'][-1]['mean_trust']:.2f}"
          "（1 回の結果だけで判断しないこと）\n")

    # 6〜7. 5 国ネットワークとモンテカルロ
    ids = [c["id"] for c in countries]
    edges = nm.make_network(params["network"]["type"], ids)
    mc = sim.monte_carlo(countries, edges, params, m)
    s = mc["summary"]
    met = nm.network_metrics(ids, edges)
    print(f"Network:（{params['network']['type']}、{params['monte_carlo_runs']} 回 × {params['simulation_years']} 年）")
    print(f"  Nodes: {met['nodes']}  Edges: {met['edges']}  Average degree: {met['average_degree']:.1f}  "
          f"Connected Components: {met['components']}")
    print(f"  Cooperation rate {s['cooperation_rate']:.3f} (sd {s['cooperation_rate_sd']:.3f})  "
          f"Tension rate {s['tension_rate']:.3f}  Conflict-state rate {s['conflict_rate']:.3f} (sd {s['conflict_rate_sd']:.3f})")
    print(f"  協調状態の平均継続 {s['cooperation_duration']:.2f} 年、緊張状態の平均継続 {s['tension_duration']:.2f} 年\n")

    # 8. DFS と BFS
    adj = nm.adjacency_list(ids, edges)
    d, t_d = ev.measure_time(nm.dfs, adj, ids[0])
    bq, t_b = ev.measure_time(nm.bfs, adj, ids[0])
    print("[8] DFS と BFS（Country A から。O(V + E)）")
    print(f"  DFS: 訪問順 {' '.join(d['order'])}  訪問 {d['visited']}  スタック最大 {d['max_frontier']}  {t_d * 1e6:.1f} us")
    print(f"  BFS: 訪問順 {' '.join(bq['order'])}  訪問 {bq['visited']}  キュー最大 {bq['max_frontier']}  {t_b * 1e6:.1f} us")
    far = ids[-2]                                   # DFS と BFS で経路が違うことがある
    print(f"  {ids[0]} → {far} の経路：DFS {nm.path_to(d['parent'], far)}、BFS（最短）{nm.path_to(bq['parent'], far)}\n")

    # 9〜10. 協調支援の最適化
    r = cp.compare(countries, edges, params, m)
    ev_ = r["evaluator"]
    print(f"Cooperation Policy Optimization:（政策 {ev_.policy}、予算 {r['k']} 本、目的関数 {cp.OBJECTIVE_LABELS[ev_.objective]}、"
          f"評価 {ev_.runs} 回 × {ev_.years} 年）")
    print(f"{'Algorithm':<22}{'Objective':>10}{'Runtime':>11}{'Evaluations':>13}  Supported edges")
    print(f"{'No support':<22}{r['baseline']:>10.4f}")
    for x in (r["exhaustive"], r["greedy"]):
        print(f"{x['algorithm']:<22}{x['objective']:>10.4f}{x['runtime_s']:>10.2f}s{x['evaluations']:>13}  "
              + " ".join(f"{u}-{v}" for u, v in x["selected"]))
    print("  全探索は C(E, K) 通りを評価（この候補集合・評価方法の中で最適）。Greedy 法は保証なし。")
    print("  ※ 仮想的な政策操作のモデルで、現実の外交政策の有効性を表すものではありません。\n")

    print("Student Research TODOs:")
    for i, todo in enumerate(TODOS, 1):
        print(f"  {i}. {todo}")


if __name__ == "__main__":
    main()
