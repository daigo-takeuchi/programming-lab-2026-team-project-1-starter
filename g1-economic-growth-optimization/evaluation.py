# G1：評価指標
#
# ・GDP と生活水準を区別して評価する（GDP が大きい配分が、生活水準も高いとは限らない）。
# ・比率（成長率・投資効率）は、分母が 0 のときは None を返す（ゼロ除算をしない）。
# ・最適化ギャップは、同じ離散探索空間・同じ目的関数での全探索の最良値との差。

import time


# ------------------------------------------------------------
# 14.1 GDP 成長率
# ------------------------------------------------------------
def growth_rate(initial, final):
    """期間全体の成長率 (final − initial) / initial。initial ≤ 0 なら None"""
    if initial is None or final is None or initial <= 0:
        return None
    return (final - initial) / initial


def annual_growth_rate(initial, final, years):
    """年平均成長率 (final / initial)^(1 / years) − 1。years ≤ 0・initial ≤ 0・final < 0 なら None"""
    if years is None or years <= 0 or initial is None or initial <= 0 or final is None or final < 0:
        return None
    return (final / initial) ** (1 / years) - 1


def gdp_growth(records):
    """records（simulation.simulate の結果）の、期間全体の成長率と年平均成長率"""
    first, last = records[0], records[-1]
    years = last["year"] - first["year"]
    return {"total": growth_rate(first["gdp"], last["gdp"]),
            "annual": annual_growth_rate(first["gdp"], last["gdp"], years)}


# ------------------------------------------------------------
# 14.2〜14.4 累積 GDP・生活水準
# ------------------------------------------------------------
def cumulative_gdp(records):
    """1〜T 年の GDP の合計（0 年目 = 初期状態は含めない）"""
    return sum(r["gdp"] for r in records[1:])


def final_living_standard(records):
    return records[-1]["living_standard"]


def average_living_standard(records):
    """1〜T 年の生活水準の平均（シミュレーションが 0 年なら初期値）"""
    years = records[1:]
    if not years:
        return records[0]["living_standard"]
    return sum(r["living_standard"] for r in years) / len(years)


# ------------------------------------------------------------
# 14.5 投資効率
# ------------------------------------------------------------
def investment_efficiency(records, key="gdp"):
    """（最終年の値 − 初期値）÷ 期間中の総投資額。総投資額が 0 なら None

    注意：単純な比率なので、遅延（まだ効果が届いていない投資）や減耗・人口増加の影響も含まれる。
    「投資 1 単位あたりの効果」と単純に解釈しないこと。
    """
    total = sum(r["total_investment"] for r in records[1:])
    if total <= 0:
        return None
    return (records[-1][key] - records[0][key]) / total


# ------------------------------------------------------------
# 14.6 最適化ギャップ
# ------------------------------------------------------------
def optimization_gap(best, value):
    """全探索の最良値 best との差。absolute = best − value（0 以上なら全探索以下）、relative = absolute / |best|"""
    absolute = best - value
    relative = absolute / abs(best) if best != 0 else None
    return {"absolute": absolute, "relative": relative}


# ------------------------------------------------------------
# 14.7 計算コスト
# ------------------------------------------------------------
def measure_time(func, *args, **kwargs):
    """func を 1 回実行して (結果, 経過秒) を返す（time.perf_counter）"""
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    return result, time.perf_counter() - t0


def computational_cost(result):
    """最適化の結果から、実行時間・評価回数・反復回数を取り出す"""
    return {"runtime_s": result["runtime_s"], "evaluations": result["evaluations"],
            "iterations": result["iterations"]}


# ------------------------------------------------------------
# まとめ
# ------------------------------------------------------------
def summarize_run(records):
    """1 つのシミュレーション結果の主な指標"""
    g = gdp_growth(records)
    last = records[-1]
    return {"final_gdp": last["gdp"], "gdp_growth_total": g["total"], "gdp_growth_annual": g["annual"],
            "cumulative_gdp": cumulative_gdp(records), "final_gdp_per_capita": last["gdp_per_capita"],
            "final_living_standard": final_living_standard(records),
            "average_living_standard": average_living_standard(records),
            "final_health": last["health"], "final_human_capital": last["human_capital"],
            "final_technology": last["technology"], "final_infrastructure": last["infrastructure"],
            "gdp_per_investment": investment_efficiency(records, "gdp"),
            "living_standard_per_investment": investment_efficiency(records, "living_standard")}


def format_table(rows, columns):
    """文字の表。rows = [辞書]、columns = [(キー, 見出し, 書式)]。値が None なら "-" """
    cells = [[("-" if r.get(k) is None else f.format(r[k])) for k, _h, f in columns] for r in rows]
    heads = [h for _k, h, _f in columns]
    widths = [max([len(h)] + [len(c[i]) for c in cells]) for i, h in enumerate(heads)]
    lines = ["  ".join(h.ljust(w) if i == 0 else h.rjust(w) for i, (h, w) in enumerate(zip(heads, widths)))]
    for c in cells:
        lines.append("  ".join(v.ljust(w) if i == 0 else v.rjust(w) for i, (v, w) in enumerate(zip(c, widths))))
    return "\n".join(lines)


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：生活水準の「最も低い年」や「下がった年の数」など、別の評価指標を作る。
# TODO 2：投資効率を「遅延で届いていない投資」を除いて計算し直すと、どう変わるか。
# TODO 3：複数の指標（GDP・生活水準・健康・人的資本）で、他の配分に負けない配分（Pareto 最適）を探す（Advanced F）。
