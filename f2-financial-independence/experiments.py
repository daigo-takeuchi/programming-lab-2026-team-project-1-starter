# F2：学生向け研究実験の入口（Experiment 1〜5）
#
# 各実験は「最小限の観察」だけを行う。条件を広げた実験・グラフ化・考察は学生が行う（各関数の TODO）。
# グラフは notebooks/ の Notebook で作る。
#
#   python3 experiments.py        すべての実験を実行
#   python3 experiments.py 3      Experiment 3 だけ実行
#
# 金額は万円。すべて架空のデータ（data/sample_scenarios.json）による教育用の計算。

import csv
import sys

import financial_model as fm
import fire_analysis as fa
import optimization as op
import retirement_model as rm


def fmt_age(age):
    return "not reached" if age is None else f"{age}"


def write_csv(rows, path):
    """結果（辞書のリスト）を CSV に保存する"""
    keys = []
    for r in rows:
        for k in r:
            if k not in keys:
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=keys)
        w.writeheader()
        w.writerows(rows)


def experiment1_savings_rate(scenarios, settings):
    """Experiment 1：貯蓄率 ―― 貯蓄率を変えて、65 歳時点の資産と FIRE 達成年齢を比べる（所得は固定）"""
    print("=== Experiment 1：貯蓄率（Standard を基準、所得 400 万円は固定）===")
    base = scenarios[0]
    print(f"  {'rate':>6}{'expenses':>10}{'target':>9}{'FIRE age':>12}{'assets@65':>11}")
    for r in op.sweep_savings_rate(base, op.DEFAULT_SAVINGS_RATES, settings, keep="income"):
        print(f"  {r['param']:>6.0%}{r['annual_expenses']:>10.0f}{r['target']:>9.0f}"
              f"{fmt_age(r['fire_age']):>12}{r['assets_at_report']:>11.0f}")
    # TODO 1-1：貯蓄率を 5% 刻みにして、FIRE 達成年齢のグラフを作る。
    # TODO 1-2：貯蓄率を上げると、FIRE 目標（生活費 / 4%）も下がる。2 つの効果を分けて説明する。
    # TODO 1-3：現役時の生活費（current_expenses）と FIRE 達成年齢のトレードオフを表にする。


def experiment2_return(scenarios, settings):
    """Experiment 2：収益率 ―― 収益率を変えて、複利の効果と FIRE 達成年齢を比べる"""
    print("=== Experiment 2：収益率（Standard を基準、貯蓄率 20%）===")
    base = scenarios[0]
    print(f"  {'return':>7}{'FIRE age':>12}{'assets@65':>11}{'contrib.':>10}{'gains':>9}")
    for ret in op.DEFAULT_RETURNS:
        s = fm.with_changes(base, annual_return=ret)
        acc = fm.accumulate(s, settings["report_age"])
        age = fa.fire_age(fm.accumulate(s, settings["accumulation_end_age"]),
                          fa.fire_target(s["annual_expenses"], settings["withdrawal_rate"]))
        print(f"  {ret:>7.0%}{fmt_age(age):>12}{acc[-1]['end_assets']:>11.0f}"
              f"{fm.total_contributions(acc):>10.0f}{fm.total_investment_return(acc):>9.0f}")
    print("  contrib. = 拠出した貯蓄の合計、gains = 投資収益の合計（65 歳まで）")
    # TODO 2-1：65 歳時点の資産のうち、投資収益が占める割合を収益率ごとに計算する。
    # TODO 2-2：収益率を 1% 上げる効果と、貯蓄率を 10% 上げる効果を比べる（仮説：README の例）。
    # TODO 2-3：収益率が負（例：-2%）の場合も調べる。


def experiment3_expenses(scenarios, settings):
    """Experiment 3：生活費 ―― 生活費を変えて FIRE 目標と達成年齢を比べる（所得固定 / 貯蓄率固定を区別）"""
    print("=== Experiment 3：生活費（Standard を基準）===")
    base = scenarios[0]
    expenses = [200, 240, 280, 320, 360]
    for keep, note in [("income", "所得 400 万円を固定（貯蓄率が変わる）"),
                       ("savings_rate", "貯蓄率 20% を固定（所得が変わる）")]:
        rows = op.sweep_expenses(base, expenses, settings, keep=keep)
        text = ", ".join(f"{r['param']}→{fmt_age(r['fire_age'])}" for r in rows)
        print(f"  {note}: 生活費→FIRE 年齢  {text}")
    # TODO 3-1：sweep_savings_rate の keep="income" と keep="expenses" を比べる。
    #           初期資産 0 のとき、2 つの結果が同じになるのはなぜか、式から考える。
    # TODO 3-2：初期資産を 500 万円にすると、上の関係はどう変わるか。
    # TODO 3-3：リタイア後の生活費を現役時と変える（例：8 割になる）と仮定した場合を調べる。


def experiment4_retirement(scenarios, settings):
    """Experiment 4：リタイア後の資産 ―― リタイア年齢・取り崩し額を変えて、資産の持続期間を比べる"""
    print("=== Experiment 4：リタイア後の資産（High Savings を基準）===")
    s = scenarios[1]
    acc = fm.accumulate(s, settings["accumulation_end_age"])
    end = settings["retirement_end_age"]
    print(f"  {'retire at':>10}{'assets':>8}{'expenses':>10}{'depletion':>11}{'years':>7}")
    for age in [45, 50, 55, 60]:
        for expenses in [200, 240, 280]:
            rows = rm.simulate_withdrawal(age, end, fm.assets_at(acc, age), expenses, s["annual_return"])
            dep = rm.depletion_age(rows)
            print(f"  {age:>10}{fm.assets_at(acc, age):>8.0f}{expenses:>10}"
                  f"{'none' if dep is None else dep:>11}{rm.years_sustained(rows):>7}")
    # TODO 4-1：リタイア後の収益率を下げる（例：2%）と、持続年数はどう変わるか。
    # TODO 4-2：FIRE 目標に「到達した年齢」でリタイアしても、100 歳まで持たないシナリオを探す（RQ5）。
    # TODO 4-3：資産が 100 歳まで持つための最低の資産額を、全探索（または単調性を確かめて二分探索）で求める。


def experiment5_sensitivity(scenarios, settings):
    """Experiment 5：感度分析 ―― 1 つの仮定を変えたとき、FIRE 達成年齢がどれだけ変わるか"""
    print("=== Experiment 5：感度分析（Standard を基準）===")
    base = scenarios[0]
    ref = op.evaluate_scenario(base, settings)["fire_age"]
    print(f"  基準の FIRE 達成年齢：{fmt_age(ref)}")
    changes = [
        ("savings_rate 0.2 → 0.3", dict(savings_rate=0.3, annual_expenses=280)),
        ("annual_return 3% → 4%", dict(annual_return=0.04)),
        ("annual_expenses 320 → 280（目標のみ）", dict(annual_expenses=280)),
        ("initial_assets 0 → 500", dict(initial_assets=500)),
    ]
    for label, ch in changes:
        r = op.evaluate_scenario(fm.with_changes(base, **ch), settings)
        print(f"  {label:38}: FIRE {fmt_age(r['fire_age'])}")
    for rate in [0.035, 0.04, 0.05]:
        r = op.evaluate_scenario(base, dict(settings, withdrawal_rate=rate))
        print(f"  {'withdrawal_rate ' + format(rate, '.1%'):38}: FIRE {fmt_age(r['fire_age'])}  "
              f"target {r['target']:.0f}  depletion {r['depletion_age']}")
    # TODO 5-1：変える幅をそろえる（例：すべて ±10%）か、現実的な幅を決めて、トルネード図にする（Notebook 04）。
    # TODO 5-2：リタイア年齢（FIRE 達成年齢ではなく自分で決めた年齢）を変えた場合の持続年数も調べる。
    # TODO 5-3：どの仮定に結果が最も敏感か、そしてその仮定の不確実性はどのくらいかを考察する。


EXPERIMENTS = {
    "1": experiment1_savings_rate,
    "2": experiment2_return,
    "3": experiment3_expenses,
    "4": experiment4_retirement,
    "5": experiment5_sensitivity,
}

if __name__ == "__main__":
    scenarios, settings = fm.load_scenarios()
    for key in sys.argv[1:] or list(EXPERIMENTS):
        if key not in EXPERIMENTS:
            raise SystemExit(f"Experiment {key} はありません（1〜5）")
        EXPERIMENTS[key](scenarios, settings)
        print()
    print("※ 架空のデータによる教育用の計算です。将来の投資収益の予測や、投資の推奨ではありません。")
