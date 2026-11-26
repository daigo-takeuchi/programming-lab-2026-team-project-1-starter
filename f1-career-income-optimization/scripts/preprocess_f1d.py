"""【教員用】F-1D：全国家計構造調査（令和6年）・子供の学習費調査（令和5年度）→ data/f1d/*_small.csv

1) data/f1d/household_assets_small.csv
   原データ：data/raw/f1d/household_assets_2024_age.xlsx
     表番号4-4「世帯の種類，世帯区分，世帯主の性別，世帯主の年齢階級，資産・負債の種類別1世帯当たり資産現在高・負債現在高－全国」
   取り出すもの：世帯区分「全世帯」・世帯主の性別「平均」、世帯の種類（総世帯・二人以上の世帯・単身世帯）×
     世帯主の年齢階級（5 歳階級 13 区分）= 39 行。
   列：金融資産残高（貯蓄現在高）、金融負債残高、住宅・宅地資産額、世帯人員、世帯主の平均年齢。
   単位：千円 → 万円（÷10）。**純資産（資産 − 負債）は計算しない**（原表の「純金融資産」「純資産総額」は使わない。学生の課題）。

2) data/f1d/learning_cost_small.csv
   原データ：data/raw/f1d/learning_cost_2023_school_type.xlsx（「1 学校種別の学習費」）
   取り出すもの：学校種（幼稚園・小学校・中学校・高等学校（全日制））× 公立・私立 = 8 行。
   列：学習費総額、学校教育費、学校給食費、学校外活動費。単位：円（子供 1 人当たりの年間の額）→ 万円（÷10000）。
   「…」（計数があり得ない・調査対象外）は空欄のまま（例：高等学校の学校給食費）。
"""

from preprocess_common import clean_label, require_raw, read_xlsx, scaled, to_number, write_csv

ASSETS_RAW = "f1d/household_assets_2024_age.xlsx"
COST_RAW = "f1d/learning_cost_2023_school_type.xlsx"
HOUSEHOLD_TYPES = {"0_総世帯": ("all", "総世帯"), "1_二人以上の世帯": ("two_or_more", "二人以上の世帯"),
                   "2_単身世帯": ("single", "単身世帯")}
ASSET_ITEMS = {"21_金融資産残高（貯蓄現在高）": "financial_assets", "22_金融負債残高": "financial_liabilities",
               "3_住宅・宅地": "housing_land_assets"}
AGE_COLUMNS = list(range(13, 26))   # 101_30歳未満 〜 113_85歳以上（5 歳階級）


def household_assets():
    rows = read_xlsx(require_raw(ASSETS_RAW))["d04004"]
    ages = [rows[5][c].split("_", 1)[1].replace("（５歳階級）", "") for c in AGE_COLUMNS]
    ages = [a if a.endswith(("歳", "未満", "以上")) else a + "歳" for a in ages]   # 「30～34」→「30～34歳」
    assert ages[0] == "30歳未満" and ages[-1] == "85歳以上", ages
    table = {}
    for r in rows[7:]:
        if len(r) < 26 or r[5] != "0_全世帯" or r[7] != "0_平均" or r[3] not in HOUSEHOLD_TYPES:
            continue
        key = r[10] if r[10] in ASSET_ITEMS else r[8]
        for c, age in zip(AGE_COLUMNS, ages):
            table.setdefault((r[3], age), {})[key] = to_number(r[c])
    out = []
    for (htype, age), v in table.items():
        code, name = HOUSEHOLD_TYPES[htype]
        out.append({"household_type_code": code, "household_type": name, "head_age_group": age,
                    "head_mean_age": v["世帯主の年齢"], "household_size": v["世帯人員"],
                    "financial_assets": scaled(v["21_金融資産残高（貯蓄現在高）"], 10, 1),
                    "financial_liabilities": scaled(v["22_金融負債残高"], 10, 1),
                    "housing_land_assets": scaled(v["3_住宅・宅地"], 10, 1),
                    "survey_year": 2024, "source": "national_survey_family_income_2024"})
    if len(out) != len(HOUSEHOLD_TYPES) * len(AGE_COLUMNS):
        raise SystemExit(f"行数が想定と違います: {len(out)}")
    write_csv("f1d/household_assets_small.csv",
              ["household_type_code", "household_type", "head_age_group", "head_mean_age", "household_size",
               "financial_assets", "financial_liabilities", "housing_land_assets", "survey_year", "source"], out)


def learning_cost():
    rows = read_xlsx(require_raw(COST_RAW))["2023kodo001"]
    assert "単位：円" in rows[2][0], "単位の注記が想定と違います"
    schools = [clean_label(rows[9][c]) for c in (1, 3, 5, 7)]
    assert schools == ["幼稚園", "小学校", "中学校", "高等学校（全日制）"], schools
    items = {clean_label(r[0]): r for r in rows[11:] if r and r[0]}
    wanted = {"学習費総額": "total_cost", "学校教育費": "school_education_cost",
              "学校給食費": "school_lunch_cost", "学校外活動費": "out_of_school_cost"}
    out = []
    for k, school in enumerate(schools):
        for j, (ownership, code) in enumerate([("公立", "public"), ("私立", "private")]):
            col = 1 + 2 * k + j
            assert clean_label(rows[10][col]) == ownership
            row = {"school_type": school, "ownership_code": code, "ownership": ownership,
                   "survey_year": "2023年度", "source": "learning_cost_survey_2023"}
            for label, name in wanted.items():
                row[name] = scaled(to_number(items[label][col]), 10000, 4)
            out.append(row)
    write_csv("f1d/learning_cost_small.csv",
              ["school_type", "ownership_code", "ownership", *wanted.values(), "survey_year", "source"], out)


if __name__ == "__main__":
    household_assets()
    learning_cost()
