# F1：キャリア選択のシナリオ（進学・就職・資格取得・転職）
#
# 1 つのシナリオは、次のキーを持つ「辞書」で表す（data/sample_careers.json と同じ形）。
#
#   name, label          : 識別名と表示名
#   start_age            : 就職開始年齢（それまでは進学などで所得 0）
#   initial_salary       : 初年度年収（万円）
#   annual_growth_rate   : 年間昇給率（0.02 = 2%）
#   retirement_age       : 退職年齢（この年からは計算しない）。省略時 65
#   education_cost       : 進学費用の合計（万円）。base_age〜start_age-1 歳の各年に均等に支払う。省略時 0
#   certificate          : 資格取得（なければ null / None）
#       age              :   取得する年齢（この年に費用を支払う）
#       cost             :   取得費用（万円）
#       salary_increase  :   取得した翌年（age + 1 歳）から毎年加わる年収の増加額（万円）
#       study_years      :   取得前に学習する年数（省略時 0）
#       study_income_ratio:  学習中の年収の割合（1.0 = 減らない、0.5 = 半分。省略時 1.0）
#   job_change           : 転職（なければ null / None）
#       age              :   転職する年齢（この年から新しい年収、この年に費用を支払う）
#       new_salary       :   転職後の初年度年収（万円）
#       growth_rate      :   転職後の昇給率
#       cost             :   転職時の一時費用（万円）
#
# ■ 仮定（README 4〜7章）
#   ・転職後の初年度年収は、転職する年齢・それまでの経験によらず一定（Core の単純化。Experiment 3 で変更できる）。
#   ・資格による年収の増加は定額で、転職しても続く。資格取得は必ず成功する（成功確率は Advanced A）。
#   ・すべての数値は教育用の架空の値で、実際の賃金統計ではない。

import copy
import json
import os

import career_model as cm

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_careers.json")


# ------------------------------------------------------------
# シナリオを作る関数（Scenario A〜D）
# ------------------------------------------------------------
def early_job(initial_salary=250, growth_rate=0.02, start_age=18, name="early_job", label="Early Job"):
    """Scenario A：18 歳で就職"""
    return {"name": name, "label": label, "start_age": start_age, "initial_salary": initial_salary,
            "annual_growth_rate": growth_rate, "retirement_age": cm.RETIREMENT_AGE,
            "education_cost": 0, "certificate": None, "job_change": None}


def university(initial_salary=330, growth_rate=0.025, education_cost=400, start_age=22,
               name="university", label="University"):
    """Scenario B：進学後に就職（18〜21 歳は進学、22 歳で就職）"""
    s = early_job(initial_salary, growth_rate, start_age, name, label)
    s["education_cost"] = education_cost
    return s


def certificate(base, age=30, cost=100, salary_increase=40, study_years=0, study_income_ratio=1.0,
                name="certificate", label="Certificate"):
    """Scenario C：base のキャリアに、資格取得を加えたシナリオ（base は変更しない）"""
    s = copy.deepcopy(base)
    s.update(name=name, label=label)
    s["certificate"] = {"age": age, "cost": cost, "salary_increase": salary_increase,
                        "study_years": study_years, "study_income_ratio": study_income_ratio}
    return s


def job_change(base, age=35, new_salary=420, growth_rate=0.025, cost=30, name="job_change", label="Job Change"):
    """Scenario D：base のキャリアに、転職を加えたシナリオ（base は変更しない）"""
    s = copy.deepcopy(base)
    s.update(name=name, label=label)
    s["job_change"] = {"age": age, "new_salary": new_salary, "growth_rate": growth_rate, "cost": cost}
    return s


def with_changes(scenario, **changes):
    """シナリオのコピーを作り、一部の値を変える（元のシナリオは変更しない）

    certificate・job_change の中の値は "job_change.age" のように「.」でつないで指定する。
    例：with_changes(s, initial_salary=300, **{"job_change.age": 40})
    """
    s = copy.deepcopy(scenario)
    for key, value in changes.items():
        if "." in key:
            outer, inner = key.split(".", 1)
            if s.get(outer) is None:
                raise KeyError(f"シナリオに {outer} がありません")
            s[outer][inner] = value
        else:
            s[key] = value
    return s


# ------------------------------------------------------------
# データの読み込みと検証
# ------------------------------------------------------------
def load_scenarios(path=DATA_FILE):
    """data/sample_careers.json を読み込み、(シナリオのリスト, 設定の辞書) を返す"""
    with open(path, encoding="utf-8") as f:
        data = json.load(f)
    scenarios = data["careers"]
    for s in scenarios:
        validate_scenario(s)
    return scenarios, data.get("settings", {})


def validate_scenario(s, base_age=cm.BASE_AGE):
    """シナリオの値を確認する（不正なら ValueError / TypeError）"""
    retirement = s.get("retirement_age", cm.RETIREMENT_AGE)
    cm.validate_params(s["start_age"], retirement, s["initial_salary"], s["annual_growth_rate"], base_age)
    if s.get("education_cost", 0) < 0:
        raise ValueError("進学費用は 0 以上にしてください")
    cert = s.get("certificate")
    if cert:
        cm._check_int_age("certificate.age", cert["age"])
        if not s["start_age"] <= cert["age"] < retirement:
            raise ValueError("資格取得の年齢は、就職開始年齢以上・退職年齢未満にしてください")
        if cert["cost"] < 0:
            raise ValueError("資格取得費用は 0 以上にしてください")
        if not 0 <= cert.get("study_years", 0) <= cert["age"] - s["start_age"]:
            raise ValueError("学習年数は 0 以上で、就職後の期間に収まるようにしてください")
        if not 0 <= cert.get("study_income_ratio", 1.0) <= 1:
            raise ValueError("学習中の年収の割合は 0〜1 にしてください")
    jc = s.get("job_change")
    if jc:
        cm._check_int_age("job_change.age", jc["age"])
        if not s["start_age"] < jc["age"] < retirement:
            raise ValueError(f"転職年齢 {jc['age']} は、就職開始年齢より後・退職年齢より前にしてください")
        cm.validate_params(jc["age"], retirement, jc["new_salary"], jc["growth_rate"], base_age)
        if jc["cost"] < 0:
            raise ValueError("転職費用は 0 以上にしてください")


# ------------------------------------------------------------
# 年齢別の所得・費用・キャッシュフロー
# ------------------------------------------------------------
def incomes(s, base_age=cm.BASE_AGE):
    """年齢別の年収（万円）のリスト（i 番目 = base_age + i 歳）"""
    validate_scenario(s, base_age)
    retirement = s.get("retirement_age", cm.RETIREMENT_AGE)
    values = cm.income_by_age(s["start_age"], s["initial_salary"], s["annual_growth_rate"], retirement, base_age)

    jc = s.get("job_change")
    if jc:   # 転職年齢以降は、転職後の年収に置き換える
        after = cm.income_by_age(jc["age"], jc["new_salary"], jc["growth_rate"], retirement, base_age)
        for i in range(cm.index_of_age(jc["age"], base_age, retirement), len(values)):
            values[i] = after[i]

    cert = s.get("certificate")
    if cert:
        k = cm.index_of_age(cert["age"], base_age, retirement)
        for i in range(k - cert.get("study_years", 0), k):          # 学習中は年収が減ることがある
            values[i] *= cert.get("study_income_ratio", 1.0)
        for i in range(k + 1, len(values)):                          # 取得した翌年から年収が増える
            values[i] += cert["salary_increase"]
    return values


def costs(s, base_age=cm.BASE_AGE):
    """年齢別のキャリア関連費用（万円）のリスト（進学費用・資格取得費用・転職費用）"""
    retirement = s.get("retirement_age", cm.RETIREMENT_AGE)
    values = [0.0] * (retirement - base_age)
    study_years = s["start_age"] - base_age
    if s.get("education_cost", 0) > 0:
        if study_years == 0:
            raise ValueError("進学費用があるのに、進学期間（base_age〜start_age-1 歳）がありません")
        for i in range(study_years):
            values[i] += s["education_cost"] / study_years
    if s.get("certificate"):
        values[cm.index_of_age(s["certificate"]["age"], base_age, retirement)] += s["certificate"]["cost"]
    if s.get("job_change"):
        values[cm.index_of_age(s["job_change"]["age"], base_age, retirement)] += s["job_change"]["cost"]
    return values


def cashflows(s, base_age=cm.BASE_AGE):
    """年齢別のキャッシュフロー = 年収 − キャリア関連費用（万円）"""
    return [y - c for y, c in zip(incomes(s, base_age), costs(s, base_age))]


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：20 歳で就職するシナリオ（専門学校など）に、自分たちで仮定した進学費用を設定して比べる。
# TODO 2：進学中のアルバイト収入（年 xx 万円）を加える。
# TODO 3：転職後の初年度年収を、それまでの経験年数によって変える（例：new_salary + k × 経験年数）。
# TODO 4：資格の年収増加を、定額ではなく割合（例：+10%）にする。
# TODO 5：転職を 2 回以上できるようにする（job_change をリストにする）。
