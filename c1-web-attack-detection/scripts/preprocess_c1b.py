"""C-1B の前処理：Loghub OpenSSH_2k → 教育用 CSV（教員用）

入力（data/raw/loghub/、Git 管理外。scripts/download_datasets.py で取得）:
    OpenSSH_2k.log_structured.csv（Loghub が配布する構造化版。EventId と EventTemplate は Loghub の解析結果）
    OpenSSH_2k.log（生ログ。構造化版の Content と一致することを確認する）

出力:
    data/c1b/authentication_small.csv  認証の試行（成功・失敗）を表す行だけ（1 行 = 1 回の試行の記録）
    data/c1b/ssh_events_small.csv      sshd の全イベント（2,000 行）とイベントの種類
    data/c1b/LICENSE_LOGHUB.txt        Loghub のライセンス文（全コピーへの同梱が条件）
    data/raw/loghub/anonymization_map_c1b.csv  匿名化の対応表（Git 管理外。配布しない）

方針:
- 原データは実際のサーバーのログで、正解ラベルはない。label 列はすべて "unknown"。
- result（success / failure）は認証の結果であり、攻撃かどうかの正解ではない。
- 成功・失敗の比率は調整しない。人工データを混ぜない。
- 1 回の認証試行は、sshd の "Failed password ..." 行と pam_unix の "authentication failure" 行など、
  複数の行に記録される。二重に数えないよう、authentication_small.csv には sshd の試行行
  （Loghub の EventId E1・E8・E9・E10・E14）だけを入れる。
- "message repeated N times: [ Failed password ... ]"（E14）は、syslog が同じメッセージを
  まとめた行である。行は 1 つのまま残し、repeat_count に N を記録する（行を増やさない）。
- 原データに年がないため、日付は log_date（MM-DD）と log_time（HH:MM:SS）に分けて記録し、年を付けない。
- IP アドレス・ドメイン名は ip-001 / host-001 のような一貫した匿名 ID にする。
  ユーザー名は、ログイン成功・セッションの記録がある実在アカウント（このログでは 1 件）だけを user-001 にする。
  攻撃者が試したユーザー名（root、admin など）は個人を特定しないため、そのまま残す。

使い方（c1-web-attack-detection ディレクトリで実行する）:
    python3 scripts/preprocess_c1b.py           # CSV を作る
    python3 scripts/preprocess_c1b.py --check   # 既存の CSV が再生成結果と一致するか確認する
"""

import argparse
import csv
import re
import sys

from preprocess_common import (DATA_DIR, RAW_DIR, Anonymizer, check_or_write, log_date,
                               require, to_csv_text)

RAW = RAW_DIR / "loghub"
# ドメイン名に見えるが、ホスト名ではない文字列（Java の例外クラス名）は匿名化しない
NOT_HOSTS = {"com.jcraft.jsch.JSchException"}
SERVER = "LabSZ"   # ログに記録されたサーバー名（研究室のサーバー。個人情報ではない）

# 認証の試行を表す行（EventId → event_type, auth_type, result）
ATTEMPT_EVENTS = {
    "E1": ("accepted_password", "password", "success"),
    "E8": ("failed_none_invalid_user", "none", "failure"),
    "E9": ("failed_password", "password", "failure"),
    "E10": ("failed_password_invalid_user", "password", "failure"),
    "E14": ("failed_password_repeated", "password", "failure"),
}
ATTEMPT = re.compile(
    r"(?:message repeated (?P<repeat>\d+) times: \[ )?"
    r"(?:Accepted|Failed) (?:password|none) for (?P<invalid>invalid user )?(?P<user>.*?) "
    r"from (?P<ip>[\d.]+) port \d+ ssh2")
# 注意：試行されたユーザー名には空白で始まるもの（例：" 0101"）もある。原データのまま残す。

# sshd の全イベントの大まかな分類（Loghub の EventId ごと）
EVENT_TYPES = {
    "E1": "auth_success", "E8": "auth_failure", "E9": "auth_failure", "E10": "auth_failure",
    "E14": "auth_failure",
    "E15": "pam_auth_failure", "E16": "pam_auth_failure", "E17": "pam_auth_failure",
    "E19": "pam_auth_failure", "E20": "pam_auth_failure", "E21": "pam_unknown_user",
    "E18": "max_retries", "E4": "too_many_failures", "E5": "too_many_failures",
    "E12": "invalid_user", "E13": "invalid_user",
    "E27": "reverse_dns_failed",
    "E2": "disconnect", "E3": "disconnect", "E6": "disconnect", "E7": "disconnect",
    "E11": "disconnect", "E24": "disconnect", "E25": "disconnect", "E26": "disconnect",
    "E22": "session_closed", "E23": "session_opened",
}

AUTH_COLUMNS = ["record_id", "source_line", "log_date", "log_time", "user_id", "src_host", "dst_host",
                "auth_type", "result", "invalid_user", "repeat_count", "event_type", "message", "label"]
EVENT_COLUMNS = ["record_id", "source_line", "log_date", "log_time", "host_id", "process_name", "pid",
                 "event_id", "event_type", "message", "label"]


def load_rows():
    with open(require(RAW / "OpenSSH_2k.log_structured.csv"), encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))
    raw_lines = require(RAW / "OpenSSH_2k.log").read_text(encoding="utf-8").splitlines()
    if len(rows) != len(raw_lines):
        raise SystemExit("構造化版と生ログの行数が一致しません")
    for row, line in zip(rows, raw_lines):
        if not line.rstrip().endswith(row["Content"].rstrip()):
            raise SystemExit(f"{row['LineId']} 行目：構造化版と生ログの内容が一致しません")
    return rows


def build(rows):
    anon = Anonymizer()
    # 実在アカウント（成功・セッションの記録があるユーザー）を先に調べる
    real_users = set()
    for row in rows:
        m = re.search(r"(?:Accepted \S+ for|session (?:opened|closed) for user) (\S+)", row["Content"])
        if m:
            real_users.add(m.group(1))

    def user_label(name):
        return anon.user(name) if name in real_users else name

    def clean(message):
        message = anon.text(message, keep_hosts=NOT_HOSTS)
        for name in real_users:
            message = re.sub(rf"\b{re.escape(name)}\b", anon.user(name), message)
        return message

    auth_rows, event_rows = [], []
    for row in rows:
        date = log_date(row["Date"], row["Day"])
        message = clean(row["Content"])
        event_rows.append({
            "record_id": len(event_rows) + 1, "source_line": int(row["LineId"]),
            "log_date": date, "log_time": row["Time"], "host_id": SERVER,
            "process_name": "sshd", "pid": row["Pid"], "event_id": row["EventId"],
            "event_type": EVENT_TYPES.get(row["EventId"], "other"), "message": message,
            "label": "unknown",
        })
        if row["EventId"] not in ATTEMPT_EVENTS:
            continue
        m = ATTEMPT.search(row["Content"])
        if m is None:
            raise SystemExit(f"{row['LineId']} 行目：認証試行の形式を解析できません: {row['Content']}")
        event_type, auth_type, result = ATTEMPT_EVENTS[row["EventId"]]
        auth_rows.append({
            "record_id": len(auth_rows) + 1, "source_line": int(row["LineId"]),
            "log_date": date, "log_time": row["Time"],
            "user_id": user_label(m.group("user")), "src_host": anon.ip(m.group("ip")),
            "dst_host": SERVER, "auth_type": auth_type, "result": result,
            "invalid_user": "yes" if m.group("invalid") else "no",
            "repeat_count": int(m.group("repeat") or 1),
            "event_type": event_type, "message": message, "label": "unknown",
        })
    return auth_rows, event_rows, anon


def main():
    parser = argparse.ArgumentParser(description="C-1B 前処理（Loghub OpenSSH_2k）")
    parser.add_argument("--check", action="store_true", help="既存の CSV が再生成結果と一致するか確認する")
    args = parser.parse_args()

    auth_rows, event_rows, anon = build(load_rows())
    outputs = {
        DATA_DIR / "c1b" / "authentication_small.csv": to_csv_text(AUTH_COLUMNS, auth_rows),
        DATA_DIR / "c1b" / "ssh_events_small.csv": to_csv_text(EVENT_COLUMNS, event_rows),
        DATA_DIR / "c1b" / "LICENSE_LOGHUB.txt": (RAW / "LICENSE").read_text(encoding="utf-8"),
    }
    mismatched = check_or_write(outputs, args.check)
    if args.check:
        if mismatched:
            print("再生成結果と一致しないファイル:", ", ".join(mismatched))
            sys.exit(1)
        print("OK: C-1B の出力は再生成結果と一致しました。")
        return
    map_text = to_csv_text(["kind", "anonymized", "original"], list(anon.mapping_rows()))
    (RAW / "anonymization_map_c1b.csv").write_text(map_text, encoding="utf-8")

    failures = sum(r["result"] == "failure" for r in auth_rows)
    print(f"認証の試行 {len(auth_rows)} 行（成功 {len(auth_rows) - failures}、失敗 {failures}）、"
          f"repeat_count の合計 {sum(r['repeat_count'] for r in auth_rows)}")
    print(f"匿名化：IP {len(anon.maps['ip'])} 個、ホスト名 {len(anon.maps['host'])} 個、"
          f"ユーザー {len(anon.maps['user'])} 個")


if __name__ == "__main__":
    main()
