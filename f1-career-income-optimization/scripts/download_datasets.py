"""【教員用】公開統計の原データ（Excel）を e-Stat の公式ファイルダウンロードから取得する

- 保存先：data/raw/<テーマ>/（Git 管理外。学生に配布しない）
- e-Stat の「ファイル」画面にあるダウンロードリンク（登録不要）と同じ URL を使う。API（要登録）は使わない。
- 取得前に HEAD でファイル容量を確かめ、1 ファイル 10MB を超えるものは取得しない（教員の承認が必要）。
- 取得後に SHA-256 と容量を data/raw/download_log.csv に記録する。既にあるファイルは取得し直さない（--force で再取得）。
- 不動産情報ライブラリの取引価格 CSV は Web 画面の操作で教員が取得する（docs/dataset_sources.md）。このスクリプトでは取得しない。
- 標準ライブラリだけで動く。

使い方（f1-career-income-optimization ディレクトリで）:
    python3 scripts/download_datasets.py            # すべて取得
    python3 scripts/download_datasets.py --list     # 取得対象の一覧だけ表示
"""

import argparse
import csv
import datetime
import hashlib
import sys
import urllib.request
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
MAX_BYTES = 10 * 1024 * 1024
DOWNLOAD_URL = "https://www.e-stat.go.jp/stat-search/file-download?statInfId={id}&fileKind={kind}"
USER_AGENT = "educational-material-preparation (python urllib)"

SOURCES = [
    {"theme": "f1a", "file": "wage_census_2025_education_age.xlsx", "stat_inf_id": "000040420843", "kind": 4,
     "survey": "賃金構造基本統計調査（令和7年）", "agency": "厚生労働省",
     "table": "一般労働者 産業大分類：学歴、年齢階級別きまって支給する現金給与額、所定内給与額及び年間賞与その他特別給与額（産業計・産業別）"},
    {"theme": "f1b", "file": "family_income_expenditure_2025_age.xlsx", "stat_inf_id": "000040409533", "kind": 0,
     "survey": "家計調査（家計収支編）2025年", "agency": "総務省統計局",
     "table": "二人以上の世帯 詳細結果表 年次：世帯主の年齢階級別 二人以上の世帯・勤労者世帯・無職世帯"},
    {"theme": "f1d", "file": "household_assets_2024_age.xlsx", "stat_inf_id": "000040488257", "kind": 0,
     "survey": "全国家計構造調査（令和6年）", "agency": "総務省統計局",
     "table": "表番号4-4 世帯の種類，世帯区分，世帯主の性別，世帯主の年齢階級，資産・負債の種類別1世帯当たり資産現在高・負債現在高－全国"},
    {"theme": "f1d", "file": "learning_cost_2023_school_type.xlsx", "stat_inf_id": "000040233659", "kind": 0,
     "survey": "子供の学習費調査（令和5年度）", "agency": "文部科学省",
     "table": "1 学校種別の学習費"},
]


def url_of(src):
    return DOWNLOAD_URL.format(id=src["stat_inf_id"], kind=src["kind"])


def request(url, method="GET"):
    req = urllib.request.Request(url, method=method, headers={"User-Agent": USER_AGENT})
    return urllib.request.urlopen(req, timeout=60)


def download(src, force=False):
    path = RAW_DIR / src["theme"] / src["file"]
    if path.exists() and not force:
        print(f"取得済み: {path.relative_to(PROJECT_DIR)}")
        return path
    with request(url_of(src), "HEAD") as r:
        size = int(r.headers.get("Content-Length", "0"))
    if size > MAX_BYTES:
        raise SystemExit(f"{src['file']} は {size:,} バイトで 10MB を超えます。教員の承認を得てから取得してください。")
    with request(url_of(src)) as r:
        data = r.read()
    if len(data) > MAX_BYTES or not data.startswith(b"PK"):
        raise SystemExit(f"{src['file']}：Excel（xlsx）ではない応答です（{len(data):,} バイト）。")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)
    log = RAW_DIR / "download_log.csv"
    new = not log.exists()
    with open(log, "a", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        if new:
            w.writerow(["file", "url", "bytes", "sha256", "downloaded_at", "survey", "table"])
        w.writerow([f"{src['theme']}/{src['file']}", url_of(src), len(data), hashlib.sha256(data).hexdigest(),
                    datetime.datetime.now().isoformat(timespec="seconds"), src["survey"], src["table"]])
    print(f"取得: {path.relative_to(PROJECT_DIR)}（{len(data):,} バイト）")
    return path


def main():
    parser = argparse.ArgumentParser(description="公開統計の原データの取得（e-Stat）")
    parser.add_argument("--list", action="store_true")
    parser.add_argument("--force", action="store_true")
    args = parser.parse_args()
    for src in SOURCES:
        if args.list:
            print(src["theme"], src["file"], url_of(src), src["survey"], src["table"], sep="\n  ")
        else:
            download(src, args.force)
    return 0


if __name__ == "__main__":
    sys.exit(main())
