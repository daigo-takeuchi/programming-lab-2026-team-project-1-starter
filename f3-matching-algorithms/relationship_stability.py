# F3：長期的な関係継続モデル（教育用の架空モデル。Python 標準ライブラリのみ）
#
# ■ 実際の離婚確率・婚姻の継続を予測するモデルではない。係数（alpha・beta・gamma・baseline_hazard）は
#   すべて教育用の仮定で、現実のデータから推定した値でも、実証された因果効果でもない（README 10章・22章）。
#
# ■ 離散時間モデル（1 年 = 1 ステップ）
#   年次関係解消確率
#     p = clip(baseline_hazard − alpha × initial_compatibility − beta × conflict_resolution + gamma × annual_stress, 0, 1)
#   各年 t = 1, 2, ..., T について 0〜1 の一様乱数 u_t を引き、u_t < p ならその年に関係解消。
#   一度解消したペアは、再び継続状態には戻らない（再マッチングは Advanced D）。
#
# ■ 変数（すべて 0〜1）
#   initial_compatibility : 初期適合度（ペアの 2 方向の希望スコアの平均。preferences.pair_compatibility）
#   conflict_resolution   : 葛藤対処能力を表す架空の指標。Core では全ペア共通の値（パラメータ）。
#                           実在の人物について推定してはいけない
#   annual_stress         : 年次ストレス（架空。Core では毎年一定）
#   value_similarity・lifestyle_similarity : 記録はするが、Core の解消確率には**加えない**。
#                           すでに initial_compatibility の中に含まれているので、加えると二重に数えることになる
#
# ■ 乱数（共通乱数）
#   同じペア・同じ反復なら、どのアルゴリズムで成立したかによらず、同じ乱数の列を使う
#   （乱数の生成器を「シード・反復番号・ペアの 2 人の ID」から作る）。違うペアの乱数は独立。
#   これにより、アルゴリズム間の差が「どんなペアを作ったか」によるものか、乱数の偶然によるものかを区別しやすくなる。
#
# ■ 打ち切り（censoring）
#   観測期間（T 年）の終わりまで解消しなかったペアは「観測期間内に解消しなかった」（censored）として扱う。
#   その後いつ解消するかは推測しない。

import copy
import json
import os
import random

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "relationship_parameters.json")
CHECKPOINTS = (5, 10, 20)
PARAM_KEYS = ("baseline_hazard", "alpha", "beta", "gamma", "default_annual_stress", "default_conflict_resolution",
              "simulation_years", "random_seed")


def load_parameters(path=DATA_FILE):
    """関係継続モデルのパラメータを読み込む（教育用の架空の値）"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    params = {k: data[k] for k in PARAM_KEYS}
    validate_parameters(params)
    return params


def validate_parameters(params):
    for k in ("baseline_hazard", "default_annual_stress", "default_conflict_resolution"):
        if not 0 <= params[k] <= 1:
            raise ValueError(f"{k} は 0〜1 にしてください")
    for k in ("alpha", "beta", "gamma"):
        if params[k] < 0:
            raise ValueError(f"係数 {k} は 0 以上にしてください（向きは式の符号で決まっている）")
    if isinstance(params["simulation_years"], bool) or not isinstance(params["simulation_years"], int) \
            or params["simulation_years"] < 1:
        raise ValueError("simulation_years は 1 以上の整数にしてください")


def with_changes(params, **changes):
    """パラメータのコピーを作り、一部を変える（感度分析用。元は変更しない）"""
    p = copy.deepcopy(params)
    p.update(changes)
    validate_parameters(p)
    return p


def control_parameters(params):
    """対照条件（Experiment F）：初期適合度が解消確率に影響しないモデル（alpha = 0）"""
    return with_changes(params, alpha=0.0)


def clip(x, lo=0.0, hi=1.0):
    return max(lo, min(hi, x))


def annual_dissolution_probability(initial_compatibility, conflict_resolution, annual_stress, params):
    """年次関係解消確率（0〜1 に制限）"""
    for name, v in [("initial_compatibility", initial_compatibility), ("conflict_resolution", conflict_resolution),
                    ("annual_stress", annual_stress)]:
        if not 0 <= v <= 1:
            raise ValueError(f"{name} は 0〜1 にしてください：{v}")
    raw = (params["baseline_hazard"] - params["alpha"] * initial_compatibility
           - params["beta"] * conflict_resolution + params["gamma"] * annual_stress)
    return clip(raw)


def theoretical_survival(p, years):
    """解消確率が毎年一定 p のときの、years 年後の理論的な継続確率 (1 − p)^years"""
    return (1 - p) ** years


# ------------------------------------------------------------
# 1 組のシミュレーション
# ------------------------------------------------------------
def pair_rng(seed, replicate, a_id, b_id):
    """ペアごとの乱数生成器（同じシード・反復・ペアなら、どのアルゴリズムでも同じ乱数の列）"""
    return random.Random(f"{seed}|{replicate}|{a_id}|{b_id}")


def simulate_pair(p, years, rng):
    """解消確率 p で years 年シミュレーションする

    返り値：dissolved（観測期間内に解消したか）、dissolution_year（解消した年 1〜years、なければ None）、
            years_continued（観測期間内に継続した年数）、censored（観測期間の終わりまで継続＝打ち切り）
    """
    for t in range(1, years + 1):
        if rng.random() < p:
            return {"dissolved": True, "dissolution_year": t, "years_continued": t - 1, "censored": False}
    return {"dissolved": False, "dissolution_year": None, "years_continued": years, "censored": True}


def status_at(record, t):
    """t 年後に関係が継続しているか（True / False）。観測期間より後は分からないので None"""
    if t > record["observed_years"]:
        return None
    return record["dissolution_year"] is None or record["dissolution_year"] > t


# ------------------------------------------------------------
# 成立したペアのシミュレーション
# ------------------------------------------------------------
def make_pairs(matching, algorithm, compat, satisfaction=None):
    """マッチングの結果を、関係継続シミュレーションの入力（ペアのリスト）にする

    compat       : {(a, b): 初期適合度}（または関数 f(a, b)）
    satisfaction : {参加者 ID: 初期満足度}（evaluation.satisfaction_by_participant の結果。省略可）
    """
    pairs = []
    for a, b in sorted(matching.items()):
        c = compat(a, b) if callable(compat) else compat[(a, b)]
        s = None if satisfaction is None else (satisfaction[a] + satisfaction[b]) / 2
        pairs.append({"pair_id": f"{a}-{b}", "participant_ids": [a, b], "algorithm": algorithm,
                      "initial_compatibility": c, "initial_satisfaction": s})
    return pairs


def simulate_pairs(pairs, params, years=None, replicate=0, seed=None, annual_stress=None, conflict_resolution=None):
    """各ペアの関係継続をシミュレーションし、ペアごとの記録のリストを返す。O(P T)"""
    years = params["simulation_years"] if years is None else years
    seed = params["random_seed"] if seed is None else seed
    stress = params["default_annual_stress"] if annual_stress is None else annual_stress
    conflict = params["default_conflict_resolution"] if conflict_resolution is None else conflict_resolution
    records = []
    for pair in pairs:
        p = annual_dissolution_probability(pair["initial_compatibility"], conflict, stress, params)
        a, b = pair["participant_ids"]
        result = simulate_pair(p, years, pair_rng(seed, replicate, a, b))
        rec = dict(pair, annual_dissolution_probability=p, observed_years=years, replicate=replicate, **result)
        for t in CHECKPOINTS:
            rec[f"continuing_{t}y"] = status_at(rec, t)
        records.append(rec)
    return records


def monte_carlo(pairs, params, replicates, years=None, seed=None, **kw):
    """反復 replicates 回のシミュレーション（反復ごとの記録のリスト）。O(M P T)"""
    return [simulate_pairs(pairs, params, years, r, seed, **kw) for r in range(replicates)]


# ------------------------------------------------------------
# F4 への受け渡し（Advanced F）
# ------------------------------------------------------------
F4_FORMAT_VERSION = "f3-to-f4/1"


def export_pairs_for_f4(pairs, params):
    """F4「パートナー関係の安定性シミュレーション」に渡すデータ（辞書）。json.dump でそのまま保存できる"""
    return {
        "format": F4_FORMAT_VERSION,
        "note": "F3 の教育用の架空データ。実在の人物・実際の関係を表すものではない",
        "relationship_parameters": dict(params),
        "pairs": [{"pair_id": p["pair_id"], "participant_ids": list(p["participant_ids"]),
                   "initial_compatibility": p["initial_compatibility"],
                   "initial_satisfaction": p.get("initial_satisfaction"),
                   "matching_algorithm": p["algorithm"]} for p in pairs],
    }


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：alpha（初期適合度の影響係数）を変更する。
# TODO 2：baseline_hazard（基準解消確率）を変更する。
# TODO 3：annual_stress（年次ストレス）を変更する。年ごとに変わるストレスにする（Advanced B）。
# TODO 4：反復回数（replicates）を変えて、継続率のばらつきを調べる。
# TODO 5：解消確率をロジスティック関数で表すモデルにする（Advanced C）。
