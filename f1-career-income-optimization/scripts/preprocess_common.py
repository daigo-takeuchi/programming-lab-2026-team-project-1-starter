"""【教員用】前処理スクリプトの共通関数（標準ライブラリのみ）

方針（docs/preprocessing_policy.md）:
- 欠損・秘匿・該当なしの記号（「－」「…」「...」「x」「*」など）は**空欄**にする。0 に置き換えない。
- 金額は万円にそろえる。月額と年額は別の列にし、年額を作るための計算（月額 × 12 など）はしない（学生が行う）。
- 原データの名称（学歴・年齢階級・項目名）は日本語のまま残し、ID・列名は英語にする。
"""

import csv
import re
import sys
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
RAW_DIR = PROJECT_DIR / "data" / "raw"
DATA_DIR = PROJECT_DIR / "data"
sys.path.insert(0, str(Path(__file__).resolve().parent))

from xlsx_reader import read_xlsx  # noqa: E402

MISSING_MARKS = {"", "－", "-", "―", "…", "...", "x", "X", "*", "***", "…　"}


def clean_label(text):
    """セルの見出しから、ふりがな（カタカナの読み）・改行・余分な空白を取り除く"""
    text = text.replace("\n", "").replace("　", "").strip()
    # 見出しの後ろに付いているカタカナの読み（例：「大学ダイガク」→「大学」）を取り除く
    text = re.sub(r"(?<=[^゠-ヿ])[゠-ヿ]+$", "", text)
    return text.strip()


def to_number(text):
    """数値の文字列を float にする。欠損・秘匿の記号は None（空欄）"""
    s = str(text).strip().replace(",", "")
    if s in MISSING_MARKS:
        return None
    return float(s)


def scaled(value, divisor, digits):
    """単位の変換（例：千円 → 万円は 10 で割る）。None はそのまま"""
    if value is None:
        return None
    return round(value / divisor, digits)


def fmt(value):
    """CSV に書く文字列。None は空欄、整数になる値は整数で書く"""
    if value is None:
        return ""
    if isinstance(value, float) and value.is_integer():
        return str(int(value))
    return str(value)


def write_csv(rel_path, columns, rows):
    path = DATA_DIR / rel_path
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f, lineterminator="\n")
        w.writerow(columns)
        for r in rows:
            w.writerow([fmt(r[c]) for c in columns])
    print(f"作成: data/{rel_path}（{len(rows)} 行、{len(columns)} 列）")
    return path


def require_raw(rel_path):
    path = RAW_DIR / rel_path
    if not path.exists():
        raise SystemExit(f"原データ data/raw/{rel_path} がありません。先に scripts/download_datasets.py を実行してください。")
    return path
