# F4：家事・経済的負担のモデルと、満足度（効用）の計算
#
# ・x = Partner A の家事分担率、y = Partner A の生活費の負担率（B はそれぞれ 1 − x、1 − y）。
# ・x と y は別々に決める。「所得の多い側が家事を少なくする」ことを自動的に正当化しない。
# ・満足度の式と係数は教育用の架空のもの。実際の夫婦関係の満足度を予測しない。
# ・ここにある計算は 1 回あたり O(1)（2 人分の四則演算だけ）。

WEEK_HOURS = 168


def clip(v, lo=0.0, hi=1.0):
    return lo if v < lo else hi if v > hi else v


def _ratio(a, b, default=0.5):
    """a / (a + b)。両方 0 なら default"""
    return default if a + b == 0 else a / (a + b)


# ------------------------------------------------------------
# 8.1・8.2 家事時間と生活費の分担
# ------------------------------------------------------------
def housework_hours(x, total):
    """(Partner A の家事時間, Partner B の家事時間)  ［時間/週］"""
    if not 0 <= x <= 1:
        raise ValueError(f"家事分担率は 0〜1 にしてください（{x!r}）")
    return x * total, (1 - x) * total


def financial_amounts(y, expenses):
    """(Partner A の生活費負担, Partner B の生活費負担)  ［万円/年］"""
    if not 0 <= y <= 1:
        raise ValueError(f"生活費の負担率は 0〜1 にしてください（{y!r}）")
    return y * expenses, (1 - y) * expenses


# ------------------------------------------------------------
# 8.3 分担ルール（いずれも Partner A の分担率を返す）
# ------------------------------------------------------------
def equal_share(partners=None):
    """50:50"""
    return 0.5


def income_share(partners):
    """所得比例：A の負担率 = A の所得 / 2 人の所得（生活費の負担に使う）"""
    return _ratio(partners["A"]["annual_income"], partners["B"]["annual_income"])


def work_hours_housework_share(partners):
    """労働時間に応じた家事分担：労働時間の長い人ほど家事を少なく（A の家事分担率 = B の労働時間 / 合計）"""
    return _ratio(partners["B"]["weekly_work_hours"], partners["A"]["weekly_work_hours"])


def income_housework_share(partners):
    """所得に応じた家事分担：所得の多い人ほど家事を少なく（A の家事分担率 = B の所得 / 合計）

    比較のために用意したルール。「所得が多いから家事をしなくてよい」ことを正当化するものではない。
    """
    return _ratio(partners["B"]["annual_income"], partners["A"]["annual_income"])


def preference_housework_share(partners):
    """希望に基づく家事分担：A の希望と「B の希望から決まる A の分担」の中間"""
    return (partners["A"]["preferred_housework_share"] + 1 - partners["B"]["preferred_housework_share"]) / 2


def preference_financial_share(partners):
    """希望に基づく生活費の負担：A の希望と「B の希望から決まる A の負担」の中間"""
    return (partners["A"]["preferred_financial_share"] + 1 - partners["B"]["preferred_financial_share"]) / 2


def equal_workload_housework_share(partners, total):
    """有償労働 + 家事の合計時間が 2 人で等しくなる家事分担率（公平性の基準の 1 つ。0〜1 に収める）"""
    if total == 0:
        return 0.5
    wa, wb = partners["A"]["weekly_work_hours"], partners["B"]["weekly_work_hours"]
    return clip((wb - wa + total) / (2 * total))


HOUSEWORK_RULE_FUNCS = {
    "equal": equal_share,
    "work_hours": work_hours_housework_share,
    "income": income_housework_share,
    "preference": preference_housework_share,
}
FINANCIAL_RULE_FUNCS = {
    "equal": equal_share,
    "income": income_share,
    "preference": preference_financial_share,
}


def apply_rule(rule, partners, kind):
    """分担ルール（名前、または 0〜1 の数値）から A の分担率を求める。kind = "housework" / "financial" """
    if isinstance(rule, (int, float)) and not isinstance(rule, bool):
        return float(rule)
    funcs = HOUSEWORK_RULE_FUNCS if kind == "housework" else FINANCIAL_RULE_FUNCS
    return funcs[rule](partners)


def initial_allocation(scenario):
    """シナリオの分担ルールから、最初の (x, y) を求める"""
    return (apply_rule(scenario["housework_rule"], scenario["partners"], "housework"),
            apply_rule(scenario["financial_rule"], scenario["partners"], "financial"))


# ------------------------------------------------------------
# 実行可能性
# ------------------------------------------------------------
def overloads(x, y, partners, household):
    """各パートナーの「超過分」：家事時間が家事に使える時間を超えた分、生活費が所得を超えた分"""
    ha, hb = housework_hours(x, household["total_housework_hours"])
    fa, fb = financial_amounts(y, household["annual_expenses"])
    out = {}
    for pid, h, f in (("A", ha, fa), ("B", hb, fb)):
        p = partners[pid]
        out[pid] = {"housework_hours": max(0.0, h - p["available_housework_hours"]),
                    "financial": max(0.0, f - p["annual_income"])}
    return out


def is_feasible(x, y, partners, household, tol=1e-9):
    """どちらも家事に使える時間・所得の範囲内なら True"""
    ov = overloads(x, y, partners, household)
    return all(v <= tol for pid in ov for v in ov[pid].values())


def feasibility_report(x, y, partners, household):
    """実行可能性の説明（文字列のリスト）。空なら実行可能"""
    msgs = []
    ov = overloads(x, y, partners, household)
    for pid in ("A", "B"):
        if ov[pid]["housework_hours"] > 1e-9:
            msgs.append(f"Partner {pid}: 家事が {ov[pid]['housework_hours']:.1f} 時間/週 超過")
        if ov[pid]["financial"] > 1e-9:
            msgs.append(f"Partner {pid}: 生活費が所得を {ov[pid]['financial']:.0f} 万円/年 超過")
    return msgs


# ------------------------------------------------------------
# 9 満足度（効用）
# ------------------------------------------------------------
UTILITY_KEYS = ("housework_mismatch", "financial_mismatch", "free_time", "communication",
                "stress", "overload", "unfairness", "financial_strain")


def utility_components(pid, x, y, partners, household, params):
    """Partner pid の満足度を決める要素（それぞれ 0〜1）"""
    p, q = partners[pid], partners["B" if pid == "A" else "A"]
    my_x = x if pid == "A" else 1 - x
    my_y = y if pid == "A" else 1 - y
    total = household["total_housework_hours"]
    my_h, their_h = my_x * total, (1 - my_x) * total
    my_f = my_y * household["annual_expenses"]
    free = max(0.0, params["discretionary_hours"] - p["weekly_work_hours"] - my_h)
    over_h = max(0.0, my_h - p["available_housework_hours"])
    over_f = max(0.0, my_f - p["annual_income"])
    if p["annual_income"] > 0:
        burden_ratio = my_f / p["annual_income"]
    else:
        burden_ratio = 1.0 if my_f > 0 else 0.0
    my_load = p["weekly_work_hours"] + my_h
    their_load = q["weekly_work_hours"] + their_h
    return {
        "housework_mismatch": abs(my_x - p["preferred_housework_share"]),
        "financial_mismatch": abs(my_y - p["preferred_financial_share"]),
        "free_time": clip(free / params["discretionary_hours"]),
        "communication": (p["communication_score"] + q["communication_score"]) / 2,
        "stress": clip(household.get("stress", 0.0)),
        "overload": clip(over_h / params["overload_scale_hours"]
                         + (over_f / household["annual_expenses"] if household["annual_expenses"] else 0.0)),
        "unfairness": clip(max(0.0, my_load - their_load) / params["workload_scale_hours"]),
        "financial_strain": clip((burden_ratio - params["strain_threshold"]) / (1 - params["strain_threshold"])),
    }


def utility(pid, x, y, partners, household, params):
    """Partner pid のその年の満足度（効用）。教育用の重み付きモデル

    U_i = clip( base
               − (1 − buffer × comm) × (w1 × 家事の希望とのずれ + w2 × 生活費の希望とのずれ)
               + w3 × comm − w4 × ストレス + w5 × 自由時間 − w6 × 超過
               − w7 × 公平性の重視度 × 不公平感 − w8 × 家計の圧迫, 0, 1)

    comm（コミュニケーション）は 2 人の指標の平均。buffer は「話し合いで不満が和らぐ」程度（架空の仮定）。
    不公平感 = 自分の（労働時間 + 家事時間）が相手より多い分。家計の圧迫 = 生活費の負担 / 自分の所得 が
    strain_threshold を超えた分。どちらも「何を負担と感じるか」についてのモデル上の仮定。
    """
    c = utility_components(pid, x, y, partners, household, params)
    mismatch = params["w_housework"] * c["housework_mismatch"] + params["w_financial"] * c["financial_mismatch"]
    damp = 1 - params["communication_buffer"] * c["communication"]
    u = (params["base_satisfaction"]
         - damp * mismatch
         + params["w_communication"] * c["communication"]
         - params["w_stress"] * c["stress"]
         + params["w_free_time"] * c["free_time"]
         - params["w_overload"] * c["overload"]
         - params["w_fairness"] * partners[pid]["fairness_weight"] * c["unfairness"]
         - params["w_financial_strain"] * c["financial_strain"])
    return clip(u)


def utilities(x, y, partners, household, params):
    """(U_A, U_B)"""
    return (utility("A", x, y, partners, household, params),
            utility("B", x, y, partners, household, params))


def satisfaction_summary(ua, ub):
    """2 人の満足度をまとめる：平均・最低・差。平均だけで公平性を評価しない"""
    return {"A": ua, "B": ub, "mean": (ua + ub) / 2, "min": min(ua, ub), "diff": abs(ua - ub)}


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：満足度の重み（w_housework など）を変えて、最適な分担がどう変わるか調べる（Notebook 02）。
# TODO 2：communication_buffer = 0（話し合いで不満が和らがない）にして、RQ3 の結果を比べる。
# TODO 3：不公平感の定義を「家事時間だけの差」や「生活費の所得に対する割合の差」に変えてみる。
# TODO 4：家事の種類（料理・掃除・育児など）ごとに分担を決めるモデルにする。
