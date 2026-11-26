"""【教員用】F-1 のデータセット（Tiny・Small）の品質を検証する（標準ライブラリのみ）

検証の結果は 3 種類に分けて表示する。
- [エラー]   データ自体の破損：必須列がない、型が違う、ID の重複、外部キーの不整合、必須の値の欠損、単位の範囲外 など。
             1 件でもあれば終了コード 1。
- [境界条件] 教材のために**意図的に入れた**ケース（時間制約の違反、赤字、回収できない教育費 など）。
             学生がプログラムで検出する対象なので、データから除外しない。存在しなければエラーにする。
- [情報]     件数、人工データ（_tiny）と公開統計（_small）の区別、Small の欠損（空欄）の数 など。

使い方（f1-career-income-optimization ディレクトリで）:
    python3 scripts/validate_datasets.py                 # 検証して結果を表示する
    python3 scripts/validate_datasets.py --report        # docs/data_validation_report.md にも書き出す
"""

import argparse
import csv
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
REPORT = PROJECT_DIR / "docs" / "data_validation_report.md"
HOURS_PER_WEEK = 168
BASIC_HOURS = 77   # 教材の初期値（Notebook のパラメータと同じ）

# 列の型：str、int、float。"opt_" で始まる型は空欄を許す（公開統計の欠損・秘匿・該当なし）
SCHEMA = {
    "f1a/career_options_tiny.csv": {"career_id": "str", "career_name": "str", "start_age": "int",
                                    "retirement_age": "int", "initial_salary": "float", "annual_growth": "float",
                                    "education_cost": "int"},
    "f1b/work_options_tiny.csv": {"option_id": "str", "work_style": "str", "annual_income": "int",
                                  "weekly_work_hours": "int"},
    "f1b/household_scenarios_tiny.csv": {"scenario_id": "str", "living_cost": "int", "childcare_cost": "int",
                                         "eldercare_cost": "int", "required_childcare_hours": "int",
                                         "required_eldercare_hours": "int"},
    "f1c/housing_options_tiny.csv": {"housing_id": "str", "area": "str", "purchase_price": "int",
                                     "monthly_rent": "float", "floor_area": "int", "annual_maintenance_cost": "int",
                                     "commute_minutes": "int"},
    "f1d/family_members_tiny.csv": {"person_id": "str", "family_id": "str", "generation": "int", "role": "str",
                                    "age": "int", "annual_income": "int", "annual_expense": "int",
                                    "initial_assets": "int"},
    "f1d/transfer_scenarios_tiny.csv": {"scenario_id": "str", "sender_role": "str", "receiver_role": "str",
                                        "annual_transfer": "int", "start_year": "int", "duration_years": "int"},
    "f1a/salary_by_age_small.csv": {"education_code": "str", "education": "str", "age_group": "str",
                                    "age_min": "opt_int", "age_max": "opt_int", "mean_age": "opt_float",
                                    "monthly_cash_earnings": "opt_float", "monthly_scheduled_earnings": "opt_float",
                                    "annual_special_earnings": "opt_float", "workers_10": "opt_float",
                                    "survey_year": "int", "source": "str"},
    "f1b/household_expenses_small.csv": {"age_group": "str", "category_code": "str", "category": "str",
                                         "value": "opt_float", "unit": "str", "survey_year": "int",
                                         "household_type": "str", "source": "str"},
    "f1d/household_assets_small.csv": {"household_type_code": "str", "household_type": "str",
                                       "head_age_group": "str", "head_mean_age": "opt_float",
                                       "household_size": "opt_float", "financial_assets": "opt_float",
                                       "financial_liabilities": "opt_float", "housing_land_assets": "opt_float",
                                       "survey_year": "int", "source": "str"},
    "f1d/learning_cost_small.csv": {"school_type": "str", "ownership_code": "str", "ownership": "str",
                                    "total_cost": "opt_float", "school_education_cost": "opt_float",
                                    "school_lunch_cost": "opt_float", "out_of_school_cost": "opt_float",
                                    "survey_year": "str", "source": "str"},
}
# 1 行を一意に決める列（主キー）
KEYS = {
    "f1a/career_options_tiny.csv": ["career_id"], "f1b/work_options_tiny.csv": ["option_id"],
    "f1b/household_scenarios_tiny.csv": ["scenario_id"], "f1c/housing_options_tiny.csv": ["housing_id"],
    "f1d/family_members_tiny.csv": ["person_id"], "f1d/transfer_scenarios_tiny.csv": ["scenario_id"],
    "f1a/salary_by_age_small.csv": ["education_code", "age_group"],
    "f1b/household_expenses_small.csv": ["age_group", "category_code"],
    "f1d/household_assets_small.csv": ["household_type_code", "head_age_group"],
    "f1d/learning_cost_small.csv": ["school_type", "ownership_code"],
}
OPTIONAL_FILES = {"f1c/housing_prices_small.csv"}   # 教員が手動で取得するデータ（なくてもエラーにしない）


class Result:
    def __init__(self):
        self.errors, self.boundaries, self.infos = [], [], []

    def error(self, msg):
        self.errors.append(msg)

    def boundary(self, ok, msg):
        if ok:
            self.boundaries.append(msg)
        else:
            self.errors.append(f"境界条件がありません：{msg}")

    def info(self, msg):
        self.infos.append(msg)


def convert(value, kind):
    if kind.startswith("opt_"):
        if value == "":
            return None
        kind = kind[4:]
    if value == "":
        raise ValueError("空欄")
    return {"str": str, "int": int, "float": float}[kind](value)


def load(rel, res):
    path = DATA_DIR / rel
    with open(path, encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        header = reader.fieldnames or []
        raw = list(reader)
    schema = SCHEMA[rel]
    missing = [c for c in schema if c not in header]
    extra = [c for c in header if c not in schema]
    if missing:
        res.error(f"{rel}：必須列がありません {missing}")
        return []
    if extra:
        res.error(f"{rel}：定義されていない列があります {extra}")
    rows, blanks = [], 0
    for n, r in enumerate(raw, start=2):
        row = {}
        for col, kind in schema.items():
            try:
                row[col] = convert(r[col], kind)
            except ValueError:
                res.error(f"{rel} {n} 行目：{col} = {r[col]!r} を {kind} に変換できません")
            if r[col] == "":
                blanks += 1
        rows.append(row)
    keys = [tuple(r.get(k) for k in KEYS[rel]) for r in rows]
    if len(keys) != len(set(keys)):
        res.error(f"{rel}：主キー {KEYS[rel]} が重複しています")
    kind = "人工データ（Tiny）" if rel.endswith("_tiny.csv") else "公開統計を加工（Small）"
    res.info(f"{rel}：{len(rows)} 行 × {len(header)} 列、{kind}" + (f"、空欄 {blanks} 個（欠損・秘匿・該当なし）" if blanks else ""))
    if rel.endswith("_small.csv") and not all(r.get("source") for r in rows):
        res.error(f"{rel}：source（出典）が空の行があります")
    return rows


def check_ranges(name, rows, res, checks):
    for r in rows:
        for col, low, high in checks:
            v = r.get(col)
            if v is not None and not (low <= v <= high):
                res.error(f"{name}：{col} = {v} が範囲 {low}〜{high} の外です（{r}）")


def validate(res):
    d = {}
    for rel in SCHEMA:
        if (DATA_DIR / rel).exists():
            d[rel] = load(rel, res)
        else:
            res.error(f"{rel}：ファイルがありません")
            d[rel] = []
    for rel in OPTIONAL_FILES:
        res.info(f"{rel}：{'あり（形式は未検証）' if (DATA_DIR / rel).exists() else 'なし（教員が手動で取得するデータ）'}")

    # ---------------- F-1A ----------------
    careers = d["f1a/career_options_tiny.csv"]
    check_ranges("F-1A", careers, res, [("start_age", 15, 80), ("retirement_age", 15, 80),
                                         ("initial_salary", 0, 5000), ("annual_growth", -0.5, 0.5),
                                         ("education_cost", 0, 5000)])
    for c in careers:
        if c["start_age"] > c["retirement_age"]:
            res.error(f"F-1A：{c['career_id']} の就業開始年齢が退職年齢より後です（年齢と就業期間の不整合）")
    years = {c["career_id"]: c["retirement_age"] - c["start_age"] for c in careers}
    res.boundary(any(c["annual_growth"] == 0 for c in careers), "F-1A 昇給率 0 の候補")
    res.boundary(any(c["education_cost"] == 0 for c in careers), "F-1A 教育費 0 の候補")
    res.boundary(any(v == 0 for v in years.values()), "F-1A 就業期間 0 年の候補")
    sig = [(c["start_age"], c["retirement_age"], c["initial_salary"], c["annual_growth"], c["education_cost"])
           for c in careers]
    res.boundary(len(sig) != len(set(sig)), "F-1A 同じ生涯所得になる候補（条件がすべて同じ候補）")

    def net_by_age(c, age):     # 教育費を 18 歳で払う仮定の、age 歳までの累積（検証用の簡単な計算）
        total = -c["education_cost"]
        for a in range(18, age + 1):
            if c["start_age"] <= a < c["retirement_age"]:
                total += c["initial_salary"] * (1 + c["annual_growth"]) ** (a - c["start_age"])
        return total
    base = next((c for c in careers if c["career_id"] == "C21"), None)
    never = [c["career_id"] for c in careers if base and c["education_cost"] > 0
             and all(net_by_age(c, a) < net_by_age(base, a) for a in range(18, 65))]
    res.boundary(bool(never), f"F-1A 教育費を回収できない候補（比較対象 C21 に退職まで追いつかない：{never}）")

    # ---------------- F-1B ----------------
    works = d["f1b/work_options_tiny.csv"]
    homes = d["f1b/household_scenarios_tiny.csv"]
    check_ranges("F-1B 勤務形態", works, res, [("annual_income", 0, 3000), ("weekly_work_hours", 0, HOURS_PER_WEEK)])
    check_ranges("F-1B 世帯", homes, res, [("living_cost", 0, 3000), ("childcare_cost", 0, 1000),
                                            ("eldercare_cost", 0, 1000), ("required_childcare_hours", 0, HOURS_PER_WEEK * 2),
                                            ("required_eldercare_hours", 0, HOURS_PER_WEEK * 2)])
    if works and homes:
        incomes = [a["annual_income"] + b["annual_income"] for a in works for b in works]
        expenses = [h["living_cost"] + h["childcare_cost"] + h["eldercare_cost"] for h in homes]
        res.boundary(any(i >= e for i in incomes for e in expenses), "F-1B 年間収支が黒字になる組合せ")
        res.boundary(any(max(incomes) < e for e in expenses), "F-1B どの組合せでも赤字になる世帯")
        cap = 2 * (HOURS_PER_WEEK - BASIC_HOURS)
        need = {h["scenario_id"]: h["required_childcare_hours"] + h["required_eldercare_hours"] for h in homes}
        res.boundary(any(v > cap for v in need.values()),
                     f"F-1B 2 人とも休業しても必要な育児・介護時間を満たせない世帯（必要時間 > {cap}）")
        full = min(w["weekly_work_hours"] for w in works if w["work_style"] == "full_time")
        exact = 2 * (HOURS_PER_WEEK - BASIC_HOURS - full)
        res.boundary(exact in need.values(), f"F-1B 時間制約をちょうど満たす世帯（フルタイム 2 人で残り時間が 0、必要時間 {exact}）")
        res.boundary(any(v > exact for v in need.values()), "F-1B フルタイム 2 人では時間制約に違反する世帯")
        res.boundary(any(i >= e and v <= exact for i in incomes for e, v in zip(expenses, need.values())),
                     "F-1B 所得の制約と時間の制約の両方を満たせる世帯")

    # ---------------- F-1C ----------------
    houses = d["f1c/housing_options_tiny.csv"]
    check_ranges("F-1C", houses, res, [("purchase_price", 1, 100000), ("monthly_rent", 0, 1000),
                                        ("floor_area", 1, 1000), ("annual_maintenance_cost", 0, 1000),
                                        ("commute_minutes", 0, 300)])
    prices = [h["purchase_price"] for h in houses]
    res.boundary(len(prices) != len(set(prices)), "F-1C 同じ価格の物件が複数")
    res.boundary(3000 in prices, "F-1C 予算 3,000 万円と価格が等しい物件")
    res.boundary(any(h["commute_minutes"] > 60 for h in houses), "F-1C 通勤時間 60 分を超える物件（通勤時間の制約違反）")
    if prices:
        res.info(f"F-1C 価格の範囲 {min(prices)}〜{max(prices)} 万円：予算 {min(prices) - 100} ならすべて予算超過、"
                 f"{max(prices)} ならすべて予算以内（Notebook の動作確認で使う）")

    # ---------------- F-1D ----------------
    members = d["f1d/family_members_tiny.csv"]
    transfers = d["f1d/transfer_scenarios_tiny.csv"]
    check_ranges("F-1D 家族", members, res, [("generation", 1, 3), ("age", 0, 110), ("annual_income", 0, 5000),
                                               ("annual_expense", 0, 5000), ("initial_assets", -10000, 100000)])
    check_ranges("F-1D 移転", transfers, res, [("annual_transfer", 0, 5000), ("start_year", 1, 50),
                                                 ("duration_years", 0, 50)])
    families = {}
    for m in members:
        families.setdefault(m["family_id"], []).append(m)
        if not m["person_id"].startswith(m["family_id"]):
            res.error(f"F-1D：{m['person_id']} の ID が family_id {m['family_id']} と一致しません（外部キー）")
        if (m["role"], m["generation"]) not in {("parent", 1), ("child", 2)}:
            res.error(f"F-1D：{m['person_id']} の role と generation が一致しません")
    for fid, ms in families.items():
        roles = sorted(m["role"] for m in ms)
        if roles != ["child", "parent"]:
            res.error(f"F-1D：家族 {fid} の構成が親 1 人・子 1 人ではありません {roles}")
        elif next(m for m in ms if m["role"] == "parent")["age"] <= next(m for m in ms if m["role"] == "child")["age"]:
            res.error(f"F-1D：家族 {fid} の親の年齢が子以下です")
    for t in transfers:
        if t["sender_role"] not in {"parent", "child"} or t["receiver_role"] not in {"parent", "child"}:
            res.error(f"F-1D：{t['scenario_id']} の送り手・受け手の役割が家族のデータにありません（参照先）")
    res.boundary(any(t["annual_transfer"] == 0 for t in transfers), "F-1D 移転額 0")
    res.boundary(any(t["duration_years"] == 0 for t in transfers), "F-1D 移転期間 0")
    parents = [m for m in members if m["role"] == "parent"]
    res.boundary(any(p["annual_income"] < p["annual_expense"] for p in parents), "F-1D 親の年間収支が赤字")
    children = [m for m in members if m["role"] == "child"]
    res.boundary(any(c["annual_income"] < c["annual_expense"] and c["initial_assets"] < 5 * (c["annual_expense"] - c["annual_income"])
                     for c in children), "F-1D 移転がなければ 5 年以内に子の資産不足が起きる家族")
    res.boundary(any(p["initial_assets"] >= 1000 and p["annual_income"] >= p["annual_expense"] for p in parents),
                 "F-1D 最低生活資金（例：1,000 万円）を維持できる親")

    # ---------------- Small（公開統計） ----------------
    sal = d["f1a/salary_by_age_small.csv"]
    check_ranges("F-1A Small", sal, res, [("monthly_cash_earnings", 1, 300), ("annual_special_earnings", 0, 2000)])
    if sal and any(r["monthly_scheduled_earnings"] and r["monthly_cash_earnings"]
                   and r["monthly_scheduled_earnings"] > r["monthly_cash_earnings"] for r in sal):
        res.error("F-1A Small：所定内給与額がきまって支給する現金給与額を超える行があります（定義上ありえない）")
    exp = d["f1b/household_expenses_small.csv"]
    for r in exp:
        if r["unit"] not in {"万円/月", "人"}:
            res.error(f"F-1B Small：単位 {r['unit']!r} が想定外です")
    check_ranges("F-1B Small", [r for r in exp if r["unit"] == "万円/月"], res, [("value", 0, 200)])
    assets = d["f1d/household_assets_small.csv"]
    check_ranges("F-1D Small", assets, res, [("financial_assets", 0, 100000), ("financial_liabilities", 0, 100000)])
    cost = d["f1d/learning_cost_small.csv"]
    check_ranges("F-1D Small 学習費", cost, res, [("total_cost", 0, 1000)])
    return res


def write_report(res):
    lines = ["# データ品質の検証結果", "", "`scripts/validate_datasets.py --report` が自動で作成する。", "",
             f"- エラー（データの破損）：{len(res.errors)} 件",
             f"- 境界条件（意図的に含めたケース。学生が検出する対象）：{len(res.boundaries)} 件", "",
             "## エラー", ""] + ([f"- {e}" for e in res.errors] or ["- なし"]) + \
            ["", "## 境界条件（意図的）", ""] + [f"- {b}" for b in res.boundaries] + \
            ["", "## 情報", ""] + [f"- {i}" for i in res.infos] + [""]
    REPORT.write_text("\n".join(lines), encoding="utf-8")
    print(f"書き出し: {REPORT.relative_to(PROJECT_DIR)}")


def main():
    parser = argparse.ArgumentParser(description="F-1 データセットの検証")
    parser.add_argument("--report", action="store_true", help="docs/data_validation_report.md に書き出す")
    args = parser.parse_args()
    res = validate(Result())
    for e in res.errors:
        print("[エラー]", e)
    for b in res.boundaries:
        print("[境界条件]", b)
    for i in res.infos:
        print("[情報]", i)
    print(f"エラー {len(res.errors)} 件、境界条件 {len(res.boundaries)} 件")
    if args.report:
        write_report(res)
    return 1 if res.errors else 0


if __name__ == "__main__":
    sys.exit(main())
