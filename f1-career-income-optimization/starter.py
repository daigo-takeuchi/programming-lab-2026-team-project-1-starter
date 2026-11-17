# F1：キャリア選択と生涯所得の最適化 ―― 一連のデモ
#
# 1. 架空のキャリアデータを読み込む
# 2. 各キャリアの年齢別所得を計算する
# 3〜5. 生涯所得・累積純収入・NPV を計算する
# 6. 複数キャリアを比較・順位付けする
# 7〜8. 転職年齢を全探索し、評価基準ごとの最適な転職年齢を表示する
# 9. 学生向け研究 TODO
#
# 金額の単位は万円。すべて教育用の架空の数値で、実際の賃金統計ではありません。

import career_model as cm
import income_analysis as ia
import optimization as op
import scenarios as sc

careers, settings = sc.load_scenarios()
rate = settings.get("discount_rate", ia.DEFAULT_DISCOUNT_RATE)

print("F1: Career Income Optimization")
print("（架空のデータによる教育用シミュレーション。金額は万円、税・社会保険料は考慮しない額面）")
print(f"計算期間：{cm.BASE_AGE}〜{cm.RETIREMENT_AGE - 1} 歳（退職年齢 {cm.RETIREMENT_AGE} 歳の年からは計算しない）")
print()

# ------------------------------------------------------------
print("=== 年齢別所得（抜粋）===")
show_ages = [18, 20, 22, 25, 30, 35, 40, 50, 64]
print(f"{'Scenario':16}" + "".join(f"{a:>7}" for a in show_ages))
for s in careers:
    inc = sc.incomes(s)
    print(f"{s['label']:16}" + "".join(f"{inc[cm.index_of_age(a)]:7.0f}" for a in show_ages))
print()

# ------------------------------------------------------------
results = [ia.evaluate(s, rate) for s in careers]
print(f"{'Scenario':16}{'Lifetime Income':>17}{'Costs':>8}{'Net Income':>12}{'NPV (r=' + format(rate, '.0%') + ')':>13}")
for r in results:
    print(f"{r['label']:16}{r['gross']:>17,.0f}{r['costs']:>8,.0f}{r['net']:>12,.0f}{r['npv']:>13,.0f}")
print("Net Income = 生涯所得 − キャリア関連費用（進学・資格・転職）。手取りではありません。")
print()

print("=== 順位（大きい順）===")
for key, title in op.CRITERIA.items():
    print(f"{title:22}: " + " > ".join(r["label"] for r in op.rank(results, key)))
print()

# ------------------------------------------------------------
print("=== 投資回収年齢（累積純収入が比較対象に追いつく年齢）===")
pairs = [
    ("university", careers[0], "Early Job"),
    ("vocational", careers[0], "Early Job"),
]
named = {s["name"]: s for s in careers}


def payback_text(p):
    if p["status"] == "recovered":
        return f"{p['payback_age']} 歳（{p['behind_from']} 歳から比較対象を下回り、{p['payback_age']} 歳で追いつく）"
    if p["status"] == "not_recovered":
        return f"退職までに回収できない（退職時の差 {p['final_gap']:,.0f} 万円）"
    return "一度も比較対象を下回らない（回収すべき差がない）"


for name, baseline, base_label in pairs:
    print(f"{named[name]['label']:16} vs {base_label:22}: {payback_text(ia.payback_age(named[name], baseline))}")
for name, key, base_label in [("certificate", "certificate", "same career w/o cert"),
                              ("job_change", "job_change", "same career w/o change")]:
    baseline = sc.with_changes(named[name], **{key: None})
    print(f"{named[name]['label']:16} vs {base_label:22}: {payback_text(ia.payback_age(named[name], baseline))}")
print()

# ------------------------------------------------------------
jc = named["job_change"]
first, last = settings.get("switch_age_range", [22, 60])
candidates = op.switch_age_candidates(jc, first, last)
rows = op.evaluate_switch_ages(jc, candidates, rate)
best = op.optimal_switch_ages(rows)
print(f"=== 転職年齢の全探索：{first}〜{last} 歳の {len(candidates)} 通り × {cm.RETIREMENT_AGE - cm.BASE_AGE} 年（O(KT)）===")
print("Optimal Job Change Age:")
for key, label in [("gross", "Gross Income"), ("net", "Net Income"), ("npv", f"NPV (r={rate:.0%})")]:
    print(f"  {label:14}: {best[key]['switch_age']} 歳（{best[key]['value']:,.0f} 万円）")
print("  同じ最大値が複数ある場合は、最も若い転職年齢を選ぶ規則。")
print("  ※ 転職後の初年度年収を年齢によらず一定（420 万円）と仮定しているため、早く転職するほど有利になる。")
print("    この仮定を変えると結果が変わる（experiments.py の Experiment 3）。")
for a in [25, 35, 45, 55, 60]:
    r = next(x for x in rows if x["switch_age"] == a)
    print(f"  switch at {a}: gross {r['gross']:,.0f}  NPV {r['npv']:,.0f}")
print()

# ------------------------------------------------------------
print("Student Research TODOs:")
for todo in [
    "1. experiments.py の Experiment 1〜5 を実行し、各関数の TODO を実装する",
    "2. 進学費用・初年度年収・昇給率を変えて、進学の投資回収年齢を調べる（RQ1）",
    "3. 資格取得の年齢・費用・年収増加を変えて、回収できる条件を探す（RQ2）",
    "4. 転職後の年収が経験によって変わるモデルにして、最適な転職年齢を再計算する（RQ3）",
    "5. 割引率を 0〜5% で変えて、生涯所得と NPV の順位の違いを説明する（RQ4）",
    "6. モデルの仮定と限界（README 17章）を、自分たちの結果に即して考察する",
]:
    print(f"  {todo}")
