# G2：国家ペアの信頼度の更新（0〜1）
#
#   Trust(t+1) = clip( Trust(t) + 行動の効果 + 対話の効果 + 協定の効果, 0, 1 )
#
#   行動の効果（自分から見た信頼度ではなく、ペアで 1 つの値）：
#     相互協調               +mutual_cooperation
#     一方的な非協調          exploited（裏切られた側の不信）と exploiter の平均
#     相互非協調             +mutual_noncooperation（負の値）
#
# 係数はすべて教育用の架空の値（data/simulation_parameters.json の "trust"）。
# 信頼度が高くても必ず協調するわけではない（Conditional Cooperation の協調確率には上限があり、行動には誤りもある）。


def clip(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def action_effect(a1, a2, coef):
    """2 国の行動 (a1, a2) による信頼度の変化（"C" = 協調、"N" = 非協調）"""
    if a1 == "C" and a2 == "C":
        return coef["mutual_cooperation"]
    if a1 == "N" and a2 == "N":
        return coef["mutual_noncooperation"]
    return (coef["exploited"] + coef["exploiter"]) / 2      # 一方的な非協調


def update_trust(trust, a1, a2, coef, dialogue=False, agreement=False):
    """1 年分の信頼度の更新"""
    delta = action_effect(a1, a2, coef)
    if dialogue:
        delta += coef["dialogue"]
    if agreement:
        delta += coef["agreement"]
    return clip(trust + delta)


# TODO 1：一方的な非協調で、裏切った側と裏切られた側の信頼度を別々に持つ（非対称な信頼）。
# TODO 2：信頼の回復は遅く、低下は速い（非対称な更新速度）モデルにする。
