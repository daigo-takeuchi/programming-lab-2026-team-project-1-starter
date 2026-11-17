# G2：ゲーム理論（2×2 の利得行列・4 つの戦略・繰り返しゲーム・Nash 均衡）
#
# 行動：C = Cooperate（協調）、N = Non-cooperate（非協調）
# 利得行列は教育用の架空の値（data/payoff_matrix.json。囚人のジレンマ型）。現実の国家行動を表さない。
#
# ■ 一回限りのゲームと繰り返しゲームを区別する
#   ・一回限りのゲーム：nash_equilibria で純粋戦略の Nash 均衡を全探索する（4 通りの行動の組をすべて調べる）。
#     囚人のジレンマ型の利得では、(N, N) が唯一の Nash 均衡になる。
#   ・繰り返しゲーム：play_repeated で同じ相手と何回も対戦する。Tit-for-Tat などで協調が続くことがある。
#   ・「Nash 均衡であること」と「長期的に協調が維持されること」は同じ意味ではない。

import json
import random

import trust_model as tm
from agents import DATA_DIR, STRATEGIES, STRATEGY_LABELS
from textbook.insertion_sort import insertion_sort

PAYOFF_PATH = DATA_DIR / "payoff_matrix.json"
ACTIONS = ("C", "N")


# ------------------------------------------------------------
# 利得行列
# ------------------------------------------------------------
def load_payoff_matrix(path=PAYOFF_PATH):
    with open(path, encoding="utf-8") as f:
        m = json.load(f)["payoffs"]
    validate_payoff_matrix(m)
    return m


def validate_payoff_matrix(m):
    for a in ACTIONS:
        for b in ACTIONS:
            v = m.get(a, {}).get(b)
            if isinstance(v, bool) or not isinstance(v, (int, float)):
                raise ValueError(f"利得行列の ({a}, {b}) が数値ではありません：{v!r}")
    return True


def payoffs(m, a1, a2):
    """(国家 1 の利得, 国家 2 の利得)。m[自分の行動][相手の行動] = 自分の利得"""
    if a1 not in ACTIONS or a2 not in ACTIONS:
        raise ValueError(f"行動は C か N にしてください（{a1!r}, {a2!r}）")
    return m[a1][a2], m[a2][a1]


def is_prisoners_dilemma(m):
    """T > R > P > S（T = m[N][C], R = m[C][C], P = m[N][N], S = m[C][N]）"""
    return m["N"]["C"] > m["C"]["C"] > m["N"]["N"] > m["C"]["N"]


def best_responses(m, opponent_action):
    """相手の行動に対する最適反応（利得が最大の自分の行動。複数あればすべて）"""
    best = max(m[a][opponent_action] for a in ACTIONS)
    return [a for a in ACTIONS if m[a][opponent_action] == best]


def nash_equilibria(m):
    """一回限りのゲームの純粋戦略 Nash 均衡（4 通りの組を全探索）"""
    return [(a1, a2) for a1 in ACTIONS for a2 in ACTIONS
            if a1 in best_responses(m, a2) and a2 in best_responses(m, a1)]


# ------------------------------------------------------------
# 戦略
# ------------------------------------------------------------
def conditional_probability(me, trust, opponent_history, coef, interdependence_bonus=0.0):
    """Conditional Cooperation の協調確率

    p = clip(w_pref × 協調傾向 + w_trust × 信頼度 + w_hist × 相手の最近の協調率
             + w_inter × 経済的相互依存 + offset, 最小確率, 最大確率)
    最大確率が 1 未満なので、信頼度が高くても必ず協調するとは限らない。
    """
    window = opponent_history[-coef["history_window"]:]
    recent = sum(1 for a in window if a == "C") / len(window) if window else 0.5
    inter = min(1.0, me["economic_interdependence"] + interdependence_bonus)
    p = (coef["w_preference"] * me["cooperation_preference"] + coef["w_trust"] * trust
         + coef["w_opponent_history"] * recent + coef["w_interdependence"] * inter + coef["offset"])
    return tm.clip(p, coef["min_probability"], coef["max_probability"])


def choose_action(strategy, me, my_history, opponent_history, trust, rng, params, interdependence_bonus=0.0):
    """戦略に従って行動を選ぶ。行動の誤り（action_noise の確率で反対の行動になる）を含む

    always_cooperate    ：常に C
    always_noncooperate ：常に N
    tit_for_tat         ：初回は C、以後は相手の前回の行動をまねる
    conditional         ：信頼度・協調傾向・相手の最近の協調率などで決まる確率で C
    乱数は「行動の誤り」用に毎回 1 つ、conditional ではさらに 1 つ使う。
    """
    if strategy == "always_cooperate":
        action = "C"
    elif strategy == "always_noncooperate":
        action = "N"
    elif strategy == "tit_for_tat":
        action = "C" if not opponent_history else opponent_history[-1]
    elif strategy == "conditional":
        p = conditional_probability(me, trust, opponent_history, params["conditional"], interdependence_bonus)
        action = "C" if rng.random() < p else "N"
    else:
        raise ValueError(f"戦略 {strategy!r} は {STRATEGIES} のどれかにしてください")
    if rng.random() < params.get("action_noise", 0.0):
        action = "N" if action == "C" else "C"
    return action


# ------------------------------------------------------------
# 繰り返しゲーム（2 国）
# ------------------------------------------------------------
def play_repeated(c1, c2, rounds, m, params, seed=0, dialogue=False, agreement=False, trust=None):
    """2 国が rounds 回くり返して対戦する（状態遷移なし。ゲームと信頼度だけ）

    戻り値：{"actions": [(a1, a2), ...], "payoffs": [(p1, p2), ...], "trust": [各回の後の信頼度],
             "cumulative": (累積利得 1, 累積利得 2), 各種の率}
    """
    rng = random.Random(seed)
    trust = (c1["trust"] + c2["trust"]) / 2 if trust is None else trust
    h1, h2, acts, pays, trusts = [], [], [], [], []
    for _ in range(rounds):
        a1 = choose_action(c1["strategy"], c1, h1, h2, trust, rng, params)
        a2 = choose_action(c2["strategy"], c2, h2, h1, trust, rng, params)
        p = payoffs(m, a1, a2)
        trust = tm.update_trust(trust, a1, a2, params["trust"], dialogue, agreement)
        h1.append(a1)
        h2.append(a2)
        acts.append((a1, a2))
        pays.append(p)
        trusts.append(trust)
    return summarize_game(acts, pays, trusts)


def summarize_game(acts, pays, trusts=()):
    n = len(acts)
    c1 = sum(p[0] for p in pays)
    c2 = sum(p[1] for p in pays)
    return {"actions": acts, "payoffs": pays, "trust": list(trusts), "rounds": n, "cumulative": (c1, c2),
            "average_payoff": ((c1 + c2) / (2 * n)) if n else 0.0,
            "average_payoff_1": c1 / n if n else 0.0, "average_payoff_2": c2 / n if n else 0.0,
            "cooperation_rate": sum((a == "C") + (b == "C") for a, b in acts) / (2 * n) if n else 0.0,
            "cooperation_rate_1": sum(a == "C" for a, _ in acts) / n if n else 0.0,
            "mutual_cooperation_rate": sum(a == "C" and b == "C" for a, b in acts) / n if n else 0.0,
            "noncooperation_rate": sum((a == "N") + (b == "N") for a, b in acts) / (2 * n) if n else 0.0}


def tournament(countries, rounds, m, params, seed=0, opponent=None):
    """戦略ごとに、同じ相手・同じ初期条件で繰り返しゲームをする

    countries：[(戦略名, 国家)]。opponent を指定すれば全員がその相手と対戦する（同じ相手）、
    指定しなければ総当たり（自分と同じ戦略の相手を含む）で平均する。
    戻り値：{戦略名: {"average_payoff", "cooperation_rate", ...}}
    """
    out = {}
    for name, c in countries:
        rivals = [opponent] if opponent is not None else [d for _n, d in countries]
        games = [play_repeated(c, r, rounds, m, params, seed) for r in rivals]
        k = len(games)
        out[name] = {"average_payoff": sum(g["average_payoff_1"] for g in games) / k,
                     "cumulative_payoff": sum(g["cumulative"][0] for g in games) / k,
                     "cooperation_rate": sum(g["cooperation_rate_1"] for g in games) / k,
                     "mutual_cooperation_rate": sum(g["mutual_cooperation_rate"] for g in games) / k,
                     "noncooperation_rate": 1 - sum(g["cooperation_rate_1"] for g in games) / k,
                     "first_round_payoff": sum(g["payoffs"][0][0] for g in games) / k if rounds else 0.0}
    return out


def rank(values, higher_is_better=True):
    """{名前: 値} を順位順の [(名前, 値)] にする（同点は名前順）。教科書の insertion_sort を使う"""
    keyed = [((-v if higher_is_better else v), name) for name, v in values.items()]
    insertion_sort(keyed)
    return [(name, values[name]) for _k, name in keyed]


def label(strategy):
    return STRATEGY_LABELS.get(strategy, strategy)


# TODO 1：利得行列を変える（例：協調の利得 R を 4 にする）と、協調率はどう変わるか（Notebook 01）。
# TODO 2：新しい戦略（例：Generous Tit-for-Tat、Grim Trigger）を追加する（Advanced A）。
# TODO 3：混合戦略の Nash 均衡を求める。
