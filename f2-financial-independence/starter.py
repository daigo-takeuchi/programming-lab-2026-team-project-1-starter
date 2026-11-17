# F2：資産形成と早期リタイア（FIRE）のシミュレーション ―― 一連のデモ
#
# 1. 架空のシナリオを読み込む
# 2. 年齢別資産を計算する
# 3〜4. FIRE 目標資産と FIRE 達成年齢を求める
# 5. 複数シナリオを比較する
# 6〜7. リタイア後の取り崩しを計算し、資産枯渇の有無を判定する
# 8. 貯蓄率の全探索を行う
# 9. 学生向け研究 TODO
#
# 金額は万円。すべて教育用の架空の数値で、将来の投資収益の予測や投資の推奨ではありません。

import financial_model as fm
import fire_analysis as fa
import optimization as op
import retirement_model as rm

scenarios, settings = fm.load_scenarios()
W = settings["withdrawal_rate"]
REPORT = settings["report_age"]
END = settings["retirement_end_age"]


def age_text(age, none="not reached"):
    return none if age is None else str(age)


print("F2: Financial Independence Simulation")
print("（架空のデータによる教育用シミュレーション。金額は万円、税・インフレ・手数料・年金は考慮しない）")
print(f"資産形成は {settings['accumulation_end_age']} 歳まで、リタイア後は {END} 歳まで計算。"
      f"FIRE 目標 = 年間生活費 / {W:.0%}")
print()

# ------------------------------------------------------------
print("=== 年齢別資産（Standard、抜粋）===")
std = scenarios[0]
acc = fm.accumulate(std, settings["accumulation_end_age"])
print(f"{'age':>5}{'start assets':>14}{'return':>9}{'savings':>9}{'end assets':>12}")
for r in acc:
    if r["age"] in (22, 23, 30, 40, 50, 60, 64):
        print(f"{r['age']:>5}{r['start_assets']:>14,.0f}{r['investment_return']:>9,.0f}"
              f"{r['savings']:>9,.0f}{r['end_assets']:>12,.0f}")
print()

# ------------------------------------------------------------
results = [op.evaluate_scenario(s, settings) for s in scenarios]
print(f"{'Scenario':14}{'Savings':>8}{'Return':>8}{'Expenses':>10}{'FIRE Target':>13}{'FIRE Age':>10}"
      f"{'Assets at ' + str(REPORT):>14}")
for r in results:
    print(f"{r['label']:14}{r['savings_rate']:>8.0%}{r['annual_return']:>8.0%}{r['annual_expenses']:>10,.0f}"
          f"{r['target']:>13,.0f}{age_text(r['fire_age']):>10}{r['assets_at_report']:>14,.0f}")
print()
print("FIRE 達成年齢の早い順：" + " > ".join(r["label"] for r in op.rank(results, "fire_age", minimize=True)))
print()

# ------------------------------------------------------------
print(f"Retirement Simulation（FIRE 達成年齢でリタイアし、同じ生活費・同じ収益率で {END} 歳まで取り崩す）:")
print(f"{'Scenario':14}{'Retirement Age':>16}{'Assets':>9}{'Depletion Age':>15}{'Years Covered':>15}")
for r in results:
    if r["fire_age"] is None:
        print(f"{r['label']:14}{'(FIRE not reached)':>16}")
        continue
    print(f"{r['label']:14}{r['fire_age']:>16}{r['retire_assets']:>9,.0f}"
          f"{age_text(r['depletion_age'], 'none'):>15}{r['years_sustained']:>15}")
print("→ FIRE 目標に到達しても、その後ずっと生活費を賄えるとは限らない（RQ5）。")
print()

# 1 つのシナリオの取り崩しの様子
hs = scenarios[1]
hs_acc = fm.accumulate(hs, settings["accumulation_end_age"])
age0 = fa.fire_age(hs_acc, fa.fire_target(hs["annual_expenses"], W))
ret = rm.simulate_withdrawal(age0, END, fm.assets_at(hs_acc, age0), hs["annual_expenses"], hs["annual_return"])
print(f"High Savings：{age0} 歳でリタイア（資産 {fm.assets_at(hs_acc, age0):,.0f}）→ 資産の推移（抜粋）")
for r in ret:
    if r["age"] in (age0, 60, 70, 80, 90) or r["depleted"] and r["age"] == rm.depletion_age(ret):
        print(f"  {r['age']:>3} 歳：年初 {r['start_assets']:>7,.0f}  収益 {r['investment_return']:>5,.0f}  "
              f"取り崩し {r['withdrawal']:>4,.0f}  年末 {r['end_assets']:>7,.0f}{'  ← 枯渇' if r['depleted'] else ''}")
print(f"Depletion Age: {age_text(rm.depletion_age(ret), 'none')}")
print()

# ------------------------------------------------------------
print("=== 貯蓄率の全探索（Standard、所得 400 万円を固定。生活費 = 所得 × (1 − 貯蓄率)）===")
rows = op.sweep_savings_rate(std, op.savings_rate_candidates(), settings, keep="income")
print(f"{'rate':>6}{'current expenses':>18}{'FIRE target':>13}{'FIRE age':>13}{'depletion':>11}")
for r in rows:
    print(f"{r['param']:>6.0%}{r['current_expenses']:>18,.0f}{r['target']:>13,.0f}"
          f"{age_text(r['fire_age']):>13}{age_text(r['depletion_age'], 'none' if r['fire_age'] else '-'):>11}")
b = op.best(rows, "fire_age", minimize=True)
print(f"FIRE 達成年齢が最小：貯蓄率 {b['param']:.0%}（{b['fire_age']} 歳）。ただし現役時の生活費は {b['current_expenses']:,.0f} 万円に減る。")
print("→ 候補の中で貯蓄率が最も高いものが選ばれるだけ。何を最適とするか（生活費の制約など）は研究で決める。")
print()

# ------------------------------------------------------------
print("Student Research TODOs:")
for todo in [
    "1. experiments.py の Experiment 1〜5 を実行し、各関数の TODO を実装する",
    "2. notebooks/ の Notebook 01〜04 でグラフを作り、05 で発表資料にまとめる",
    "3. 貯蓄率と収益率のどちらが FIRE 達成年齢に大きく影響するか、仮説を立てて調べる（RQ1・RQ2）",
    "4. 「所得を固定」と「生活費を固定」の実験を区別して、生活費の影響を調べる（RQ3）",
    "5. FIRE 目標に到達した後、資産が何歳まで持つかを調べ、FIRE の定義を考える（RQ4・RQ5）",
    "6. モデルの仮定と限界（README 19章）を考察する",
]:
    print(f"  {todo}")
