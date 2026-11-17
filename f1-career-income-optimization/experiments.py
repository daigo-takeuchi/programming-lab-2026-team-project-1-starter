# F1：学生向け研究実験の入口（Experiment 1〜5）
#
# 各実験は「最小限の観察」だけを行う。条件を広げた実験、表・グラフ化、考察は学生が行う（各関数の TODO）。
#
#   python3 experiments.py        すべての実験を実行
#   python3 experiments.py 3      Experiment 3 だけ実行
#
# 金額の単位は万円。すべて架空のデータ（data/sample_careers.json）にもとづく教育用の計算。

import csv
import sys

import income_analysis as ia
import optimization as op
import scenarios as sc


def by_name(careers, name):
    for s in careers:
        if s["name"] == name:
            return s
    raise KeyError(name)


def without(scenario, key):
    """certificate や job_change を外した、比較の基準になるシナリオ（コピー）"""
    return sc.with_changes(scenario, **{key: None, "name": scenario["name"] + "_base",
                                        "label": scenario.get("label", "") + " (base)"})


def write_csv(rows, path):
    """結果（辞書のリスト）を CSV に保存する（グラフは表計算ソフトや matplotlib で作る）"""
    keys = list(rows[0]) if rows else []
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def experiment1_education(careers, settings):
    """Experiment 1：進学の費用対効果 ―― 進学費用を変えて、累積純収入と投資回収年齢を見る"""
    print("=== Experiment 1：進学の費用対効果（University vs Early Job）===")
    base, uni = by_name(careers, "early_job"), by_name(careers, "university")
    print(f"  {'education_cost':>15}{'net (uni)':>12}{'net gap':>10}{'payback age':>13}")
    for cost in [0, 200, 400, 800]:
        s = sc.with_changes(uni, education_cost=cost)
        p = ia.payback_age(s, base)
        gap = ia.cumulative_net_income(s) - ia.cumulative_net_income(base)
        print(f"  {cost:>15}{ia.cumulative_net_income(s):>12.0f}{gap:>10.0f}{p['payback_age'] or p['status']!s:>13}")
    # TODO 1-1：進学後の初年度年収 initial_salary を変える（例：280, 300, 330, 360）。
    # TODO 1-2：昇給率 annual_growth_rate を変える。進学しても昇給率が同じ（2%）なら結果はどうなるか。
    # TODO 1-3：20 歳で就職（vocational）も含めて、RQ1 の 3 つを表にまとめる。
    # TODO 1-4：「進学すると年収・昇給率が上がる」という仮定そのものの根拠と限界を考える（README 5章・17章）。


def experiment2_certificate(careers, settings):
    """Experiment 2：資格取得 ―― 取得年齢を変えて、回収年齢と生涯所得の差を見る"""
    print("=== Experiment 2：資格取得（Certificate vs 資格なし）===")
    cert = by_name(careers, "certificate")
    base = without(cert, "certificate")
    print(f"  {'cert age':>9}{'net gain':>10}{'payback age':>13}")
    for age in [25, 30, 40, 50, 60]:
        s = sc.with_changes(cert, **{"certificate.age": age})
        p = ia.payback_age(s, base)
        gain = ia.cumulative_net_income(s) - ia.cumulative_net_income(base)
        print(f"  {age:>9}{gain:>10.0f}{p['payback_age'] or p['status']!s:>13}")
    # TODO 2-1：資格取得費用 certificate.cost を変える。
    # TODO 2-2：取得後の年収増加 certificate.salary_increase を変える。
    # TODO 2-3：学習期間 study_years と学習中の年収の割合 study_income_ratio を変える（勉強のために仕事を減らす場合）。
    # TODO 2-4：「何歳までに取得すれば元が取れるか」を全探索で求める。


def experiment3_job_change(careers, settings):
    """Experiment 3：転職年齢 ―― 全探索で、評価基準ごとの最適な転職年齢を求める"""
    print("=== Experiment 3：転職年齢の全探索 ===")
    jc = by_name(careers, "job_change")
    first, last = settings.get("switch_age_range", [22, 60])
    # (転職後の初年度年収, 転職後の昇給率, 転職費用)
    for new_salary, growth, cost in [(420, 0.025, 30), (250, 0.025, 100)]:
        s = sc.with_changes(jc, **{"job_change.new_salary": new_salary, "job_change.growth_rate": growth,
                                   "job_change.cost": cost})
        rows = op.evaluate_switch_ages(s, op.switch_age_candidates(s, first, last), settings.get("discount_rate", 0.03))
        best = op.optimal_switch_ages(rows)
        text = ", ".join(f"{k}: {v['switch_age']} 歳" for k, v in best.items())
        print(f"  new_salary = {new_salary}, growth = {growth:.1%}, cost = {cost}：{text}（候補 {len(rows)} 通り）")
        stay = ia.evaluate(without(s, "job_change"), settings.get("discount_rate", 0.03))
        best_gross = best["gross"]["value"]
        print(f"    参考：転職しない場合 gross {stay['gross']:,.0f}（最適な転職 {best_gross:,.0f}）"
              f" → {'転職しない方が大きい' if stay['gross'] > best_gross else '転職した方が大きい'}")
    print("  ※ Core のモデルでは「転職後の初年度年収は年齢によらず一定」と仮定している。")
    print("  ※ 2 つ目の条件では、生涯所得と NPV で最適な転職年齢が大きく違う。理由を考えよう（RQ4）。")
    # TODO 3-0：「転職しない」も候補の 1 つとして全探索に含める（候補 K + 1 通り）。
    # TODO 3-1：転職年齢の範囲を変える。
    # TODO 3-2：転職費用 job_change.cost、転職後の昇給率 job_change.growth_rate を変える。
    # TODO 3-3：転職後の年収が経験年数に応じて増える（new_salary + k × (転職年齢 − 就職年齢)）ように scenarios.incomes を拡張し、
    #           最適な転職年齢が変わるか調べる。
    # TODO 3-4：転職年齢と生涯所得・NPV のグラフを作る（write_csv で保存して表計算ソフトで描くなど）。


def experiment4_discount_rate(careers, settings):
    """Experiment 4：割引率 ―― 割引率を変えると、NPV によるキャリアの順位が変わるか"""
    print("=== Experiment 4：割引率と NPV の順位 ===")
    for rate in [0.0, 0.01, 0.03, 0.05]:
        ranked = op.rank([ia.evaluate(s, rate) for s in careers], "npv")
        print(f"  r = {rate:.0%}: " + " > ".join(r["label"] for r in ranked))
    # TODO 4-1：各割引率での NPV の値を表にする（r = 0 の NPV が累積純収入と一致することも確かめる）。
    # TODO 4-2：順位が入れ替わる割引率を細かく探す（例：0.1% 刻み）。
    # TODO 4-3：なぜ割引率が高いと「早く稼ぐ」キャリアが有利になるのか、式から説明する。


def experiment5_sensitivity(careers, settings):
    """Experiment 5：感度分析 ―― 1 つの仮定を ±20% 変えたとき、累積純収入の差（University − Early Job）がどう変わるか"""
    print("=== Experiment 5：感度分析（University − Early Job の累積純収入の差）===")
    base, uni = by_name(careers, "early_job"), by_name(careers, "university")
    ref = ia.cumulative_net_income(uni) - ia.cumulative_net_income(base)
    print(f"  基準の差：{ref:.0f} 万円")
    for key in ["initial_salary", "annual_growth_rate", "education_cost"]:
        for factor in [0.8, 1.2]:
            s = sc.with_changes(uni, **{key: uni[key] * factor})
            diff = ia.cumulative_net_income(s) - ia.cumulative_net_income(base)
            print(f"  University の {key} × {factor}: 差 {diff:8.0f} 万円（基準から {diff - ref:+.0f}）")
    # TODO 5-1：Early Job 側の初年度年収・昇給率も変える。
    # TODO 5-2：資格取得費用・転職費用についても同様に調べる。
    # TODO 5-3：どの仮定に結果が最も敏感か、トルネード図（変化の大きい順の横棒グラフ）にまとめる。
    # TODO 5-4：NPV（割引率 3%）でも同じ感度分析をする。


EXPERIMENTS = {
    "1": experiment1_education,
    "2": experiment2_certificate,
    "3": experiment3_job_change,
    "4": experiment4_discount_rate,
    "5": experiment5_sensitivity,
}

if __name__ == "__main__":
    careers, settings = sc.load_scenarios()
    for key in sys.argv[1:] or list(EXPERIMENTS):
        if key not in EXPERIMENTS:
            raise SystemExit(f"Experiment {key} はありません（1〜5）")
        EXPERIMENTS[key](careers, settings)
        print()
    print("※ 架空のデータによる教育用の計算です。実際の所得の予測ではありません。")
