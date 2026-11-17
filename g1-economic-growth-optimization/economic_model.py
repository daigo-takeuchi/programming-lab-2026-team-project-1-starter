# G1：経済成長モデル（教育用の架空モデル）
#
# ■ 考え方（README 8〜11 章）
#   投資 → 状態変数（人的資本・技術・インフラ・健康）→ GDP・生活水準
#
#   1. 各分野への投資は、対応する状態変数を改善する（教育 → 人的資本、研究開発 → 技術、
#      インフラ → インフラ、医療 → 健康）。投資額そのものは GDP に足さない（二重計上しない）。
#   2. 投資効果 = 効率 × 投資額 ^ r（r = returns_exponent。r = 0.5 なら平方根 → 収穫逓減。r = 1 なら逓減なし）
#   3. 投資効果は delay 年後に状態変数に加わる（遅延。FixedQueue で管理する）
#   4. 状態変数は毎年、減耗する：X(t) = (1 − 減耗率) × X(t−1) + その年に届いた投資効果
#   5. GDP(t) = 初期 GDP × (人口(t) / 初期人口) × H^a × A^b × I^c × S^d（乗法的な生産関数）
#      状態変数はすべて「初期値 = 1 の指数」なので、初年度の GDP は初期 GDP に等しい。
#      GDP は非負（状態変数が非負なので）。log GDP の変化は Σ 弾力性 × Δlog(状態変数) に分解できる。
#   6. 生活水準 = w1 × 1 人あたり GDP 指数 + w2 × 健康指数 + w3 × 人的資本指数（重みの合計 1。初年度 = 1）
#
# ■ すべて教育用の架空の値・架空のモデルです。現実の国家の GDP や政策効果を予測しません。

import json
import math
from pathlib import Path

from textbook.fixed_queue import FixedQueue

DATA_DIR = Path(__file__).resolve().parent / "data"
ECONOMY_PATH = DATA_DIR / "baseline_economy.json"

SECTORS = ("education", "rd", "infrastructure", "healthcare")
SECTOR_LABELS = {"education": "Education", "rd": "R&D", "infrastructure": "Infrastructure", "healthcare": "Healthcare"}
STATES = ("human_capital", "technology", "infrastructure", "health")
STATE_OF_SECTOR = {"education": "human_capital", "rd": "technology", "infrastructure": "infrastructure",
                   "healthcare": "health"}
EFFICIENCY_KEY = {"education": "education_efficiency", "rd": "rd_efficiency",
                  "infrastructure": "infrastructure_efficiency", "healthcare": "healthcare_efficiency"}
DELAY_KEY = {"education": "education_delay", "rd": "rd_delay", "infrastructure": "infrastructure_delay",
             "healthcare": "healthcare_delay"}
DEPRECIATION_KEY = {s: f"{s}_depreciation" for s in STATES}
ELASTICITY_KEY = {s: f"gdp_elasticity_{s}" for s in STATES}
LS_WEIGHT_KEYS = ("living_standard_weight_gdp_per_capita", "living_standard_weight_health",
                  "living_standard_weight_human_capital")
REQUIRED = (("initial_gdp", "population", "population_growth", "annual_investment_budget", "returns_exponent",
             "simulation_years")
            + tuple(f"initial_{s}" for s in STATES) + tuple(EFFICIENCY_KEY.values()) + tuple(DELAY_KEY.values())
            + tuple(DEPRECIATION_KEY.values()) + tuple(ELASTICITY_KEY.values()) + LS_WEIGHT_KEYS)


# ------------------------------------------------------------
# パラメータ
# ------------------------------------------------------------
def load_economy(path=ECONOMY_PATH):
    with open(path, encoding="utf-8") as f:
        params = json.load(f)
    validate_params(params)
    return params


def validate_params(p):
    missing = [k for k in REQUIRED if k not in p]
    if missing:
        raise ValueError(f"パラメータがありません：{missing}")
    for k in ("initial_gdp", "population", "annual_investment_budget"):
        if p[k] < 0:
            raise ValueError(f"{k} は 0 以上にしてください（{p[k]!r}）")
    if p["population"] == 0:
        raise ValueError("population は正の値にしてください")
    for s in STATES:
        if p[f"initial_{s}"] <= 0:
            raise ValueError(f"initial_{s} は正の値にしてください")
        if not 0 <= p[DEPRECIATION_KEY[s]] <= 1:
            raise ValueError(f"{DEPRECIATION_KEY[s]} は 0〜1 にしてください")
        if p[ELASTICITY_KEY[s]] < 0:
            raise ValueError(f"{ELASTICITY_KEY[s]} は 0 以上にしてください")
    for sec in SECTORS:
        if p[EFFICIENCY_KEY[sec]] < 0:
            raise ValueError(f"{EFFICIENCY_KEY[sec]} は 0 以上にしてください")
        d = p[DELAY_KEY[sec]]
        if isinstance(d, bool) or not isinstance(d, int) or d < 0:
            raise ValueError(f"{DELAY_KEY[sec]} は 0 以上の整数にしてください（{d!r}）")
    if not 0 < p["returns_exponent"] <= 1:
        raise ValueError("returns_exponent は 0 より大きく 1 以下にしてください")
    if abs(sum(p[k] for k in LS_WEIGHT_KEYS) - 1) > 1e-9 or any(p[k] < 0 for k in LS_WEIGHT_KEYS):
        raise ValueError("生活水準の重みは 0 以上で、合計 1 にしてください")
    if int(p["simulation_years"]) < 1:
        raise ValueError("simulation_years は 1 以上にしてください")
    return True


def with_changes(params, **changes):
    """一部のパラメータだけを変えたコピー（感度分析用）。元の params は変えない"""
    p = dict(params)
    p.update(changes)
    validate_params(p)
    return p


# ------------------------------------------------------------
# 投資効果（収穫逓減）と遅延
# ------------------------------------------------------------
def investment_effect(investment, efficiency, exponent=0.5):
    """投資効果 = efficiency × investment ^ exponent（investment = 0 なら 0）"""
    if investment < 0:
        raise ValueError(f"投資額は 0 以上にしてください（{investment!r}）")
    if investment == 0:
        return 0.0
    return efficiency * investment ** exponent


def marginal_effect(investment, efficiency, exponent=0.5, unit=1.0):
    """投資を unit だけ増やしたときに増える効果（収穫逓減なら、投資額が大きいほど小さい）"""
    return investment_effect(investment + unit, efficiency, exponent) - investment_effect(investment, efficiency, exponent)


class DelayLine:
    """投資効果を delay 年遅らせて届ける（教科書の FixedQueue を使う）

    delay 個の 0 を先に入れておき、毎年「今年の効果を入れて、delay 年前の効果を取り出す」。
    delay = 0 ならキューを使わず、その年の効果をそのまま返す。
    """

    def __init__(self, delay):
        if isinstance(delay, bool) or not isinstance(delay, int) or delay < 0:
            raise ValueError(f"delay は 0 以上の整数にしてください（{delay!r}）")
        self.delay = delay
        self.queue = None
        if delay > 0:
            self.queue = FixedQueue(delay)
            for _ in range(delay):
                self.queue.enque(0.0)

    def push(self, effect):
        """今年の投資効果を入れ、今年届く効果を返す"""
        if self.queue is None:
            return effect
        arrived = self.queue.deque()
        self.queue.enque(effect)
        return arrived

    def pending(self):
        """まだ届いていない効果の合計"""
        if self.queue is None:
            return 0.0
        return sum(self.queue.que[(self.queue.front + i) % self.queue.capacity] for i in range(len(self.queue)))


# ------------------------------------------------------------
# 状態変数・GDP・生活水準
# ------------------------------------------------------------
def initial_states(params):
    return {s: float(params[f"initial_{s}"]) for s in STATES}


def update_state(value, depreciation, arrived_effect):
    """X(t) = (1 − 減耗率) × X(t−1) + その年に届いた投資効果（0 未満にはしない）"""
    return max(0.0, (1 - depreciation) * value + arrived_effect)


def population_at(params, year):
    return params["population"] * (1 + params["population_growth"]) ** year


def compute_gdp(states, population, params):
    """GDP = 初期 GDP × (人口 / 初期人口) × Π (状態 / 初期状態) ^ 弾力性（非負）"""
    g = params["initial_gdp"] * population / params["population"]
    for s in STATES:
        ratio = states[s] / params[f"initial_{s}"]
        g *= max(ratio, 0.0) ** params[ELASTICITY_KEY[s]]
    return max(g, 0.0)


def gdp_per_capita(gdp, population):
    return gdp / population if population > 0 else 0.0


def indices(states, gdp, population, params):
    """生活水準の材料になる指数（初年度 = 1）"""
    base_pc = params["initial_gdp"] / params["population"]
    return {"gdp_per_capita_index": gdp_per_capita(gdp, population) / base_pc if base_pc > 0 else 0.0,
            "health_index": states["health"] / params["initial_health"],
            "human_capital_index": states["human_capital"] / params["initial_human_capital"]}


def living_standard(states, gdp, population, params):
    """生活水準 = w1 × 1 人あたり GDP 指数 + w2 × 健康指数 + w3 × 人的資本指数（教育用の人工的な指標）"""
    ix = indices(states, gdp, population, params)
    return (params["living_standard_weight_gdp_per_capita"] * ix["gdp_per_capita_index"]
            + params["living_standard_weight_health"] * ix["health_index"]
            + params["living_standard_weight_human_capital"] * ix["human_capital_index"])


def gdp_decomposition(states_before, states_after, pop_before, pop_after, params):
    """GDP の変化（log の差）を、人口と各状態変数の寄与に分ける

    log GDP(t) − log GDP(t−1) = log(人口の比) + Σ 弾力性 × log(状態の比)。
    どの状態変数が GDP の変化を生んだかを説明するのに使う。
    """
    out = {"population": math.log(pop_after / pop_before)}
    for s in STATES:
        if states_before[s] <= 0 or states_after[s] <= 0:
            out[s] = None
        else:
            out[s] = params[ELASTICITY_KEY[s]] * math.log(states_after[s] / states_before[s])
    return out


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：投資効率（*_efficiency）を変えて、成長経路を比べる（Notebook 01）。
# TODO 2：減耗率（*_depreciation）を変える。減耗率が 0 だと状態変数はどうなるか。
# TODO 3：投資効果の遅延（education_delay・rd_delay）を変える（Experiment 5）。
# TODO 4：returns_exponent を 1（収穫逓減なし）にして、最適配分を比べる（Experiment 6）。
# TODO 5：投資効果を log(1 + 投資額) にするなど、別の収穫逓減の形を試す。
