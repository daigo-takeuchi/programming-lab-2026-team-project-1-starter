"""C-1C の前処理：旧 C1 教材の人工アクセスログ → 教育用 CSV（教員用）

入力:  data/sample_access.log（旧 C1 教材のために教員が作成した**人工データ**。48 行）
出力:  data/c1c/web_access_log_synthetic.csv

- 公開データではないため、ファイル名に "synthetic" を付け、"_small"（公開データ由来）とは区別する。
- 読み込みには旧教材の log_parser.parse_line をそのまま使う（形式チェックを含む）。
  形式に合わない行（29 行目：ステータスコードが "-"）は出力せず、その行番号を表示する。
- scenario 列は、旧教材の README（docs/legacy/README_web_access_log.md「サンプルログ」の表）に
  記録された、作成者が IP アドレスごとに意図したパターンである。攻撃の正解ラベルではない。
    normal                    ：通常アクセス（パターン A。偶発的な 404 を含む）
    access_concentration      ：アクセス集中（パターン B）
    error_404_concentration   ：404 エラー集中（パターン C）
- response_bytes が空欄の行は、原ログのサイズが "-"（送信データなし）だったことを表す。
- IP アドレスはドキュメント用アドレス（RFC 5737）なので、匿名化しない。
- URL の長さ、IP 別の回数などの集計値は、学生が計算する課題なので含めない。

使い方:
    python3 scripts/preprocess_c1c.py           # CSV を作る
    python3 scripts/preprocess_c1c.py --check   # 既存の CSV が再生成結果と一致するか確認する
"""

import argparse
import sys

from preprocess_common import DATA_DIR, PROJECT_DIR, check_or_write, require, to_csv_text

sys.path.insert(0, str(PROJECT_DIR))
import log_parser  # noqa: E402  旧教材のパーサーを再利用する

SOURCE = DATA_DIR / "sample_access.log"
OUTPUT = DATA_DIR / "c1c" / "web_access_log_synthetic.csv"
SCENARIOS = {"203.0.113.50": "access_concentration", "198.51.100.66": "error_404_concentration"}
COLUMNS = ["request_id", "source_line", "timestamp", "src_ip", "method", "url", "status",
           "response_bytes", "scenario"]


def build():
    rows, invalid = [], []
    with open(require(SOURCE), encoding="utf-8") as f:
        for line_no, line in enumerate(f, start=1):
            if not line.strip():
                continue
            rec = log_parser.parse_line(line)
            if rec is None:
                invalid.append(line_no)
                continue
            rows.append({
                "request_id": len(rows) + 1, "source_line": line_no,
                "timestamp": rec["timestamp"].isoformat(), "src_ip": rec["ip"],
                "method": rec["method"], "url": rec["path"], "status": rec["status"],
                "response_bytes": "" if rec["size"] is None else rec["size"],
                "scenario": SCENARIOS.get(rec["ip"], "normal"),
            })
    return rows, invalid


def main():
    parser = argparse.ArgumentParser(description="C-1C 前処理（旧教材の人工アクセスログ）")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    rows, invalid = build()
    mismatched = check_or_write({OUTPUT: to_csv_text(COLUMNS, rows)}, args.check)
    if args.check:
        if mismatched:
            print("再生成結果と一致しないファイル:", ", ".join(mismatched))
            sys.exit(1)
        print("OK: C-1C の出力は再生成結果と一致しました。")
        return
    print(f"読み込めなかった行（出力しない）: {invalid}")


if __name__ == "__main__":
    main()
