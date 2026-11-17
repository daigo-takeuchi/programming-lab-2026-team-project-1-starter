# F4：2 人の分担を決める意思決定戦略
#
#   Strategy A  fixed     ：最初の分担をずっと続ける
#   Strategy B  greedy    ：その年の平均満足度が最大になる分担を、候補から全探索で選ぶ
#   Strategy C  fairness  ：平均満足度 − λ × 満足度の差 が最大になる分担を選ぶ（公平性を考慮した交渉）
#   Strategy D  adaptive  ：一定期間ごと（と、ストレスイベントの年）に見直し、満足度が下がっていたら
#                           今の分担の「近く」だけを調べて少しずつ再調整する
#
# ・すべての戦略で、同じ候補集合（candidate_grid）、同じ制約（household_model.is_feasible）、
#   同じ満足度関数（household_model.utilities）を使う。違うのは「選び方」だけ。
# ・同点のときは候補の並び順（x が小さい順 → y が小さい順）で最初のものを選ぶので、結果は決定的。
# ・最大値探索に教科書の max_of（第2章）、その位置の探索に seq_search（第3章）、
#   戦略の順位付けに insertion_sort（第6章）を使う。

import household_model as hm
from textbook.max import max_of
from textbook.ssearch_while import seq_search
from textbook.insertion_sort import insertion_sort

STRATEGIES = ("fixed", "greedy", "fairness", "adaptive")
LABELS = {"fixed": "Fixed", "greedy": "Greedy", "fairness": "Fairness-aware", "adaptive": "Adaptive"}


# ------------------------------------------------------------
# 候補集合
# ------------------------------------------------------------
def share_grid(step=0.1):
    """[0.0, 0.1, ..., 1.0]（step 刻み。浮動小数点の誤差を避けるため整数から作る）"""
    n = round(1 / step)
    if n <= 0 or abs(n * step - 1) > 1e-9:
        raise ValueError(f"step は 1 を割り切る正の値にしてください（{step!r}）")
    return [round(i / n, 10) for i in range(n + 1)]


def candidate_grid(step=0.1, housework_shares=None, financial_shares=None):
    """(x, y) の候補のリスト。家事 K 通り × 生活費 L 通り = K × L 個"""
    xs = share_grid(step) if housework_shares is None else list(housework_shares)
    ys = share_grid(step) if financial_shares is None else list(financial_shares)
    return [(x, y) for x in xs for y in ys]


def feasible_candidates(candidates, partners, conditions):
    """実行可能な候補だけを残す（全戦略で同じ制約）"""
    return [(x, y) for x, y in candidates if hm.is_feasible(x, y, partners, conditions)]


def choice_set(candidates, partners, conditions, params):
    """戦略が選んでよい候補（全戦略で同じ）

    ・ふつうは実行可能な候補だけ。
    ・実行可能な候補が 1 つもないとき（例：家事が増えて 2 人の家事に使える時間の合計を超えた）：
      infeasible_fallback = True なら全候補から選ぶ（超過分は満足度の減点になるので「最も無理の少ない」分担になる）。
      False なら空のリスト（戦略は None を返し、シミュレーションでは前年の分担を続ける）。
    """
    feasible = feasible_candidates(candidates, partners, conditions)
    if feasible or not params.get("infeasible_fallback", True):
        return feasible
    return list(candidates)


# ------------------------------------------------------------
# 目的関数と探索
# ------------------------------------------------------------
def objective(ua, ub, kind="mean", lam=1.0):
    """候補を比べる値。mean：平均満足度、fairness：平均 − λ × |差|、min：最低満足度"""
    if kind == "mean":
        return (ua + ub) / 2
    if kind == "fairness":
        return (ua + ub) / 2 - lam * abs(ua - ub)
    if kind == "min":
        return min(ua, ub)
    raise ValueError(f"目的関数 {kind!r} がありません")


def evaluate(candidates, partners, conditions, params, kind="mean", lam=1.0):
    """各候補の目的関数の値のリスト（O(候補数)）"""
    values = []
    for x, y in candidates:
        ua, ub = hm.utilities(x, y, partners, conditions, params)
        values.append(objective(ua, ub, kind, lam))
    return values


def best_candidate(candidates, partners, conditions, params, kind="mean", lam=1.0):
    """目的関数が最大の候補（全探索）。候補がなければ None

    最大値を max_of（教科書）で求め、その値が最初に現れる位置を seq_search（教科書）で探す。
    """
    if not candidates:
        return None
    values = evaluate(candidates, partners, conditions, params, kind, lam)
    best = max_of(values)
    return candidates[seq_search(values, best)]


# ------------------------------------------------------------
# 4 つの戦略（いずれも (x, y) を返す。選べる候補がなければ None）
# ------------------------------------------------------------
def fixed_allocation(current):
    """Strategy A：分担を変えない（実行不可能でも変えない。超過分は満足度の減点になる）"""
    return current


def greedy_allocation(partners, conditions, params, candidates):
    """Strategy B：その年の平均満足度を最大にする（choice_set の候補から）"""
    return best_candidate(choice_set(candidates, partners, conditions, params), partners, conditions,
                          params, "mean")


def fairness_allocation(partners, conditions, params, candidates, lam=None):
    """Strategy C：平均満足度 − λ × 満足度の差 を最大にする。λ = 0.5 なら最低満足度の最大化と同じ"""
    lam = params["fairness_lambda"] if lam is None else lam
    return best_candidate(choice_set(candidates, partners, conditions, params), partners, conditions,
                          params, "fairness", lam)


def neighbors(current, candidates, step):
    """今の分担から x・y をそれぞれ最大 1 目盛りだけ動かした候補（今の分担も含む）"""
    cx, cy = current
    return [(x, y) for x, y in candidates if abs(x - cx) <= step + 1e-9 and abs(y - cy) <= step + 1e-9]


def adaptive_allocation(current, partners, conditions, params, candidates, review):
    """Strategy D：見直しの年（review=True）だけ、近くの候補から公平性つき目的関数が最大のものに移る

    見直しの年でなければ今の分担を続ける。近くに選べる候補がなければ、choice_set 全体から選ぶ。
    """
    if not review:
        return current
    allowed = choice_set(candidates, partners, conditions, params)
    if not allowed:
        return None
    near = neighbors(current, allowed, params["share_step"])
    return best_candidate(near or allowed, partners, conditions, params, "fairness", params["fairness_lambda"])


def needs_review(year, history, params, event_year=False):
    """Adaptive の見直しをする年か

    ・ストレスイベントが起きた年
    ・review_interval 年ごとの見直しの年で、関係満足度が前回の見直しより下がった、または
      review_threshold を下回っているとき
    """
    if event_year:
        return True
    interval = params["review_interval"]
    if interval <= 0 or year % interval != 0 or not history:
        return False
    now = history[-1]["relationship_satisfaction"]
    before = history[max(0, len(history) - 1 - interval)]["relationship_satisfaction"]   # interval 年前
    return now < before or now < params["review_threshold"]


def decide(strategy, current, partners, conditions, params, candidates, review=False):
    """戦略の名前で振り分ける（どの戦略も同じ引数を受け取る）"""
    if strategy == "fixed":
        return fixed_allocation(current)
    if strategy == "greedy":
        return greedy_allocation(partners, conditions, params, candidates)
    if strategy == "fairness":
        return fairness_allocation(partners, conditions, params, candidates)
    if strategy == "adaptive":
        return adaptive_allocation(current, partners, conditions, params, candidates, review)
    raise ValueError(f"戦略 {strategy!r} がありません（{STRATEGIES}）")


# ------------------------------------------------------------
# 戦略の順位付け（ソート）
# ------------------------------------------------------------
def rank_strategies(values, higher_is_better=True):
    """{戦略: 値} を順位順の [(戦略, 値)] にする。同点は名前順。insertion_sort（教科書・安定）を使う"""
    keyed = [((-v if higher_is_better else v), name) for name, v in values.items() if v is not None]
    insertion_sort(keyed)
    return [(name, values[name]) for _k, name in keyed]


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：share_step を 0.05 にして候補を増やし、結果と計算時間がどう変わるか調べる（O(KL)）。
# TODO 2：fairness_lambda を 0、0.5、1、2 と変えて、選ばれる分担を比べる（Notebook 03）。
# TODO 3：目的関数に「最低満足度」（objective の kind="min"）を使う戦略を追加する。
# TODO 4：Adaptive の見直し間隔（review_interval）としきい値（review_threshold）を変える。
# TODO 5：2 人が別々の目的を持ち、交渉で決めるモデル（ナッシュ交渉解など）にする（Advanced F）。
