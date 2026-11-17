# G1：時系列シミュレーション（1 年 = 1 ステップ）
#
#   for t = 1 .. T:
#       1. 年次投資額 = 予算 × 配分率（4 分野）
#       2. 投資効果 = 効率 × 投資額 ^ r（収穫逓減）→ 遅延キューに入れ、今年届く効果を取り出す
#       3. 状態変数を更新（減耗 + 届いた効果）
#       4. 人口を更新し、GDP・生活水準を計算する
#       5. 年次結果を記録する
#
# 乱数は使わない（Core では確率的なショックを入れない）。同じ入力なら必ず同じ結果になる。
# 計算量：T 年 × K 分野 → O(TK)

import economic_model as em

HORIZONS = (5, 10, 20, 30)


def validate_allocation(shares, tol=1e-9):
    """配分率の検証：4 分野がそろい、各 0〜1、合計 1（浮動小数点の誤差は tol まで許す）"""
    if set(shares) != set(em.SECTORS):
        raise ValueError(f"配分は {em.SECTORS} の 4 分野にしてください（{sorted(shares)}）")
    for s in em.SECTORS:
        v = shares[s]
        if isinstance(v, bool) or not isinstance(v, (int, float)) or not -tol <= v <= 1 + tol:
            raise ValueError(f"{s} の配分率は 0〜1 にしてください（{v!r}）")
    total = sum(shares.values())
    if abs(total - 1) > tol:
        raise ValueError(f"配分率の合計は 1 にしてください（合計 {total!r}）")
    return True


def annual_investments(shares, budget):
    """各分野の年次投資額（合計 = 予算）"""
    return {s: budget * shares[s] for s in em.SECTORS}


def simulate(shares, params, years=None, budget=None, check=True):
    """配分 shares で years 年シミュレーションし、年ごとの記録（0 年目 = 初期状態）のリストを返す

    shares：{"education": 0.25, "rd": 0.25, "infrastructure": 0.25, "healthcare": 0.25}
    budget：1 年あたりの投資予算（省略時は params の annual_investment_budget）。
            最適化の Greedy 法では、予算の一部だけを配分した途中の状態を評価するために使う。
    check ：False なら配分の検証（合計 1）をしない（Greedy 法の途中の評価用）。
    """
    years = int(params["simulation_years"] if years is None else years)
    budget = params["annual_investment_budget"] if budget is None else budget
    if check:
        validate_allocation(shares)
    if years < 0 or budget < 0:
        raise ValueError("years・budget は 0 以上にしてください")
    states = em.initial_states(params)
    lines = {sec: em.DelayLine(params[em.DELAY_KEY[sec]]) for sec in em.SECTORS}
    pop = em.population_at(params, 0)
    gdp = em.compute_gdp(states, pop, params)
    records = [_record(0, states, gdp, None, pop, params, shares, {s: 0.0 for s in em.SECTORS})]
    invest = annual_investments(shares, budget)
    for t in range(1, years + 1):
        new_states = {}
        for sec in em.SECTORS:
            st = em.STATE_OF_SECTOR[sec]
            effect = em.investment_effect(invest[sec], params[em.EFFICIENCY_KEY[sec]], params["returns_exponent"])
            arrived = lines[sec].push(effect)
            new_states[st] = em.update_state(states[st], params[em.DEPRECIATION_KEY[st]], arrived)
        states = new_states
        pop = em.population_at(params, t)
        prev_gdp = gdp
        gdp = em.compute_gdp(states, pop, params)
        growth = (gdp - prev_gdp) / prev_gdp if prev_gdp > 0 else None
        records.append(_record(t, states, gdp, growth, pop, params, shares, invest))
    return records


def _record(year, states, gdp, growth, pop, params, shares, invest):
    r = {"year": year, "gdp": gdp, "gdp_growth_rate": growth, "population": pop,
         "gdp_per_capita": em.gdp_per_capita(gdp, pop),
         "living_standard": em.living_standard(states, gdp, pop, params),
         "allocation": dict(shares), "investment": dict(invest), "total_investment": sum(invest.values())}
    r.update(states)
    r.update(em.indices(states, gdp, pop, params))
    return r


def series(records, key):
    """記録から 1 つの値の時系列を取り出す（例：series(recs, "gdp")）"""
    return [r[key] for r in records]


def run_scenarios(scenarios, params, years=None):
    """{シナリオ id: 記録} を返す。scenarios は data/investment_scenarios.json の形"""
    return {sc["id"]: simulate(sc["shares"], params, years) for sc in scenarios}


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：毎年の配分を変えられるようにする（例：最初の 10 年は教育重視、その後は研究開発重視）（Advanced E）。
# TODO 2：予算を GDP の一定割合にする（GDP が増えると投資も増える）。
# TODO 3：確率的な経済ショック（景気後退・災害）を入れる（Advanced D）。
