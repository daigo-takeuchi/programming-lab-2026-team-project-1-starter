# F3：学生向け研究実験の入口（Experiment A〜F）
#
# 各実験は「最小限の観察」だけを行う。条件を広げた実験・グラフ化・考察は学生が行う（各関数の TODO）。
# グラフは notebooks/ の Notebook で作る。
#
#   python3 experiments.py        すべての実験を実行
#   python3 experiments.py C      Experiment C だけ実行
#
# ■ 比較の公平性：参加者・希望順位・受け入れ可能性・関係継続モデルの係数・観測期間・試行回数をそろえる。
#   Random は複数のシードで、関係継続は複数の反復で平均し、単一のシードの結果から優劣を断定しない。
# すべて教育用の架空データ・架空モデル。

import statistics
import sys

import evaluation as ev
import matching_algorithms as ma
import participants as pt
import preferences as pr
import relationship_stability as rs

MATCHING_SEEDS = range(20)
REPLICATES = 200


def setup():
    groups = pt.load_participants()
    scores = pr.score_table(groups)
    rankings = pr.build_rankings(groups, scores)
    return groups, scores, rankings, rs.load_parameters()


def ids(groups):
    return [p["id"] for p in groups["A"]], [p["id"] for p in groups["B"]]


def experiment_a_matching_rate(groups, scores, rankings, params):
    """Experiment A：アルゴリズム別の成立率（RQ1）。希望条件の厳しさ（min_score）も変える（RQ2）"""
    print("=== Experiment A：アルゴリズム別の成立率・初期満足度 ===")
    a_ids, b_ids = ids(groups)
    n = pt.total_participants(groups)
    for extra in [0.0, 0.1, 0.2]:
        # 全員の min_score を extra だけ厳しくする（元のデータは変更しない）
        strict = {g: [dict(p, preferences=dict(p["preferences"], min_score=min(1, p["preferences"]["min_score"] + extra)))
                      for p in groups[g]] for g in pt.GROUPS}
        r = pr.build_rankings(strict, scores)
        text = []
        for name in ma.ALGORITHMS:
            seeds = MATCHING_SEEDS if name == "random" else [0]
            ms = [ma.run(name, r, a_ids, b_ids, seed=s) for s in seeds]
            rate = statistics.mean(ev.matching_rate(m, n) for m in ms)
            sat = statistics.mean(ev.satisfaction_summary(m, r, a_ids, b_ids)["mean_all"] for m in ms)
            text.append(f"{ma.LABELS[name]} {rate:.0%}/{sat:.2f}")
        acceptable = sum(len(v) for v in r.values())
        print(f"  min_score +{extra:.1f}（受け入れ可能な組 {acceptable}）: 成立率/満足度  " + ", ".join(text))
    # TODO A-1：候補者数を「上位 k 人まで」に制限して、成立率を比べる（preferences.py の TODO 4）。
    # TODO A-2：参加者を増やし（各 20 人など）、Random の成立率が他より低くなる条件を探す。
    # TODO A-3：Greedy の処理順序（ma.greedy_order(a_ids, seed)）を変えて、結果のばらつきを調べる。


def experiment_b_compatibility(groups, scores, rankings, params):
    """Experiment B：各アルゴリズムが作ったペアの初期適合度の分布（RQ3）"""
    print("=== Experiment B：成立ペアの初期適合度 ===")
    a_ids, b_ids = ids(groups)
    for name in ma.ALGORITHMS:
        seeds = MATCHING_SEEDS if name == "random" else [0]
        vals = [pr.pair_compatibility(a, b, scores) for s in seeds
                for a, b in ma.run(name, rankings, a_ids, b_ids, seed=s).items()]
        print(f"  {ma.LABELS[name]:13}: ペア {len(vals) / len(seeds):.1f} 組/回、適合度 平均 {statistics.mean(vals):.3f}、"
              f"最小 {min(vals):.3f}、最大 {max(vals):.3f}")
    # TODO B-1：分布をヒストグラムにする（Notebook 05）。
    # TODO B-2：成立率が高いアルゴリズムが、適合度の高いペアを作るとは限らない例を探す。


def experiment_c_continuation(groups, scores, rankings, params):
    """Experiment C：各アルゴリズムの成立ペアに同じ関係継続モデルを適用し、10 年継続率を比べる（RQ4）"""
    print("=== Experiment C：10 年継続率（同じモデル・同じ反復回数・共通乱数）===")
    res = ev.compare_algorithms(groups, rankings, scores, params, MATCHING_SEEDS, REPLICATES)
    for name, r in res.items():
        sd = f"（{len(MATCHING_SEEDS)} シード間の標準偏差 {r['continuation_10y_seed_sd']:.1%}）" if name == "random" else ""
        print(f"  {r['label']:13}: 10 年継続率 {r['continuation_10y']:.1%}{sd}")
    # TODO C-1：反復回数 REPLICATES を 50・200・1000 に変えて、結果がどれだけ安定するか調べる。
    # TODO C-2：初期適合度ごとの理論値 (1 − p)^10 と、シミュレーションの値を比べる。


def experiment_d_long_term(groups, scores, rankings, params):
    """Experiment D：成立率 × 継続率 ＝ 長期成立率で比べる（RQ5）"""
    print("=== Experiment D：成立率と 10 年長期成立率 ===")
    res = ev.compare_algorithms(groups, rankings, scores, params, MATCHING_SEEDS, REPLICATES)
    for r in res.values():
        print(f"  {r['label']:13}: 成立率 {r['matching_rate']:.0%} → 10 年長期成立率 {r['long_term_10y']:.1%}")
    # TODO D-1：成立率の順位と、10 年長期成立率の順位を並べて比べる（同じか？）。
    # TODO D-2：希望条件を厳しくした場合（Experiment A）でも同じことが言えるか調べる。


def experiment_e_sensitivity(groups, scores, rankings, params):
    """Experiment E：関係継続モデルの係数を変えたとき、10 年継続率の差がどう変わるか"""
    print("=== Experiment E：感度分析（Greedy と Gale-Shapley の 10 年継続率）===")
    changes = [("基準", {}), ("alpha × 2", {"alpha": params["alpha"] * 2}),
               ("baseline_hazard 0.12", {"baseline_hazard": 0.12}), ("gamma 0", {"gamma": 0.0}),
               ("beta × 2", {"beta": params["beta"] * 2})]
    for label, ch in changes:
        p = rs.with_changes(params, **ch)
        res = ev.compare_algorithms(groups, rankings, scores, p, [0], REPLICATES, algorithms=("greedy", "gale_shapley"))
        print(f"  {label:22}: " + "  ".join(f"{r['label']} {r['continuation_10y']:.1%}" for r in res.values()))
    for stress in [0.0, 0.3, 0.6, 1.0]:
        res = ev.compare_algorithms(groups, rankings, scores, params, [0], REPLICATES, algorithms=("gale_shapley",),
                                    annual_stress=stress)
        print(f"  年次ストレス {stress:<12}: Gale-Shapley {res['gale_shapley']['continuation_10y']:.1%}")
    # TODO E-1：各係数を系統的に変えて、表・グラフにする（Notebook 05）。
    # TODO E-2：アルゴリズム間の差が、どの係数に最も敏感か調べる。
    # TODO E-3：alpha を大きくしすぎたり baseline_hazard を小さくしすぎたりすると、式の値が負になり clip で 0 になる
    #           （継続率 100%）。どの範囲の係数なら clip されないか、式から求める。


def experiment_f_control(groups, scores, rankings, params):
    """Experiment F：初期適合度が解消確率に影響しない対照モデル（alpha = 0）と比べる"""
    print("=== Experiment F：対照条件（alpha = 0）との比較 ===")
    for label, p in [("通常のモデル", params), ("対照（alpha = 0）", rs.control_parameters(params))]:
        res = ev.compare_algorithms(groups, rankings, scores, p, MATCHING_SEEDS, REPLICATES)
        print(f"  {label:16}: " + "  ".join(f"{r['label']} {r['continuation_10y']:.1%}" for r in res.values()))
    # TODO F-1：対照条件で、アルゴリズム間の 10 年継続率の差がなくなるか（偶然のばらつき程度になるか）確かめる。
    # TODO F-2：「アルゴリズムの違い → 初期適合度の違い → 継続率の違い」という流れが、モデルの仮定（alpha > 0）
    #           によって作られていることを説明する。


EXPERIMENTS = {
    "A": experiment_a_matching_rate,
    "B": experiment_b_compatibility,
    "C": experiment_c_continuation,
    "D": experiment_d_long_term,
    "E": experiment_e_sensitivity,
    "F": experiment_f_control,
}

if __name__ == "__main__":
    data = setup()
    for key in [k.upper() for k in sys.argv[1:]] or list(EXPERIMENTS):
        if key not in EXPERIMENTS:
            raise SystemExit(f"Experiment {key} はありません（A〜F）")
        EXPERIMENTS[key](*data)
        print()
    print("※ 教育用の架空データ・架空モデルです。実際の結婚成立率・離婚率を予測するものではありません。")
