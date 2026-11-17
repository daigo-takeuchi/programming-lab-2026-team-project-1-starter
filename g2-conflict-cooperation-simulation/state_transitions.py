# G2：国家ペアの関係の状態遷移（確率モデル）
#
# 状態（抽象的なラベル。現実の軍事行動を表さない）：
#   0 Cooperation（協調） 1 Neutral（中立） 2 Tension（緊張） 3 Conflict（紛争状態）
#
#   P(次の状態 | 今の状態, 2 国の行動, 信頼度, 対話, 協定)
#
#   1. 2 国の行動の組（相互協調 / 一方だけ協調 / 相互非協調）で、基本の遷移行列を選ぶ（各行の合計 = 1）
#   2. 改善度 m = trust_effect × (信頼度 − 0.5) + dialogue_effect × 対話 + agreement_effect × 協定
#                 + spillover_effect × 隣の関係の状態（前年。協調なら +、緊張・紛争状態なら −。simulation.py が計算）
#      （−max_shift〜max_shift に制限）。m > 0 なら各状態の確率の m の割合を「1 段階良い状態」へ、
#      m < 0 なら |m| の割合を「1 段階悪い状態」へ移す（行の合計は 1 のまま）
#   3. 外部ショック：確率 external_shock_probability で、遷移後の状態が 1 段階悪くなる
#
# ■ 対照条件：dialogue_affects_transitions = False なら、対話は遷移確率に影響しない
#   （対話の効果をモデルに組み込んだことによる結果と、その他の要因による結果を区別するため）。
#
# 確率の値はすべて架空。これらはモデルの仮定であり、実証された因果関係ではない。

STATES = ("Cooperation", "Neutral", "Tension", "Conflict")
SEVERITY = {"Cooperation": 0.0, "Neutral": 1 / 3, "Tension": 2 / 3, "Conflict": 1.0}
OUTCOMES = ("mutual_cooperation", "mixed", "mutual_noncooperation")


def outcome_of(a1, a2):
    if a1 == "C" and a2 == "C":
        return "mutual_cooperation"
    if a1 == "N" and a2 == "N":
        return "mutual_noncooperation"
    return "mixed"


def validate_matrix(matrix, tol=1e-9):
    """4×4、各要素 0〜1、各行の合計 1 を確かめる"""
    if len(matrix) != len(STATES) or any(len(row) != len(STATES) for row in matrix):
        raise ValueError("遷移行列は 4×4 にしてください")
    for i, row in enumerate(matrix):
        if any(isinstance(p, bool) or not isinstance(p, (int, float)) or p < -tol or p > 1 + tol for p in row):
            raise ValueError(f"{STATES[i]} の行に 0〜1 でない確率があります：{row}")
        if abs(sum(row) - 1) > tol:
            raise ValueError(f"{STATES[i]} の行の合計が 1 ではありません（{sum(row)}）")
    return True


def validate_transition_params(tp):
    for o in OUTCOMES:
        validate_matrix(tp["base"][o])
    if not 0 <= tp["external_shock_probability"] <= 1:
        raise ValueError("external_shock_probability は 0〜1 にしてください")
    if tp["initial_state"] not in STATES:
        raise ValueError(f"initial_state は {STATES} のどれかにしてください")
    return True


def shift_row(row, m):
    """確率の m の割合を 1 段階良い状態（m > 0）または悪い状態（m < 0）へ移した新しい行"""
    out = list(row)
    if m > 0:
        for i in range(1, len(row)):           # Neutral → Cooperation, Tension → Neutral, Conflict → Tension
            moved = row[i] * m
            out[i] -= moved
            out[i - 1] += moved
    elif m < 0:
        for i in range(len(row) - 1):          # 1 段階悪い状態へ
            moved = row[i] * (-m)
            out[i] -= moved
            out[i + 1] += moved
    return out


def improvement(trust, dialogue, agreement, tp, extra=0.0):
    """改善度 m。extra = 隣の関係からの波及（simulation.neighbor_spillover × spillover_effect）"""
    m = tp["trust_effect"] * (trust - 0.5) + extra
    if dialogue and tp.get("dialogue_affects_transitions", True):
        m += tp["dialogue_effect"]
    if agreement:
        m += tp["agreement_effect"]
    lim = tp["max_shift"]
    return max(-lim, min(lim, m))


def transition_matrix(a1, a2, trust, dialogue, agreement, tp, extra=0.0):
    """行動・信頼度・対話・協定（・隣からの波及）を反映した遷移行列（外部ショックは含まない）"""
    m = improvement(trust, dialogue, agreement, tp, extra)
    return [shift_row(row, m) for row in tp["base"][outcome_of(a1, a2)]]


def sample(row, u):
    """一様乱数 u（0〜1）で次の状態の番号を選ぶ（累積確率を先頭から線形に調べる）"""
    acc = 0.0
    for i, p in enumerate(row):
        acc += p
        if u < acc:
            return i
    return len(row) - 1


def next_state(state, a1, a2, trust, dialogue, agreement, tp, rng, extra=0.0):
    """次の状態（乱数を毎回 2 つ使う：遷移用と外部ショック用。乱数列をそろえるため常に 2 つ）"""
    row = transition_matrix(a1, a2, trust, dialogue, agreement, tp, extra)[STATES.index(state)]
    i = sample(row, rng.random())
    shock = rng.random() < tp["external_shock_probability"]
    if shock:
        i = min(i + 1, len(STATES) - 1)
    return STATES[i], shock


def update_tension(tension, state, smoothing):
    """緊張度 = 状態の深刻度（0, 1/3, 2/3, 1）の指数移動平均"""
    return (1 - smoothing) * tension + smoothing * SEVERITY[state]


def stationary_distribution(matrix, iterations=500):
    """遷移行列をくり返し掛けて求める定常分布（同じ行動・条件が続いた場合の長期的な状態の割合）"""
    dist = [1 / len(STATES)] * len(STATES)
    for _ in range(iterations):
        dist = [sum(dist[i] * matrix[i][j] for i in range(len(STATES))) for j in range(len(STATES))]
    return dist


# TODO 1：遷移確率を変える（data/simulation_parameters.json の transition.base）。
# TODO 2：dialogue_effect を 0、または dialogue_affects_transitions を false にした対照条件と比べる。
# TODO 3：外部ショックの確率や大きさ（1 段階 → 2 段階）を変える（Advanced E）。
# TODO 4：spillover_effect を 0 にすると、各国家ペアは独立に変化する。ネットワーク構造の影響はどう変わるか。
