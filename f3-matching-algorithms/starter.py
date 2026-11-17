# F3：出会いとマッチングのアルゴリズム ―― 一連のデモ
#
#  1〜3. 参加者データの読み込み、希望スコア、希望順位
#  4〜7. 3 種類のマッチング、成立率、初期満足度、Blocking pair
#  8〜10. 成立ペアの関係継続シミュレーション、5・10・20 年継続率、長期成立率
#  11. アルゴリズム間の比較
#  12. 学生向け TODO
#
# すべて教育用の架空データ・架空モデルです。実際の結婚成立率・離婚率を予測するものではありません。

import evaluation as ev
import matching_algorithms as ma
import participants as pt
import preferences as pr
import relationship_stability as rs

MATCHING_SEEDS = range(20)   # Random Matching のシード（20 通りの平均）
REPLICATES = 200             # 関係継続シミュレーションの反復回数

groups = pt.load_participants()
scores = pr.score_table(groups)
rankings = pr.build_rankings(groups, scores)
params = rs.load_parameters()
a_ids = [p["id"] for p in groups["A"]]
b_ids = [p["id"] for p in groups["B"]]

print("F3: Matching and Relationship Continuation")
print("（教育用の架空データ・架空モデル。実際の結婚成立率・離婚率を予測するものではありません）")
print(f"参加者：Group A {len(a_ids)} 人、Group B {len(b_ids)} 人（A・B はアルゴリズム上の区分）")
print()

# ------------------------------------------------------------
print("=== 希望順位（受け入れ可能な相手だけ。かっこ内は希望スコア）===")
for pid, lst in rankings.items():
    text = ", ".join(f"{q}({scores[(pid, q)]:.2f})" for q in lst) or "（受け入れ可能な相手なし）"
    print(f"  {pid}: {text}")
print()

# ------------------------------------------------------------
print("=== マッチングの結果（Random はシード 0 の例）===")
for name in ma.ALGORITHMS:
    m = ma.run(name, rankings, a_ids, b_ids, seed=0)
    ma.validate_matching(m, rankings)
    bp = ev.blocking_pairs(m, rankings, a_ids, b_ids)
    pairs = ", ".join(f"{a}–{b}({pr.pair_compatibility(a, b, scores):.2f})" for a, b in sorted(m.items()))
    print(f"  {ma.LABELS[name]:13}: {pairs}")
    print(f"  {'':13}  Blocking pairs: {bp if bp else 'none（安定）'}")
print("  （かっこ内はペアの初期適合度）")
print()

m, steps = ma.gale_shapley(rankings, a_ids, b_ids, record=True)
print("=== Gale-Shapley の提案の記録 ===")
for s in steps:
    extra = f"（{s['rejected']} は拒否された）" if s["rejected"] else ""
    print(f"  step {s['step']}: {s['proposer']} → {s['receiver']}  {s['action']}{extra}")
print()

# ------------------------------------------------------------
print(f"=== 関係継続モデル（架空）：p = clip({params['baseline_hazard']} − {params['alpha']}×適合度 "
      f"− {params['beta']}×葛藤対処 + {params['gamma']}×ストレス, 0, 1) ===")
print(f"  葛藤対処 = {params['default_conflict_resolution']}（全ペア共通）、年次ストレス = {params['default_annual_stress']}、"
      f"観測 {params['simulation_years']} 年、反復 {REPLICATES} 回、seed = {params['random_seed']}")
for c in (0.5, 0.7, 0.9):
    p = rs.annual_dissolution_probability(c, params["default_conflict_resolution"], params["default_annual_stress"], params)
    print(f"  初期適合度 {c}: 年次解消確率 {p:.3f}、理論上の 10 年継続確率 {rs.theoretical_survival(p, 10):.3f}")
print()

# ------------------------------------------------------------
res = ev.compare_algorithms(groups, rankings, scores, params, MATCHING_SEEDS, REPLICATES)
print(f"{'Algorithm':14}{'Match Rate':>11}{'Satisfaction':>14}{'Blocking Pairs':>16}{'Compat.':>9}"
      f"{'5Y Cont.':>10}{'10Y Continuation':>18}{'20Y Cont.':>11}{'10Y Long-term Match':>21}")
for name, r in res.items():
    print(f"{r['label']:14}{r['matching_rate']:>11.0%}{r['satisfaction']:>14.2f}{r['blocking_pairs']:>16.2f}"
          f"{r['mean_compatibility']:>9.2f}{r['continuation_5y']:>10.1%}{r['continuation_10y']:>18.1%}"
          f"{r['continuation_20y']:>11.1%}{r['long_term_10y']:>21.1%}")
print(f"※ Random は {len(MATCHING_SEEDS)} 通りのシードの平均。継続率は {REPLICATES} 回の反復の平均（共通乱数）。")
print("※ Compat. = 成立ペアの初期適合度の平均。Blocking Pairs = 0 は数学的に安定という意味で、関係が長続きするという意味ではない。")
print()

ctrl = ev.compare_algorithms(groups, rankings, scores, rs.control_parameters(params), MATCHING_SEEDS, REPLICATES)
print("対照条件（alpha = 0：初期適合度が解消確率に影響しないモデル）の 10 年継続率：")
print("  " + "   ".join(f"{r['label']} {r['continuation_10y']:.1%}" for r in ctrl.values()))
print()

# ------------------------------------------------------------
print("Student Research TODOs:")
for todo in [
    "1. experiments.py の Experiment A〜F を実行し、各関数の TODO を実装する",
    "2. 希望条件（min_score・重み・候補者数）を厳しくして、成立率と初期満足度の変化を調べる（RQ2）",
    "3. 成立率・初期満足度が高いアルゴリズムが、10 年後の長期成立率も高いか検証する（RQ5）",
    "4. Blocking pair がないこと（数学的安定）と、関係が続くことを区別して説明する（RQ6）",
    "5. alpha・baseline_hazard・ストレスを変えて感度分析し、結論がモデルの仮定にどう依存するか調べる（RQ4）",
    "6. 複数のシード・反復回数で結果のばらつきを確かめ、単一シードの結果から優劣を断定しない",
    "7. notebooks/ の Notebook 01〜05 でグラフを作り、06 で研究発表にまとめる",
]:
    print(f"  {todo}")
