# G1：国家・世界経済の成長と資源配分の最適化 ― 全体の流れを確認するデモ（補遺トピック）
#
#   python3 starter.py
#
# 教育用の架空モデルです。現実の国家の GDP・経済成長率・政策効果を予測するものではありません。

import economic_model as em
import simulation as sim
import allocation_strategies as al
import optimization as op
import evaluation as ev

STEP = 0.1                     # 配分の刻み（10%）
OBJECTIVE = "final_gdp"        # 最適化の目的関数（他：cumulative_gdp, final_living_standard, average_living_standard, weighted）

TODOS = [
    "投資効率・減耗率・遅延を変えて、成長経路を比べる（Notebook 01、experiments.py 5・6）",
    "新しい配分シナリオを作り、GDP と生活水準の順位を比べる（RQ1・RQ2、Notebook 02）",
    "評価期間 5・10・20・30 年で最適配分が変わるか調べる（RQ3、experiments.py 3）",
    "配分の刻み・初期配分・目的関数を変えて、3 つのアルゴリズムを比べる（RQ4、Notebook 03）",
    "総予算・投資効果・収穫逓減・遅延の仮定を変えて、最適配分の頑健性を調べる（RQ5、Notebook 05）",
    "GDP・生活水準・健康・人的資本を同時に改善できるか、トレードオフを調べる（RQ6、Notebook 04）",
    "結論が、どの目的関数・制約条件・モデルの仮定の下で成り立つかを書く",
]


def main():
    print("G1: Economic Growth and Resource Allocation")
    print("（補遺トピック。教育用の架空モデルで、現実の経済を予測しません）\n")

    # 1. 架空の経済データ
    params = em.load_economy()
    scenarios = al.load_scenarios()
    years = params["simulation_years"]
    print(f"[1] {params['country']}: 初期 GDP {params['initial_gdp']}, 人口 {params['population']}, "
          f"年間投資予算 {params['annual_investment_budget']}（架空の単位）, {years} 年間")
    print(f"    遅延：教育 {params['education_delay']} 年・研究開発 {params['rd_delay']} 年、"
          f"収穫逓減：投資効果 = 効率 × 投資額^{params['returns_exponent']}\n")

    # 2〜4. シナリオの比較
    print(f"{'Scenario':<26}{'Final GDP':>10}{'GDP/yr':>8}{'Living Standard':>17}  Allocation")
    rows = []
    for sc in scenarios:
        s = ev.summarize_run(sim.simulate(sc["shares"], params))
        rows.append((sc["label"], s))
        print(f"{sc['label']:<26}{s['final_gdp']:>10.1f}{s['gdp_growth_annual']:>8.2%}{s['final_living_standard']:>17.3f}"
              f"  {al.format_shares(sc['shares'])}")
    by_gdp = op.rank_candidates([n for n, _ in rows], [s["final_gdp"] for _, s in rows])
    by_ls = op.rank_candidates([n for n, _ in rows], [s["final_living_standard"] for _, s in rows])
    print(f"  Final GDP が最大      : {by_gdp[0][0]}")
    print(f"  Living Standard が最大: {by_ls[0][0]}")
    print("  ※ GDP と生活水準（教育用の人工的な指標）は別の指標です。\n")

    # 5〜9. 最適化アルゴリズム
    m = al.units_count(STEP)
    res = op.compare_algorithms(params, OBJECTIVE, STEP)
    print(f"Optimization:（目的関数 = {op.OBJECTIVE_LABELS[OBJECTIVE]}、刻み {STEP:.0%}、"
          f"候補 C({m}+3, 3) = {op.count_allocations(m)} 通り、{years} 年）")
    print(f"{'Algorithm':<20}{'Objective':>11}{'Gap':>9}{'Runtime':>11}{'Evaluations':>13}  Allocation")
    for r in res.values():
        print(f"{r['algorithm']:<20}{r['objective']:>11.2f}{r['gap']['absolute']:>9.3f}{r['runtime_s'] * 1e3:>9.1f}ms"
              f"{r['evaluations']:>13}  {al.format_shares(r['shares'])}")
    print("  Gap = 全探索の最良値 − その値（同じ離散探索空間）。全探索は離散探索空間の中で最適が保証される。")
    print("  Greedy 法・局所探索は保証がない（この条件で全探索と同じでも、条件が変わると違うことがある：experiments.py 2）。")
    ls = op.exhaustive(op.Evaluator(params, "final_living_standard"), m)
    print(f"  参考：生活水準を最大にする配分（全探索）: {al.format_shares(ls['shares'])}\n")

    # 10. 学生向け TODO
    print("Student Research TODOs:")
    for i, t in enumerate(TODOS, 1):
        print(f"  {i}. {t}")


if __name__ == "__main__":
    main()
