# F1：年齢別所得モデル（Python 標準ライブラリのみ）
#
#   salary(a) = initial_salary × (1 + annual_growth_rate)^(a - start_age)    （start_age ≤ a < retirement_age）
#   salary(a) = 0                                                           （a < start_age）
#
# ■ この教材での約束
#   ・金額の単位はすべて「万円」、年齢は「歳」（整数）。1 年に 1 回、その年齢の 1 年間の年収を記録する。
#   ・退職年齢 retirement_age の年からは計算しない。retirement_age = 65 なら、64 歳の 1 年間までの所得を計算する。
#   ・年齢別のリストは base_age（既定 18 歳）から始まる。リストの i 番目 = (base_age + i) 歳の値。
#   ・ここで計算するのは「額面の年収（税・社会保険料を引く前）」の、教育用の単純なモデル。
#     可処分所得（手取り）や、インフレ・税制・年金は扱わない（README 3章・17章）。

import warnings

BASE_AGE = 18          # 年齢別リストの最初の年齢（高校卒業時を想定した教育用の基準）
RETIREMENT_AGE = 65    # 既定の退職年齢（この年齢の年からは所得なし＝計算対象外）

# これを超える昇給率は「極端」とみなして警告する（例外にはしない。学生が意図的に試すことはある）
EXTREME_GROWTH_RATE = 0.20


def _check_int_age(name, value):
    # bool は int の一種なので、True / False を年齢として受け付けないように先に除く
    if isinstance(value, bool) or not isinstance(value, int):
        raise TypeError(f"{name} は整数（歳）で指定してください：{value!r}")
    if value < 0:
        raise ValueError(f"{name} は 0 以上にしてください：{value}")


def validate_params(start_age, retirement_age, initial_salary, annual_growth_rate, base_age=BASE_AGE):
    """パラメータを確認する。不正なら例外（TypeError / ValueError）、極端なら警告（UserWarning）"""
    _check_int_age("start_age", start_age)
    _check_int_age("retirement_age", retirement_age)
    _check_int_age("base_age", base_age)
    if not base_age <= start_age:
        raise ValueError(f"就職開始年齢 {start_age} が基準年齢 {base_age} より前です")
    if not start_age < retirement_age:
        raise ValueError(f"就職開始年齢 {start_age} は退職年齢 {retirement_age} より小さくしてください")
    if not isinstance(initial_salary, (int, float)) or isinstance(initial_salary, bool):
        raise TypeError(f"initial_salary は数値で指定してください：{initial_salary!r}")
    if initial_salary < 0:
        raise ValueError(f"初年度年収は 0 以上にしてください：{initial_salary}")
    if not isinstance(annual_growth_rate, (int, float)) or isinstance(annual_growth_rate, bool):
        raise TypeError(f"annual_growth_rate は数値で指定してください：{annual_growth_rate!r}")
    if annual_growth_rate <= -1:
        raise ValueError(f"昇給率は -1 より大きくしてください（-100% 以下は年収が 0 以下になる）：{annual_growth_rate}")
    if abs(annual_growth_rate) > EXTREME_GROWTH_RATE:
        warnings.warn(f"昇給率 {annual_growth_rate:.0%} は極端な値です（毎年この割合で変化し続ける仮定になります）",
                      UserWarning, stacklevel=3)


def ages(retirement_age=RETIREMENT_AGE, base_age=BASE_AGE):
    """計算対象の年齢のリスト [base_age, base_age + 1, ..., retirement_age - 1]"""
    if retirement_age <= base_age:
        raise ValueError("退職年齢は基準年齢より大きくしてください")
    return list(range(base_age, retirement_age))


def salary_at(age, start_age, initial_salary, annual_growth_rate, retirement_age=RETIREMENT_AGE):
    """age 歳の 1 年間の年収（万円）。就職前は 0。退職年齢以降は計算対象外なので ValueError"""
    if age >= retirement_age:
        raise ValueError(f"{age} 歳は退職年齢 {retirement_age} 以降なので計算対象外です")
    if age < start_age:
        return 0.0
    return initial_salary * (1 + annual_growth_rate) ** (age - start_age)


def income_by_age(start_age, initial_salary, annual_growth_rate,
                  retirement_age=RETIREMENT_AGE, base_age=BASE_AGE):
    """年齢別の年収のリスト（i 番目 = base_age + i 歳）。長さは retirement_age - base_age"""
    validate_params(start_age, retirement_age, initial_salary, annual_growth_rate, base_age)
    incomes = []
    for age in range(base_age, retirement_age):          # O(T)：T = retirement_age - base_age
        incomes.append(salary_at(age, start_age, initial_salary, annual_growth_rate, retirement_age))
    return incomes


def index_of_age(age, base_age=BASE_AGE, retirement_age=RETIREMENT_AGE):
    """年齢 → 年齢別リストの添字（範囲外は ValueError）"""
    if not base_age <= age < retirement_age:
        raise ValueError(f"{age} 歳は計算期間 {base_age}〜{retirement_age - 1} 歳の範囲外です")
    return age - base_age


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：昇給率を一定ではなく、年齢によって変える（例：40 歳以降は昇給率が下がる）。
# TODO 2：年収に上限（頭打ち）を設ける。
# TODO 3：退職年齢を 60・65・70 歳に変えて、生涯所得がどう変わるか調べる。
