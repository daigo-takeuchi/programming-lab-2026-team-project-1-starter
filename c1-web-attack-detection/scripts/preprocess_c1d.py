"""C-1D の前処理：Loghub Linux_2k → 教育用 CSV（教員用）

入力（data/raw/loghub/、Git 管理外）:
    Linux_2k.log_structured.csv（Loghub の構造化版）、Linux_2k.log（生ログ。内容の一致を確認する）

出力:
    data/c1d/system_events_small.csv   Linux サーバーのシステムログ 2,000 行
    data/c1d/LICENSE_LOGHUB.txt        Loghub のライセンス文
    data/raw/loghub/anonymization_map_c1d.csv  匿名化の対応表（Git 管理外。配布しない）

方針:
- 原データは、Public Security Log Sharing Site（Anton Chuvakin 氏）で公開された実サーバーの
  /var/log/messages を、Loghub が再配布したもの。正解ラベルはない（label = "unknown"）。
- **ファイルの変更やランサムウェアの記録・ラベルは含まれない。** C-1D の基本課題（ファイル状態の比較）
  は人工データで行い、このログは発展課題（プロセス別・イベント別の集計など）だけに使う。2 つを統合しない。
- event_type は、メッセージの文言に対する下の RULES（上から順に最初に一致したもの）で決める。
  攻撃かどうかの判定ではなく、「どんな種類の記録か」の大まかな分類である。
- 原データに年がないため、log_date（MM-DD）と log_time（HH:MM:SS）に分け、年を付けない。
- 行の順序は原データのまま（syslog の書き込み順）。時刻が前後している箇所が 3 か所あるが、並べ替えない。
- 同じ内容の行が続く場合も、実際に繰り返し記録されたイベントなので削除しない。
- IP アドレス・ドメイン名は匿名 ID にする。ユーザー名（root、guest、test、cyrus、news）は
  システム用・汎用のアカウント名なので、そのまま残す。
- process_name は Loghub の Component をそのまま使う（例：sshd(pam_unix)）。"-- root" という値が 1 件あり、
  表計算ソフトでは数式と誤解されるおそれがある（validate_datasets.py で警告として表示する）。
"""

import argparse
import csv
import re
import sys

from preprocess_common import (DATA_DIR, RAW_DIR, Anonymizer, check_or_write, log_date,
                               require, to_csv_text)

RAW = RAW_DIR / "loghub"
# ドメイン名に見えるが、ホスト名ではない文字列（プロセス名・公開されたビルドサーバー名）は匿名化しない
NOT_HOSTS = {"rpc.statd", "rpc.idmapd", "bugs.build.redhat.com"}

# (正規表現, event_type)。上から順に調べ、最初に一致したものを使う。
RULES = [
    (r"session opened for user", "session_opened"),
    (r"session closed for user", "session_closed"),
    (r"check pass; user unknown", "auth_unknown_user"),
    (r"authentication failure|Authentication failed|Kerberos authentication failed|"
     r"Couldn't authenticate", "auth_failure"),
    (r"ANONYMOUS FTP LOGIN", "ftp_anonymous_login"),
    (r"ROOT LOGIN", "root_login"),
    (r"^connection from", "ftp_connection"),
    (r"exited abnormally", "process_error"),
    (r"startup succeeded|^restart\.?$|started\.?$", "service_start"),
    (r"shutdown succeeded", "service_stop"),
]
COLUMNS = ["record_id", "source_line", "log_date", "log_time", "host_id", "process_name", "pid",
           "event_id", "event_type", "message", "label"]


def classify(component, content):
    for pattern, event_type in RULES:
        if re.search(pattern, content.strip()):
            return event_type
    return "kernel_message" if component == "kernel" else "other"


def load_rows():
    with open(require(RAW / "Linux_2k.log_structured.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    raw_lines = require(RAW / "Linux_2k.log").read_text(encoding="utf-8").splitlines()
    if len(rows) != len(raw_lines):
        raise SystemExit("構造化版と生ログの行数が一致しません")
    for row, line in zip(rows, raw_lines):
        if row["Content"].strip() not in line:
            raise SystemExit(f"{row['LineId']} 行目：構造化版と生ログの内容が一致しません")
    return rows


def build(rows):
    anon = Anonymizer()
    out = []
    for row in rows:
        out.append({
            "record_id": len(out) + 1, "source_line": int(row["LineId"]),
            "log_date": log_date(row["Month"], row["Date"]), "log_time": row["Time"],
            "host_id": row["Level"],          # Loghub の Level 列には、このログではホスト名（combo）が入っている
            "process_name": row["Component"], "pid": row["PID"], "event_id": row["EventId"],
            "event_type": classify(row["Component"], row["Content"]),
            "message": anon.text(row["Content"].strip(), keep_hosts=NOT_HOSTS), "label": "unknown",
        })
    return out, anon


def main():
    parser = argparse.ArgumentParser(description="C-1D 前処理（Loghub Linux_2k）")
    parser.add_argument("--check", action="store_true", help="既存の CSV が再生成結果と一致するか確認する")
    args = parser.parse_args()

    rows, anon = build(load_rows())
    outputs = {
        DATA_DIR / "c1d" / "system_events_small.csv": to_csv_text(COLUMNS, rows),
        DATA_DIR / "c1d" / "LICENSE_LOGHUB.txt": (RAW / "LICENSE").read_text(encoding="utf-8"),
    }
    mismatched = check_or_write(outputs, args.check)
    if args.check:
        if mismatched:
            print("再生成結果と一致しないファイル:", ", ".join(mismatched))
            sys.exit(1)
        print("OK: C-1D の出力は再生成結果と一致しました。")
        return
    map_text = to_csv_text(["kind", "anonymized", "original"], list(anon.mapping_rows()))
    (RAW / "anonymization_map_c1d.csv").write_text(map_text, encoding="utf-8")
    counts = {}
    for r in rows:
        counts[r["event_type"]] = counts.get(r["event_type"], 0) + 1
    print("event_type 別の件数:", dict(sorted(counts.items(), key=lambda kv: -kv[1])))
    print(f"匿名化：IP {len(anon.maps['ip'])} 個、ホスト名 {len(anon.maps['host'])} 個")


if __name__ == "__main__":
    main()
