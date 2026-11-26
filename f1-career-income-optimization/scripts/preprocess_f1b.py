"""【教員用】F-1B：家計調査（家計収支編、2025年）→ data/f1b/household_expenses_small.csv

原データ：data/raw/f1b/family_income_expenditure_2025_age.xlsx（scripts/download_datasets.py で取得）
  二人以上の世帯 詳細結果表 年次 第3-2表「世帯主の年齢階級別1世帯当たり1か月間の収入と支出」の「二人」シート
  （二人以上の世帯）。
取り出すもの：世帯主の年齢階級（12 区分。平均と再掲は除く）× 支出の大分類（消費支出と 10 費目）と世帯人員・18 歳未満人員 = 13 項目 × 12 = 156 行（縦長の形式）
  - 単位：円／月（1 世帯当たり 1 か月間の平均）→ 万円／月（÷10000、小数 4 桁）。**年額（× 12）は計算しない**（学生の課題）。
  - 世帯人員・18 歳未満人員も、世帯の規模を確かめるために「人」の単位で残す（category_code が household_size など）。
"""

import re

from preprocess_common import clean_label, require_raw, read_xlsx, scaled, to_number, write_csv

RAW = "f1b/family_income_expenditure_2025_age.xlsx"
OUT = "f1b/household_expenses_small.csv"
AGE_COLUMNS = list(range(14, 26))      # 「～34歳」〜「85歳～」（13 列目は平均）
ITEMS = {  # 原データの項目名 → (category_code, 単位)
    "世帯人員": ("household_size", "人"), "18歳未満人員": ("members_under_18", "人"),
    "消費支出": ("consumption_total", "万円/月"),
    "食料": ("food", "万円/月"), "住居": ("housing", "万円/月"), "光熱・水道": ("utilities", "万円/月"),
    "家具・家事用品": ("furniture_household", "万円/月"), "被服及び履物": ("clothing", "万円/月"),
    "保健医療": ("medical", "万円/月"), "交通・通信": ("transport_communication", "万円/月"),
    "教育": ("education", "万円/月"), "教養娯楽": ("culture_recreation", "万円/月"),
    "その他の消費支出": ("other_consumption", "万円/月"),
}
COLUMNS = ["age_group", "category_code", "category", "value", "unit", "survey_year", "household_type", "source"]


def main():
    rows = read_xlsx(require_raw(RAW))["二人"]
    assert "１か月間" in rows[4][9], "表題が想定と違います"
    # 見出しの後ろのふりがな・番号（例：「～34歳２４サイ」）を取り除く
    headers = [re.sub(r"歳.*$", "歳", rows[7][c]) if not rows[7][c].startswith("85") else "85歳～"
               for c in AGE_COLUMNS]
    out, used = [], set()
    for r in rows[8:]:
        if len(r) < 26 or r[11] not in ITEMS or r[11] in used:
            continue                     # 同じ名前の項目が後ろにもう一度出てくる場合は、最初の行だけを使う
        used.add(r[11])
        code, unit = ITEMS[r[11]]
        for c, age in zip(AGE_COLUMNS, headers):
            v = to_number(r[c])
            value = v if unit == "人" else scaled(v, 10000, 4)
            out.append({"age_group": age, "category_code": code, "category": r[11], "value": value, "unit": unit,
                        "survey_year": 2025, "household_type": "二人以上の世帯", "source": "family_income_expenditure_2025"})
    found = {r["category_code"] for r in out}
    if len(found) != len(ITEMS):
        raise SystemExit(f"見つからない項目があります: {set(c for c, _ in ITEMS.values()) - found}")
    write_csv(OUT, COLUMNS, out)


if __name__ == "__main__":
    main()
