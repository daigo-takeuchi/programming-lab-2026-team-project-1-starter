"""C-1 教材用 CSV のデータ品質検証スクリプト

data/ 以下の CSV について、次の項目を確認し、結果を Markdown 形式で表示する。
  - UTF-8 で読めるか
  - 期待するカラムがそろっているか（順序も含む）
  - 空欄（欠損値）がないか
  - ID 列に重複がないか
  - 数値列が整数として読めるか
  - timestamp 列が ISO 8601 形式として読めるか
  - label 列の値が定義済みの値か
  - 表計算ソフトで数式として解釈される文字（= + - @）で始まるセルがないか
  - ファイル容量

使い方（c1-web-attack-detection ディレクトリで実行する）:
    python3 scripts/validate_datasets.py                 # 結果を表示する
    python3 scripts/validate_datasets.py --output docs/x.md   # 結果をファイルにも保存する

存在しないファイル（例：Phase 2 で作る Small Dataset）は「未作成」と表示し、エラーにはしない。
"""

import argparse
import csv
import re
import sys
from datetime import datetime
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"

# ファイルごとの仕様：カラム、ID 列、整数列、ラベルとして許す値
SPECS = {
    "c1a/network_flows_tiny.csv": {
        "columns": ["record_id", "timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
                    "protocol", "packet_count", "byte_count", "label"],
        "id": "record_id",
        "int": ["record_id", "src_port", "dst_port", "packet_count", "byte_count"],
        "labels": {"benign", "portscan", "dos"},
    },
    "c1b/authentication_tiny.csv": {
        "columns": ["record_id", "timestamp", "user_id", "src_host", "dst_host",
                    "auth_type", "result", "label"],
        "id": "record_id",
        "int": ["record_id"],
        "labels": {"benign", "bruteforce", "spraying"},
        "allowed": {"result": {"success", "failure"}},
    },
    "c1c/http_requests_tiny.csv": {
        "columns": ["request_id", "timestamp", "src_ip", "method", "url", "status", "label"],
        "id": "request_id",
        "int": ["request_id", "status"],
        "labels": {"benign", "sqli", "xss", "traversal", "long_url", "scan"},
    },
    "c1d/file_states_before_tiny.csv": {
        "columns": ["file_id", "hash"], "id": "file_id", "int": [], "labels": None,
    },
    "c1d/file_states_after_tiny.csv": {
        "columns": ["file_id", "hash"], "id": "file_id", "int": [], "labels": None,
    },
    "c1e/data_transfer_tiny.csv": {
        "columns": ["record_id", "timestamp", "src_host", "dst_host", "byte_count", "label"],
        "id": "record_id",
        "int": ["record_id", "byte_count"],
        "labels": {"benign", "exfiltration"},
    },
}

# ---- Phase 2A で追加した CSV ----
# "optional"：空欄を許す列（原データに値がない場合）。"public"：公開データ由来（数式に見える値は警告にとどめる）
LOG_COLUMNS = ["record_id", "source_line", "log_date", "log_time"]
SPECS.update({
    "c1b/authentication_small.csv": {
        "columns": LOG_COLUMNS + ["user_id", "src_host", "dst_host", "auth_type", "result",
                                  "invalid_user", "repeat_count", "event_type", "message", "label"],
        "id": "record_id", "int": ["record_id", "source_line", "repeat_count"],
        "labels": {"unknown"}, "public": True,
        "allowed": {"result": {"success", "failure"}, "invalid_user": {"yes", "no"},
                    "auth_type": {"password", "none"}},
    },
    "c1b/ssh_events_small.csv": {
        "columns": LOG_COLUMNS + ["host_id", "process_name", "pid", "event_id", "event_type",
                                  "message", "label"],
        "id": "record_id", "int": ["record_id", "source_line"], "labels": {"unknown"}, "public": True,
    },
    "c1c/web_access_log_synthetic.csv": {
        "columns": ["request_id", "source_line", "timestamp", "src_ip", "method", "url", "status",
                    "response_bytes", "scenario"],
        "id": "request_id", "int": ["request_id", "source_line", "status"], "labels": None,
        "optional": ["response_bytes"],
        "allowed": {"scenario": {"normal", "access_concentration", "error_404_concentration"}},
    },
    "c1d/system_events_small.csv": {
        "columns": LOG_COLUMNS + ["host_id", "process_name", "pid", "event_id", "event_type",
                                  "message", "label"],
        "id": "record_id", "int": ["record_id", "source_line"], "labels": {"unknown"}, "public": True,
        "optional": ["pid"],
    },
})

# まだ作成していないファイル（存在しなくてもエラーにしない）
PLANNED = [
    "c1a/network_flows_small.csv",   # Phase 2B（CIC-IDS2017）
    "c1e/data_transfer_small.csv",   # Phase 2B（CIC-IDS2017）
]

FORMULA_PREFIXES = ("=", "+", "-", "@")


def validate_file(rel_path, spec):
    """1 つの CSV を検証し、(件数, 問題のリスト, 警告のリスト) を返す"""
    path = DATA_DIR / rel_path
    problems, warnings = [], []
    try:
        with open(path, encoding="utf-8", newline="") as f:
            reader = csv.DictReader(f)
            header = reader.fieldnames or []
            rows = list(reader)
    except UnicodeDecodeError:
        return 0, ["UTF-8 として読めない"], []

    if header != spec["columns"]:
        problems.append(f"カラムが仕様と異なる: {header}")
        return len(rows), problems, warnings
    if not rows:
        problems.append("データが 0 件")

    seen_ids = set()
    optional = set(spec.get("optional", []))
    for line_no, row in enumerate(rows, start=2):   # 1 行目はヘッダー
        for column in spec["columns"]:
            value = row[column]
            if value is None or value == "":
                if column not in optional:
                    problems.append(f"{line_no} 行目: {column} が空欄")
            elif value.startswith(FORMULA_PREFIXES):
                message = f"{line_no} 行目: {column} の値 {value[:20]!r} が数式として解釈されうる文字で始まる"
                (warnings if spec.get("public") else problems).append(message)
        if "log_date" in row:
            if not re.fullmatch(r"(0[1-9]|1[0-2])-(0[1-9]|[12]\d|3[01])", row["log_date"]):
                problems.append(f"{line_no} 行目: log_date が MM-DD 形式ではない")
            if not re.fullmatch(r"([01]\d|2[0-3]):[0-5]\d:[0-5]\d", row["log_time"]):
                problems.append(f"{line_no} 行目: log_time が HH:MM:SS 形式ではない")
        row_id = row[spec["id"]]
        if row_id in seen_ids:
            problems.append(f"{line_no} 行目: ID {row_id} が重複")
        seen_ids.add(row_id)
        for column in spec["int"]:
            try:
                int(row[column])
            except (TypeError, ValueError):
                problems.append(f"{line_no} 行目: {column} が整数ではない")
        if "timestamp" in row:
            try:
                datetime.fromisoformat(row["timestamp"])
            except (TypeError, ValueError):
                problems.append(f"{line_no} 行目: timestamp が ISO 8601 形式ではない")
        if spec["labels"] is not None and row["label"] not in spec["labels"]:
            problems.append(f"{line_no} 行目: 未定義のラベル {row['label']!r}")
        for column, allowed in spec.get("allowed", {}).items():
            if row[column] not in allowed:
                problems.append(f"{line_no} 行目: {column} の値 {row[column]!r} が未定義")
    return len(rows), problems, warnings


def build_report():
    """検証結果の Markdown と、問題があったかどうかを返す"""
    lines = ["| ファイル | 件数 | 容量 | 結果 |", "| --- | ---: | ---: | --- |"]
    details = []
    has_problem = False
    for rel_path, spec in SPECS.items():
        path = DATA_DIR / rel_path
        if not path.exists():
            lines.append(f"| `data/{rel_path}` | - | - | **ファイルなし** |")
            has_problem = True
            continue
        count, problems, warnings = validate_file(rel_path, spec)
        size = path.stat().st_size
        result = "OK" if not problems else f"問題 {len(problems)} 件"
        if warnings:
            result += f"（警告 {len(warnings)} 件）"
            details.append(f"### data/{rel_path}（警告：原データの値のため変更していない）")
            details.extend(f"- {w}" for w in warnings[:20])
        lines.append(f"| `data/{rel_path}` | {count} | {size:,} B | {result} |")
        if problems:
            has_problem = True
            details.append(f"### data/{rel_path}")
            details.extend(f"- {p}" for p in problems[:20])
    for rel_path in PLANNED:
        status = "存在する（検証項目を追加すること）" if (DATA_DIR / rel_path).exists() else "未作成（Phase 2B 予定）"
        lines.append(f"| `data/{rel_path}` | - | - | {status} |")
    report = "\n".join(lines)
    if details:
        report += "\n\n" + "\n".join(details)
    return report, has_problem


def main():
    parser = argparse.ArgumentParser(description="C-1 教材用 CSV のデータ品質検証")
    parser.add_argument("--output", help="検証結果を保存する Markdown ファイル")
    args = parser.parse_args()
    report, has_problem = build_report()
    print(report)
    if args.output:
        Path(args.output).write_text(report + "\n", encoding="utf-8")
    sys.exit(1 if has_problem else 0)


if __name__ == "__main__":
    main()
