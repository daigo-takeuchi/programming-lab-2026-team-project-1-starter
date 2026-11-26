"""【教員用】F-1A：賃金構造基本統計調査（令和7年）→ data/f1a/salary_by_age_small.csv

原データ：data/raw/f1a/wage_census_2025_education_age.xlsx（scripts/download_datasets.py で取得）
  一般労働者 産業大分類「学歴、年齢階級別きまって支給する現金給与額、所定内給与額及び年間賞与その他特別給与額
  （産業計・産業別）」の「産業計」シート、民営事業所、企業規模計（10人以上）の列。
取り出すもの：男女計 × 学歴（学歴計・中学・高校・専門学校・高専・短大・大学・大学院）× 年齢階級（12 区分）= 84 行
  - 性別の行は使わない（性別で進路を判断する教材にしないため）。学歴「不明」は除く。
  - 金額は千円 → 万円（÷10）。月額と年額は別の列のまま。**年収（月額 × 12 + 賞与）は計算しない**（学生の課題）。
"""

from preprocess_common import clean_label, require_raw, read_xlsx, scaled, to_number, write_csv

RAW = "f1a/wage_census_2025_education_age.xlsx"
OUT = "f1a/salary_by_age_small.csv"
EDUCATION = {"学歴計": "all", "中学": "junior_high", "高校": "high_school", "専門学校": "vocational",
             "高専・短大": "college", "大学": "university", "大学院": "graduate"}
AGE_GROUPS = [("～19歳", "", 19), ("20～24歳", 20, 24), ("25～29歳", 25, 29), ("30～34歳", 30, 34),
              ("35～39歳", 35, 39), ("40～44歳", 40, 44), ("45～49歳", 45, 49), ("50～54歳", 50, 54),
              ("55～59歳", 55, 59), ("60～64歳", 60, 64), ("65～69歳", 65, 69), ("70歳～", 70, "")]
# 企業規模計（10人以上）の列の位置（原データの第 9 行の見出しで確認）
COL = {"mean_age": 3, "mean_tenure": 4, "monthly_cash_earnings": 7, "monthly_scheduled_earnings": 8,
       "annual_special_earnings": 9, "workers_10": 10}
COLUMNS = ["education_code", "education", "age_group", "age_min", "age_max", "mean_age",
           "monthly_cash_earnings", "monthly_scheduled_earnings", "annual_special_earnings", "workers_10",
           "survey_year", "source"]


def raw_label(row):
    return row[2] if len(row) > 2 else ""


def age_label(row):
    """年齢階級の行の見出し（例：「２０～２４歳サイ」→「20～24歳」）"""
    text = clean_label(raw_label(row)).replace("サイ", "")
    return text.translate(str.maketrans("０１２３４５６７８９", "0123456789"))


def main():
    rows = read_xlsx(require_raw(RAW))["産業計"]
    # 見出しの確認（列の位置が変わっていたら止める）
    assert "千円" in rows[11][7] and "千円" in rows[11][9] and "十人" in rows[11][10], "列の構成が想定と違います"
    out, sex = [], None
    for i, row in enumerate(rows):
        raw = raw_label(row)
        if not raw or "歳" in raw:
            continue
        compact = raw.replace("\u3000", "").replace(" ", "")
        if compact.startswith("男女計"):
            sex = "total"
        elif compact.startswith("男\n学歴計"):
            sex = "male"
        elif compact.startswith("女\n学歴計"):
            sex = "female"
        if sex != "total":
            continue                      # 性別の行は使わない
        edu = clean_label(raw.split("\n")[-1])
        if edu not in EDUCATION:
            continue                      # 「不明」など
        for k, (label, age_min, age_max) in enumerate(AGE_GROUPS, start=1):
            r = rows[i + k]
            if age_label(r) != label:
                raise SystemExit(f"{i + k} 行目：年齢階級 {age_label(r)!r} が想定 {label!r} と違います")
            out.append({
                "education_code": EDUCATION[edu], "education": edu, "age_group": label,
                "age_min": age_min, "age_max": age_max,
                "mean_age": to_number(r[COL["mean_age"]]),
                "monthly_cash_earnings": scaled(to_number(r[COL["monthly_cash_earnings"]]), 10, 2),
                "monthly_scheduled_earnings": scaled(to_number(r[COL["monthly_scheduled_earnings"]]), 10, 2),
                "annual_special_earnings": scaled(to_number(r[COL["annual_special_earnings"]]), 10, 2),
                "workers_10": to_number(r[COL["workers_10"]]),
                "survey_year": 2025, "source": "wage_census_2025",
            })
    codes = [r["education_code"] for r in out]
    if sorted(set(codes)) != sorted(EDUCATION.values()) or len(out) != len(EDUCATION) * len(AGE_GROUPS):
        raise SystemExit(f"学歴・年齢の区分が想定と違います: {sorted(set(codes))}, {len(out)} 行")
    write_csv(OUT, COLUMNS, out)


if __name__ == "__main__":
    main()
