# F4：パートナーシップの安定性と意思決定 ― 全体の流れを確認するデモ
#
#   python3 starter.py
#
# 教育用の架空データ・架空モデルです。実際の離婚確率や特定の関係の将来を予測するものではありません。

import partners as pt
import household_model as hm
import decision_strategies as ds
import relationship_dynamics as rd
import evaluation as ev

SEEDS = range(5)       # 乱数シード
REPLICATES = 200       # シードごとの反復回数（継続率は 5 × 200 = 1,000 回の結果から計算）

TODOS = [
    "家事分担率・生活費の負担率を変えて、2 人の満足度を比べる（experiments.py 1・2、Notebook 01・02）",
    "公平性の基準（workload / equal / income / preference）を変えて、評価がどう変わるか調べる（RQ1）",
    "コミュニケーション指標と communication_buffer を変える（RQ3、experiments.py 3）",
    "fairness_lambda・見直し間隔を変えて、4 つの戦略を比べる（RQ4、Notebook 03）",
    "ストレスイベントの種類・年・大きさを変える（RQ5、experiments.py 5）",
    "1 年目の満足度が高い戦略と、20 年継続率が高い戦略は同じか（RQ6、Notebook 05）",
    "シード数・反復回数を増やし、平均とばらつきを報告する。結論がどの仮定に依存するかを書く",
]


def main():
    print("F4: Partnership Stability and Decision Making")
    print("（教育用の架空データ・架空モデル。実際の関係の将来を予測しません）\n")

    # 1. 架空のパートナーデータ
    scenarios = pt.load_scenarios()
    params = rd.load_parameters()
    events = pt.load_stress_events()
    sc = pt.scenario_by_id(scenarios, "A")
    p, household = sc["partners"], sc["household"]
    print("[1] パートナー（架空）")
    for pid in pt.PARTNERS:
        q = p[pid]
        print(f"  Partner {pid}: 年収 {q['annual_income']} 万円, 労働 {q['weekly_work_hours']} h/週, "
              f"家事に使える時間 {q['available_housework_hours']} h/週, 希望の家事分担 {q['preferred_housework_share']:.0%}, "
              f"希望の生活費負担 {q['preferred_financial_share']:.0%}, コミュニケーション {q['communication_score']}")
    print(f"  家事の総時間 {household['total_housework_hours']} h/週, 生活費 {household['annual_expenses']} 万円/年\n")

    # 2〜3. 家事分担・経済的負担・満足度（シナリオ A〜D の最初の分担）
    print("[2-3] シナリオごとの最初の分担と 1 年目の満足度（ストレスは基準値）")
    rows = []
    for s in scenarios:
        x, y = hm.initial_allocation(s)
        cond = dict(s["household"], stress=params["base_stress"])
        ha, hb = hm.housework_hours(x, cond["total_housework_hours"])
        fa, fb = hm.financial_amounts(y, cond["annual_expenses"])
        ua, ub = hm.utilities(x, y, s["partners"], cond, params)
        rows.append({"name": s["label"], "hw": f"{ha:.1f} / {hb:.1f}", "fin": f"{fa:.0f} / {fb:.0f}",
                     "A": ua, "B": ub, "mean": ev.mean_satisfaction(ua, ub), "min": ev.minimum_satisfaction(ua, ub),
                     "diff": ev.satisfaction_difference(ua, ub),
                     "feasible": "yes" if hm.is_feasible(x, y, s["partners"], cond) else "NO"})
    print(ev.format_table(rows, [("name", "Scenario", "{}"), ("hw", "Housework h A/B", "{}"),
                                 ("fin", "Expenses A/B", "{}"), ("A", "Sat A", "{:.3f}"), ("B", "Sat B", "{:.3f}"),
                                 ("mean", "Mean", "{:.3f}"), ("min", "Min", "{:.3f}"), ("diff", "Diff", "{:.3f}"),
                                 ("feasible", "Feasible", "{}")]))
    for s in scenarios:
        for msg in hm.feasibility_report(*hm.initial_allocation(s), s["partners"], s["household"]):
            print(f"  ※ {s['label']}: {msg}（実行不可能。超過分は満足度の減点として扱う）")
    print()

    # 4〜8. 4 つの戦略を、同じ初期条件・同じストレスイベント・同じ乱数で 20 年間比べる
    combined = events["combined"]
    print("[4-6] 4 つの意思決定戦略で 20 年間をシミュレーション（Scenario A の初期条件）")
    print("  ストレスイベント：" + "、".join(f"Year {e['year']} {e['note']}" for e in combined))
    res = ev.compare_strategies(sc, params, combined, ds.STRATEGIES, REPLICATES, SEEDS)
    print(f"  継続率は {len(SEEDS)} シード × {REPLICATES} 回の平均（± はシード間の標準偏差）\n")
    print(f"{'Strategy':<15}{'Mean Satisfaction':>18}{'Min Sat':>9}{'Fairness':>10}"
          f"{'5Y Cont.':>10}{'10Y Continuation':>18}{'20Y Cont.':>11}")
    for s in ds.STRATEGIES:
        r = res[s]
        print(f"{ds.LABELS[s]:<15}{r['mean_satisfaction']:>18.3f}{r['min_satisfaction']:>9.3f}{r['fairness']:>10.3f}"
              f"{r['continuation_5']:>10.1%}{r['continuation_10']:>11.1%} ±{r['continuation_10_sd']:>4.1%}"
              f"{r['continuation_20']:>11.1%}")
    print("  Mean/Min Satisfaction・Fairness：関係が続いた場合の 20 年間の平均（Fairness は基準 workload）\n")

    # 1 回分の記録の例
    one = rd.simulate(sc, "adaptive", params, combined, seed=params["random_seed"], replicate=0)
    print("[5] 1 回分の記録の例（Adaptive、最初の 10 年）")
    print("  year  x(hw A)  y(fin A)  Sat A  Sat B  Rel.Sat  Stress  p(dissolve)  state")
    for r in one["records"][1:11]:
        flag = "continuing" if r["continuing"] else "DISSOLVED"
        mark = " *event" if r["event"] else (" review" if r["reviewed"] else "")
        print(f"  {r['year']:>4}  {r['housework_share']:>7.2f}  {r['financial_share']:>8.2f}  {r['satisfaction_A']:.3f}"
              f"  {r['satisfaction_B']:.3f}  {r['relationship_satisfaction']:>7.3f}  {r['stress']:>6.2f}"
              f"  {r['dissolution_probability']:>11.3f}  {flag}{mark}")
    status = (f"Year {one['dissolution_year']} に解消" if one["dissolved"]
              else f"{one['observed_years']} 年の観測期間の終わりまで継続（打ち切り）")
    print(f"  → この 1 回は {status}。1 回の結果だけで判断しないこと。\n")

    # 7. ストレスイベントの影響
    print("[7] ストレスイベントの有無による 10 年継続率の違い（Adaptive）")
    rob = ev.robustness_to_stress(sc, "adaptive", params, combined, REPLICATES, SEEDS)
    print(f"  イベントなし {rob['without']['continuation_10']:.1%} → あり {rob['with']['continuation_10']:.1%}"
          f"（差 {rob['continuation_change']:+.1%}）、平均満足度の差 {rob['satisfaction_change']:+.3f}\n")

    # 8. 満足度と公平性の順位
    print("[8] 戦略の順位（モデルの仮定の下での結果）")
    for key, label in (("first_year_mean_utility", "1 年目の平均満足度"), ("min_satisfaction", "最低満足度"),
                       ("fairness", "公平性"), ("continuation_20", "20 年継続率")):
        order = ds.rank_strategies({s: res[s][key] for s in ds.STRATEGIES})
        print(f"  {label:<14}: " + " > ".join(ds.LABELS[s] for s, _v in order))
    print("  ※ 差が「± シード間の標準偏差」と同じくらいなら、優劣は判断できない。\n")

    # 9. 学生向け TODO
    print("Student Research TODOs:")
    for i, t in enumerate(TODOS, 1):
        print(f"  {i}. {t}")


if __name__ == "__main__":
    main()
