"""【教員用】F-1 の Tiny Dataset（人工データ）を生成する ― Phase 1 初期版

- すべて教材のための人工データ（仮定値）。実際の統計・物件・人物ではない。
- 乱数のシードを固定しているので、何回実行しても同じ CSV になる（UTF-8、改行 LF）。
- 通常のケースに加えて、境界条件・制約違反のケースを意図的に入れている（各関数のコメント）。
- Phase 2 で件数・分布・境界条件を見直し、scripts/validate_datasets.py で検証する予定。
- 標準ライブラリだけで動く。

使い方（f1-career-income-optimization ディレクトリで）:
    python3 scripts/generate_synthetic_data.py              # data/f1a〜f1d に書き出す
    python3 scripts/generate_synthetic_data.py --check      # 書き出さずに、既存ファイルと一致するか確かめる
"""

import argparse
import csv
import io
import random
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
SEED = 2026


def career_options(rng):
    """F-1A：キャリア候補 24 件（万円・歳）"""
    rows = []
    paths = [  # (名前, 就業開始年齢, 初年度年収の範囲, 昇給率の範囲, 教育費の範囲)
        ("high_school_job", 18, (230, 270), (0.015, 0.025), (0, 0)),
        ("vocational_job", 20, (260, 310), (0.018, 0.028), (150, 260)),
        ("junior_college_job", 20, (250, 300), (0.018, 0.026), (180, 280)),
        ("university_job", 22, (290, 350), (0.020, 0.032), (300, 520)),
        ("graduate_job", 24, (330, 400), (0.022, 0.034), (450, 700)),
    ]
    for i in range(20):
        name, start, sal, gr, cost = paths[i % len(paths)]
        rows.append({
            "career_id": f"C{i + 1:02d}", "career_name": f"{name}_{i // len(paths) + 1}",
            "start_age": start, "retirement_age": rng.choice([60, 65, 65, 65, 70]),
            "initial_salary": rng.randrange(sal[0], sal[1] + 1, 5),
            "annual_growth": round(rng.uniform(*gr), 3),
            "education_cost": rng.randrange(cost[0], cost[1] + 1, 10) if cost[1] else 0,
        })
    # 境界条件：昇給率 0、教育費が大きく回収できない候補、開始年齢と退職年齢が近い候補、同じ値の候補
    rows += [
        {"career_id": "C21", "career_name": "zero_growth", "start_age": 18, "retirement_age": 65,
         "initial_salary": 300, "annual_growth": 0.0, "education_cost": 0},
        {"career_id": "C22", "career_name": "high_cost", "start_age": 26, "retirement_age": 65,
         "initial_salary": 320, "annual_growth": 0.02, "education_cost": 2000},
        {"career_id": "C23", "career_name": "short_career", "start_age": 64, "retirement_age": 65,
         "initial_salary": 300, "annual_growth": 0.02, "education_cost": 0},
        {"career_id": "C24", "career_name": "same_as_C21", "start_age": 18, "retirement_age": 65,
         "initial_salary": 300, "annual_growth": 0.0, "education_cost": 0},
    ]
    return rows


def work_options(rng):
    """F-1B：勤務形態 6 件（万円／年、時間／週）"""
    return [
        {"option_id": "W1", "work_style": "full_time", "annual_income": 400, "weekly_work_hours": 40},
        {"option_id": "W2", "work_style": "full_time_overtime", "annual_income": 480, "weekly_work_hours": 55},
        {"option_id": "W3", "work_style": "short_time", "annual_income": 280, "weekly_work_hours": 28},
        {"option_id": "W4", "work_style": "part_time", "annual_income": 150, "weekly_work_hours": 20},
        {"option_id": "W5", "work_style": "remote_flexible", "annual_income": 360, "weekly_work_hours": 35},
        {"option_id": "W6", "work_style": "leave", "annual_income": 0, "weekly_work_hours": 0},
    ]


def household_scenarios(rng):
    """F-1B：世帯の条件 24 件（万円／年、時間／週）。育児のみ・介護のみ・両方・どちらもなしを含む"""
    rows = []
    for i in range(22):
        kind = i % 4   # 0: 育児、1: 介護、2: 両方、3: どちらもなし
        rows.append({
            "scenario_id": f"S{i + 1:02d}",
            "living_cost": rng.randrange(280, 461, 10),
            "childcare_cost": rng.randrange(30, 121, 10) if kind in (0, 2) else 0,
            "eldercare_cost": rng.randrange(20, 101, 10) if kind in (1, 2) else 0,
            "required_childcare_hours": rng.randrange(10, 41, 5) if kind in (0, 2) else 0,
            "required_eldercare_hours": rng.randrange(5, 26, 5) if kind in (1, 2) else 0,
        })
    # 制約違反：2 人とも休業しても時間が足りない世帯（120 + 70 > 2 × (168 − 77)）、支出が非常に大きい世帯
    rows += [
        {"scenario_id": "S23", "living_cost": 360, "childcare_cost": 80, "eldercare_cost": 80,
         "required_childcare_hours": 120, "required_eldercare_hours": 70},
        {"scenario_id": "S24", "living_cost": 900, "childcare_cost": 100, "eldercare_cost": 0,
         "required_childcare_hours": 20, "required_eldercare_hours": 0},
    ]
    return rows


def housing_options(rng):
    """F-1C：住宅候補 30 件。価格は 100 万円単位で、同じ価格の物件が複数ある"""
    rows = []
    for i in range(30):
        commute = rng.randrange(15, 91, 5)
        # 通勤時間が短いほど価格が高い傾向（教材用の仮定）+ ばらつき
        price = max(1500, int(round((5200 - commute * 35 + rng.randint(-600, 600)) / 100)) * 100)
        rows.append({
            "housing_id": f"H{i + 1:02d}", "area": f"area_{chr(ord('A') + i % 8)}",
            "purchase_price": price,
            "monthly_rent": round(price / 280 + rng.uniform(-1.0, 1.0), 1),
            "floor_area": rng.randrange(40, 101, 5),
            "annual_maintenance_cost": rng.randrange(15, 41, 5),
            "commute_minutes": commute,
        })
    # 境界条件：同じ価格の物件を確実に含める
    rows[1]["purchase_price"] = rows[0]["purchase_price"]
    rows[2]["purchase_price"] = rows[0]["purchase_price"]
    return rows


def family_members(rng):
    """F-1D：12 家族 × 親子 2 人 = 24 人（万円、歳）"""
    rows = []
    for f in range(12):
        fid = f"F{f + 1:02d}"
        parent_income = rng.randrange(300, 801, 10)
        rows.append({"person_id": f"{fid}-P", "family_id": fid, "generation": 1, "role": "parent",
                     "age": rng.randrange(40, 61), "annual_income": parent_income,
                     "annual_expense": rng.randrange(250, parent_income + 61, 10),   # 親が赤字の家族を含む
                     "initial_assets": rng.randrange(0, 3001, 100)})
        rows.append({"person_id": f"{fid}-C", "family_id": fid, "generation": 2, "role": "child",
                     "age": rng.randrange(15, 26), "annual_income": rng.choice([0, 0, 60, 120, 250]),
                     "annual_expense": rng.randrange(60, 181, 10),
                     "initial_assets": rng.randrange(0, 201, 10)})
    return rows


def transfer_scenarios(rng):
    """F-1D：資金移転のシナリオ 24 件（額 × 開始年 × 期間）。移転額 0 を含む"""
    rows, i = [], 1
    for amount in (0, 50, 100, 150):
        for start in (1, 3):
            for duration in (2, 4, 6):
                rows.append({"scenario_id": f"T{i:02d}", "sender_role": "parent", "receiver_role": "child",
                             "annual_transfer": amount, "start_year": start, "duration_years": duration})
                i += 1
    return rows


FILES = {
    "f1a/career_options_tiny.csv": career_options,
    "f1b/work_options_tiny.csv": work_options,
    "f1b/household_scenarios_tiny.csv": household_scenarios,
    "f1c/housing_options_tiny.csv": housing_options,
    "f1d/family_members_tiny.csv": family_members,
    "f1d/transfer_scenarios_tiny.csv": transfer_scenarios,
}


def render(rows):
    buf = io.StringIO()
    writer = csv.DictWriter(buf, fieldnames=list(rows[0].keys()), lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def generate_all():
    """{相対パス: CSV の文字列}。ファイルごとに別の乱数（シード + 番号）を使う"""
    out = {}
    for k, (rel, func) in enumerate(FILES.items()):
        out[rel] = render(func(random.Random(SEED + k)))
    return out


def main():
    parser = argparse.ArgumentParser(description="F-1 Tiny Dataset（人工データ）の生成")
    parser.add_argument("--check", action="store_true", help="書き出さずに、既存ファイルと一致するか確かめる")
    args = parser.parse_args()
    ok = True
    for rel, text in generate_all().items():
        path = DATA_DIR / rel
        if args.check:
            same = path.exists() and path.read_text(encoding="utf-8") == text
            print(f"{'一致' if same else '不一致'}: {rel}")
            ok &= same
        else:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(text, encoding="utf-8", newline="")
            print(f"作成: {rel}（{text.count(chr(10)) - 1} 件）")
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
