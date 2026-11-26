"""【教員用】F-1C：不動産情報ライブラリ「不動産取引価格情報」→ data/f1c/housing_prices_small.csv

**状態：未検証**（2026-11-27 時点で原データを取得していないため、実際の CSV で一度も実行していない）。

原データの取得（教員が Web 画面で行う。docs/dataset_sources.md の手順）:
  https://www.reinfolib.mlit.go.jp/realEstatePrices/ で、地域（1〜2 市区町村）・取引時期（直近 1〜2 年）・
  種類（中古マンション等）を選んで CSV をダウンロードし、data/raw/f1c/ に置く（ファイル名は自由、*.csv）。
  - Web 画面の CSV 出力は内部の仕組み（公開されていない URL）で動くため、スクリプトからは取得しない。
  - API（要申請・API キー）は使わない。

処理:
  - 文字コードは UTF-8（BOM 付きを含む）か CP932 を自動判定する。
  - 列名は見出しの候補から探す。**見つからない列があれば止める**（列名を推測して埋めない）。
  - 残す列：取引価格（総額）→ 万円、面積（㎡）、取引時期、市区町村名、地区名、種類、建築年（あれば）。
  - 価格・面積が空欄または数値でない行は除外し、除外した件数を表示する。
  - 家賃・通勤時間は**元のデータにないので作らない**。人工データ（housing_options_tiny.csv）とは別のファイルにする。
"""

import csv
import re
import sys
from pathlib import Path

from preprocess_common import RAW_DIR, write_csv

CANDIDATES = {  # 出力の列名: 原データの見出しの候補（未検証）
    "trade_price_yen": ["取引価格（総額）", "取引価格(総額)", "TradePrice"],
    "floor_area_m2": ["面積（㎡）", "面積(㎡)", "Area"],
    "period": ["取引時期", "取引時点", "Period"],
    "municipality": ["市区町村名", "Municipality"],
    "district": ["地区名", "DistrictName"],
    "property_type": ["種類", "Type"],
    "building_year": ["建築年", "BuildingYear"],
}
REQUIRED = ["trade_price_yen", "floor_area_m2", "period", "municipality", "property_type"]


def read_any(path):
    data = path.read_bytes()
    for enc in ("utf-8-sig", "cp932"):
        try:
            return list(csv.DictReader(data.decode(enc).splitlines()))
        except UnicodeDecodeError:
            continue
    raise SystemExit(f"{path.name}：文字コードを判定できません")


def main():
    files = sorted((RAW_DIR / "f1c").glob("*.csv"))
    if not files:
        raise SystemExit("data/raw/f1c/*.csv がありません（教員が Web 画面から取得する。docs/dataset_sources.md）。")
    records = [r for f in files for r in read_any(f)]
    headers = list(records[0].keys()) if records else []
    columns = {}
    for name, cands in CANDIDATES.items():
        found = next((c for c in cands if c in headers), None)
        if found is None and name in REQUIRED:
            raise SystemExit(f"必須の列 {name} が見つかりません。見出し: {headers}")
        columns[name] = found
    out, skipped = [], 0
    for i, r in enumerate(records, start=1):
        price = re.sub(r"[,\s]", "", r[columns["trade_price_yen"]] or "")
        area = re.sub(r"[,\s]", "", r[columns["floor_area_m2"]] or "")
        if not price.isdigit() or not re.fullmatch(r"\d+(\.\d+)?", area):
            skipped += 1             # 空欄、または「2000㎡以上」のような数値でない値
            continue
        out.append({"record_id": f"R{len(out) + 1:04d}", "price": round(int(price) / 10000, 1),
                    "floor_area": float(area), "period": r[columns["period"]],
                    "municipality": r[columns["municipality"]],
                    "district": r[columns["district"]] if columns["district"] else "",
                    "property_type": r[columns["property_type"]],
                    "building_year": r[columns["building_year"]] if columns["building_year"] else "",
                    "source": "reinfolib_transaction_price"})
    print(f"読み込み {len(records)} 件、除外 {skipped} 件")
    write_csv("f1c/housing_prices_small.csv", list(out[0].keys()) if out else ["record_id"], out)


if __name__ == "__main__":
    sys.exit(main())
