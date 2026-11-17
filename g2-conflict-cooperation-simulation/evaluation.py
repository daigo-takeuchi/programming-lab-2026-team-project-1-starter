# G2：評価指標
#
# 年ごとの記録（simulation.simulate の records）から、協調率・緊張率・紛争状態率・継続期間などを計算する。
# 割合の分母が 0（記録やエッジがない）のときは None を返す。

import statistics
import time

import network_model as nm


def _mean(values):
    values = [v for v in values if v is not None]
    return statistics.mean(values) if values else None


# ------------------------------------------------------------
# 18.1〜18.5 行動と状態の割合（1〜T 年の平均）
# ------------------------------------------------------------
def cooperation_rate(records):
    """協調が選ばれた割合（全エッジ・全年の行動のうち C の割合）"""
    acts = [x for r in records[1:] for pair in r["actions"].values() for x in pair]
    return sum(a == "C" for a in acts) / len(acts) if acts else None


def mutual_cooperation_rate(records):
    pairs = [pair for r in records[1:] for pair in r["actions"].values()]
    return sum(a == "C" and b == "C" for a, b in pairs) / len(pairs) if pairs else None


def average_payoff(result):
    """国家あたり・1 年あたりの平均利得"""
    pay = result["payoff"]
    years = result["years"]
    return sum(pay.values()) / (len(pay) * years) if pay and years else None


def state_rate(records, state):
    """関係状態が state である国家ペアの割合（1〜T 年の平均）"""
    vals = [sum(s == state for s in r["states"].values()) / len(r["states"]) for r in records[1:] if r["states"]]
    return sum(vals) / len(vals) if vals else None


def tension_rate(records):
    return state_rate(records, "Tension")


def conflict_rate(records):
    return state_rate(records, "Conflict")


# ------------------------------------------------------------
# 18.6 継続期間
# ------------------------------------------------------------
def run_lengths(sequence, target):
    """sequence の中で target が連続した長さのリスト（例：[C, C, N, C] で C → [2, 1]）"""
    out, n = [], 0
    for x in sequence:
        if x == target:
            n += 1
        elif n:
            out.append(n)
            n = 0
    if n:
        out.append(n)
    return out


def state_durations(records, state):
    """各エッジで state が連続した期間（年）のリスト（1〜T 年。観測期間の終わりで打ち切られた期間も含む）"""
    edges = list(records[0]["states"])
    out = []
    for e in edges:
        out.extend(run_lengths([r["states"][e] for r in records[1:]], state))
    return out


def mean_duration(records, state):
    d = state_durations(records, state)
    return sum(d) / len(d) if d else None


# ------------------------------------------------------------
# 18.7 ネットワークの連結性
# ------------------------------------------------------------
def network_connectivity(nodes, edges, states):
    """最終年などの状態 states から、協調ネットワーク（Cooperation のエッジだけ）の連結性を計算する"""
    return nm.network_metrics(nodes, edges, states)


# ------------------------------------------------------------
# 18.8 政策の効果、18.9 計算コスト
# ------------------------------------------------------------
def policy_improvement(before, after, keys=("cooperation_rate", "tension_rate", "conflict_rate", "stability")):
    """支援前後の差（after − before）。tension・conflict は減るほど良いことに注意"""
    return {k: (after[k] - before[k]) if before.get(k) is not None and after.get(k) is not None else None
            for k in keys}


def measure_time(func, *args, **kwargs):
    """(結果, 経過秒)。time.perf_counter で 1 回測る"""
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    return result, time.perf_counter() - t0


# ------------------------------------------------------------
# 1 回のシミュレーションの要約
# ------------------------------------------------------------
def summarize_run(result):
    recs = result["records"]
    t = tension_rate(recs)
    c = conflict_rate(recs)
    return {"cooperation_rate": cooperation_rate(recs), "mutual_cooperation_rate": mutual_cooperation_rate(recs),
            "average_payoff": average_payoff(result), "tension_rate": t, "conflict_rate": c,
            "cooperation_state_rate": state_rate(recs, "Cooperation"),
            "stability": None if t is None or c is None else 1 - t - c,
            "cooperation_duration": mean_duration(recs, "Cooperation"),
            "tension_duration": mean_duration(recs, "Tension"),
            "ever_conflict": (any(s == "Conflict" for r in recs[1:] for s in r["states"].values())
                              if recs[0]["states"] else None),
            "final_mean_trust": recs[-1]["mean_trust"]}


def format_table(rows, columns):
    """文字の表。rows = [辞書]、columns = [(キー, 見出し, 書式)]。値が None なら "-" """
    cells = [[("-" if r.get(k) is None else f.format(r[k])) for k, _h, f in columns] for r in rows]
    heads = [h for _k, h, _f in columns]
    widths = [max([len(h)] + [len(x[i]) for x in cells]) for i, h in enumerate(heads)]
    lines = ["  ".join(h.ljust(w) if i == 0 else h.rjust(w) for i, (h, w) in enumerate(zip(heads, widths)))]
    for x in cells:
        lines.append("  ".join(v.ljust(w) if i == 0 else v.rjust(w) for i, (v, w) in enumerate(zip(x, widths))))
    return "\n".join(lines)


# TODO：国家ごとの利得の差（公平性）を評価する指標を作る（Advanced F）。
