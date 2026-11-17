# G2：協調支援戦略の最適化（全探索と Greedy 法）
#
# 問題：予算 K 本のエッジ（国家ペア）にだけ協調支援（対話・協定・信頼形成・経済協力のどれか）を行える。
#       どのエッジを選ぶと、目的関数（例：緊張・紛争状態の少なさ）が最も良くなるか。
#
# ・目的関数の評価には、モンテカルロ・シミュレーション（runs 回 × years 年）を使う。
#   すべての候補を同じシード（共通乱数）で評価するので、評価は「選んだエッジの集合」だけで決まる（決定的）。
# ・全探索：C(E, K) 通りの組合せをすべて評価する → この探索空間・この評価方法の中で最適が保証される。
# ・Greedy 法：1 本ずつ、改善が最大のエッジを足す（K 回、各回で残りの候補を評価）→ 保証なし。
# ・両者は同じ候補集合・同じ予算・同じ評価関数を使う。
# ・これは仮想的な政策操作のモデルで、現実の外交政策の有効性を表すものではない。

import time

import simulation as sim
from textbook.max import max_of
from textbook.ssearch_while import seq_search

OBJECTIVES = ("stability", "cooperation", "low_conflict")
OBJECTIVE_LABELS = {"stability": "stability = 1 − tension rate − conflict rate",
                    "cooperation": "cooperation rate", "low_conflict": "1 − conflict rate"}


def objective_from_summary(summary, objective="stability"):
    if objective == "stability":
        return 1 - summary["tension_rate"] - summary["conflict_rate"]
    if objective == "cooperation":
        return summary["cooperation_rate"]
    if objective == "low_conflict":
        return 1 - summary["conflict_rate"]
    raise ValueError(f"目的関数 {objective!r} は {OBJECTIVES} のどれかにしてください")


class PolicyEvaluator:
    """支援するエッジの集合 → 目的関数の値（大きいほど良い）。評価回数を数える"""

    def __init__(self, countries, edges, params, payoff, policy=None, objective=None, runs=None, years=None,
                 seed=None):
        opt = params.get("optimization", {})
        self.countries, self.edges, self.params, self.payoff = countries, sorted(edges), params, payoff
        self.policy = policy or params["policy"]["type"]
        self.objective = objective or opt.get("objective", "stability")
        if self.objective not in OBJECTIVES:
            raise ValueError(f"目的関数 {self.objective!r} は {OBJECTIVES} のどれかにしてください")
        if self.policy not in sim.POLICY_TYPES:
            raise ValueError(f"政策 {self.policy!r} は {sim.POLICY_TYPES} のどれかにしてください")
        self.runs = runs or opt.get("runs", 30)
        self.years = years or opt.get("years", 30)
        self.seed = params["random_seed"] if seed is None else seed
        self.evaluations = 0

    def summary(self, selected):
        mc = sim.monte_carlo(self.countries, self.edges, self.params, self.payoff, self.runs, self.seed, self.years,
                             supported=tuple(sorted(selected)), policy=self.policy)
        return mc["summary"]

    def __call__(self, selected):
        bad = [e for e in selected if e not in self.edges]
        if bad:
            raise ValueError(f"候補にないエッジです：{bad}")
        self.evaluations += 1
        return objective_from_summary(self.summary(selected), self.objective)


def combinations(items, k):
    """items から k 個を選ぶ組合せをすべて列挙する（再帰）。並びは items の順（辞書順）"""
    if k == 0:
        return [()]
    if k > len(items):
        return []
    first, rest = items[0], items[1:]
    return [(first,) + c for c in combinations(rest, k - 1)] + combinations(rest, k)


def best_index(values):
    """最大値の位置（同点なら最初）。教科書の max_of と seq_search を使う"""
    return seq_search(values, max_of(values))


def check_budget(candidates, k):
    if isinstance(k, bool) or not isinstance(k, int) or k < 0:
        raise ValueError(f"予算 K は 0 以上の整数にしてください（{k!r}）")
    if k > len(candidates):
        raise ValueError(f"予算 K = {k} が候補のエッジ数 {len(candidates)} を超えています")


def exhaustive(evaluator, candidates, k):
    """全探索：C(E, K) 通りの組合せをすべて評価する"""
    check_budget(candidates, k)
    t0, e0 = time.perf_counter(), evaluator.evaluations
    combos = combinations(list(candidates), k)
    values = [evaluator(c) for c in combos]
    i = best_index(values)
    return {"algorithm": "Exhaustive Search", "selected": combos[i], "objective": values[i],
            "evaluations": evaluator.evaluations - e0, "runtime_s": time.perf_counter() - t0,
            "guarantee": "この候補集合・評価方法の中で最適", "all": list(zip(combos, values))}


def greedy(evaluator, candidates, k):
    """Greedy 法：1 本ずつ、足したときの目的関数が最大のエッジを選ぶ（同点は候補の順で最初）"""
    check_budget(candidates, k)
    t0, e0 = time.perf_counter(), evaluator.evaluations
    selected, remaining, path = [], list(candidates), []
    value = None
    for _ in range(k):
        values = [evaluator(tuple(selected + [e])) for e in remaining]
        i = best_index(values)
        selected.append(remaining.pop(i))
        value = values[i]
        path.append((tuple(selected), value))
    if k == 0:
        value = evaluator(())
    return {"algorithm": "Greedy", "selected": tuple(sorted(selected)), "objective": value,
            "evaluations": evaluator.evaluations - e0, "runtime_s": time.perf_counter() - t0,
            "guarantee": "保証なし（一度選んだエッジを戻さない）", "path": path}


def compare(countries, edges, params, payoff, k=None, **kw):
    """同じ候補集合・予算・評価関数で、支援なし・全探索・Greedy 法を比べる"""
    k = params["policy"]["budget"] if k is None else k
    ev = PolicyEvaluator(countries, edges, params, payoff, **kw)
    baseline = ev(())
    ex = exhaustive(ev, ev.edges, k)
    gr = greedy(ev, ev.edges, k)
    for r in (ex, gr):
        r["gap"] = ex["objective"] - r["objective"]
        r["improvement"] = r["objective"] - baseline
    return {"baseline": baseline, "exhaustive": ex, "greedy": gr, "evaluator": ev, "k": k}


# TODO 1：予算 K を 1・2・3 と変え、候補数 C(E, K) と実行時間の増え方を調べる（Notebook 05）。
# TODO 2：目的関数を cooperation・low_conflict に変える。
# TODO 3：政策の種類（dialogue・agreement・trust_building・economic_cooperation）を変える、組み合わせる。
# TODO 4：政策のコストや国家間の公平性も同時に評価する（Advanced F）。
