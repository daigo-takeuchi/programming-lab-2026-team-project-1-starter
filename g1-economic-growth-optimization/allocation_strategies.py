# G1：投資配分戦略
#
#   Strategy A  Equal Allocation      ：4 分野に 25% ずつ
#   Strategy B  Priority Allocation   ：特定の分野に多く配分する
#   Strategy C  Random Allocation     ：予算制約を満たす配分をランダムに作る（乱数シードを指定できる）
#   Strategy D  Greedy Allocation     ：予算を小さな単位に分け、目的関数が最も改善する分野に 1 単位ずつ足す
#   Strategy E  Exhaustive Search     ：一定刻みの配分をすべて列挙し、目的関数が最大のものを選ぶ
#   Strategy F  Local Search          ：初期配分から、隣の配分（1 単位を別の分野へ移す）のうち良いものへ移る
#
# D〜F のアルゴリズム本体は optimization.py にある。ここでは「配分（分野 → 配分率）」として返す。
#
# ■ 配分の表し方
#   配分率 shares：{"education": 0.3, "rd": 0.3, "infrastructure": 0.2, "healthcare": 0.2}（合計 1）
#   整数単位 units：(3, 3, 2, 2)（予算を M = 1 / 刻み 個の単位に分けたときの各分野の単位数。合計 M）
#   最適化では浮動小数点の誤差を避けるため、整数単位で列挙・更新し、最後に配分率に直す。

import json
import random

import economic_model as em
from simulation import validate_allocation

SCENARIO_PATH = em.DATA_DIR / "investment_scenarios.json"
K = len(em.SECTORS)


# ------------------------------------------------------------
# 整数単位と配分率の変換
# ------------------------------------------------------------
def units_count(step):
    """刻み step から、予算を分ける単位数 M を求める（例：0.1 → 10）。1 を割り切らない刻みは ValueError"""
    if isinstance(step, bool) or not isinstance(step, (int, float)) or step <= 0 or step > 1:
        raise ValueError(f"刻みは 0 より大きく 1 以下にしてください（{step!r}）")
    m = round(1 / step)
    if abs(m * step - 1) > 1e-9:
        raise ValueError(f"刻み {step} は 1 を割り切りません（0.05・0.1・0.2・0.25 など）")
    return m


def shares_from_units(units, m):
    """整数単位 → 配分率（合計 = sum(units) / m）"""
    if len(units) != K or any(isinstance(u, bool) or not isinstance(u, int) or u < 0 for u in units):
        raise ValueError(f"units は 0 以上の整数 {K} 個にしてください（{units!r}）")
    return {s: u / m for s, u in zip(em.SECTORS, units)}


def units_from_shares(shares, m):
    """配分率 → 整数単位（刻みに乗らない配分は、最大剰余法で最も近い格子点に丸める）"""
    validate_allocation(shares)
    exact = [shares[s] * m for s in em.SECTORS]
    units = [int(e + 1e-9) for e in exact]
    rest = m - sum(units)
    # 余りの大きい順（同じなら分野の順）に 1 単位ずつ足す → 決定的
    order = sorted(range(K), key=lambda i: (-(exact[i] - units[i]), i))
    for i in order[:rest]:
        units[i] += 1
    return tuple(units)


def format_shares(shares):
    return " / ".join(f"{em.SECTOR_LABELS[s][:4]} {shares[s]:.0%}" for s in em.SECTORS)


# ------------------------------------------------------------
# シナリオの読み込み
# ------------------------------------------------------------
def load_scenarios(path=SCENARIO_PATH):
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    for sc in data["scenarios"]:
        validate_allocation(sc["shares"])
    return data["scenarios"]


# ------------------------------------------------------------
# Strategy A〜C
# ------------------------------------------------------------
def equal_allocation():
    """Strategy A：均等配分"""
    return {s: 1 / K for s in em.SECTORS}


def priority_allocation(sector, share=0.55):
    """Strategy B：sector に share、残りを他の 3 分野に均等に配分する"""
    if sector not in em.SECTORS:
        raise ValueError(f"分野 {sector!r} は {em.SECTORS} のどれかにしてください")
    if not 0 <= share <= 1:
        raise ValueError(f"share は 0〜1 にしてください（{share!r}）")
    rest = (1 - share) / (K - 1)
    return {s: (share if s == sector else rest) for s in em.SECTORS}


def random_allocation(seed=0, step=None):
    """Strategy C：予算制約（合計 1、各 0〜1）を満たすランダムな配分

    step を指定すると、その刻みの格子点（整数単位）から一様に選ぶ。指定しなければ連続値
    （0〜1 の乱数で区間を 4 つに切る方法。配分の単体上で一様）。
    """
    rng = random.Random(seed)
    if step is not None:
        m = units_count(step)
        cuts = sorted(rng.sample(range(m + K - 1), K - 1))      # 「仕切り」の位置を選ぶ（重複組合せ）
        units, prev = [], -1
        for c in cuts + [m + K - 1]:
            units.append(c - prev - 1)
            prev = c
        return shares_from_units(tuple(units), m)
    cuts = sorted(rng.random() for _ in range(K - 1))
    edges = [0.0] + cuts + [1.0]
    shares = {s: edges[i + 1] - edges[i] for i, s in enumerate(em.SECTORS)}
    shares[em.SECTORS[-1]] = 1 - sum(shares[s] for s in em.SECTORS[:-1])   # 誤差を最後の分野で調整
    return shares


# ------------------------------------------------------------
# Strategy D〜F（optimization.py のアルゴリズムを使う）
# ------------------------------------------------------------
def greedy_allocation(params, objective="final_gdp", step=0.1, years=None, **kw):
    """Strategy D：Greedy 法で求めた配分（optimization.greedy の結果の shares）"""
    import optimization as op
    return op.greedy(op.Evaluator(params, objective, years, **kw), units_count(step))["shares"]


def exhaustive_allocation(params, objective="final_gdp", step=0.1, years=None, **kw):
    """Strategy E：全探索で求めた配分"""
    import optimization as op
    return op.exhaustive(op.Evaluator(params, objective, years, **kw), units_count(step))["shares"]


def local_search_allocation(params, objective="final_gdp", step=0.1, years=None, start=None, **kw):
    """Strategy F：局所探索で求めた配分（start は初期配分の配分率。省略時は均等配分に最も近い格子点）"""
    import optimization as op
    m = units_count(step)
    start_units = units_from_shares(start or equal_allocation(), m)
    return op.local_search(op.Evaluator(params, objective, years, **kw), m, start_units)["shares"]


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：新しい配分シナリオを data/investment_scenarios.json に追加する（合計 1）。
# TODO 2：2 分野を重視する配分（例：教育 40%・医療 40%）を作る関数を書く。
# TODO 3：ランダム配分を 1,000 個作り、最良の配分と全探索の結果を比べる（ランダム探索）。
