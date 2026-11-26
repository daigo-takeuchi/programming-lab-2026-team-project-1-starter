"""前処理スクリプト（preprocess_c1x.py）の共通部品（教員用）

- Anonymizer：IP アドレス・ホスト名・ユーザー名を、一貫した匿名 ID に置き換える
- write_csv / check_or_write：CSV の書き出しと、再生成結果との一致確認
- syslog の日時（年なし）の変換

方針は docs/preprocessing_policy.md を参照。
"""

import csv
import io
import re
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"
RAW_DIR = DATA_DIR / "raw"

MONTHS = {m: i for i, m in enumerate(
    ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"], start=1)}

IPV4 = re.compile(r"(?<![\d.])(?:\d{1,3}\.){3}\d{1,3}(?![\d.])")
# ドメイン名らしい文字列（英字の TLD で終わる、2 つ以上のラベル）
FQDN = re.compile(r"(?<![\w.-])(?:[A-Za-z0-9-]+\.)+[A-Za-z]{2,}(?![\w-])")


def log_date(month_name, day):
    """syslog の「月名・日」を "MM-DD" にする。原データに年がないため、年は付けない。"""
    return f"{MONTHS[month_name]:02d}-{int(day):02d}"


class Anonymizer:
    """同じ値には同じ匿名 ID を割り当てる（初めて出てきた順に 001, 002, ...）"""

    def __init__(self):
        self.maps = {"ip": {}, "host": {}, "user": {}}

    def get(self, kind, value):
        table = self.maps[kind]
        if value not in table:
            table[value] = f"{kind}-{len(table) + 1:03d}"
        return table[value]

    def ip(self, value):
        return self.get("ip", value)

    def user(self, value):
        return self.get("user", value)

    def text(self, message, keep_hosts=()):
        """メッセージ中の IPv4 アドレスとドメイン名を匿名 ID に置き換える"""
        message = IPV4.sub(lambda m: self.ip(m.group(0)), message)

        def replace_host(m):
            name = m.group(0)
            return name if name in keep_hosts else self.get("host", name)
        return FQDN.sub(replace_host, message)

    def mapping_rows(self):
        for kind, table in self.maps.items():
            for original, anon in table.items():
                yield {"kind": kind, "anonymized": anon, "original": original}


def to_csv_text(columns, rows):
    buffer = io.StringIO()
    writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def check_or_write(outputs, check):
    """outputs = {Path: CSV文字列}。check=True なら既存ファイルとの一致だけを確認する。

    戻り値：一致しなかったファイルのリスト（check=False のときは空）
    """
    mismatched = []
    for path, text in outputs.items():
        rel = path.relative_to(PROJECT_DIR)
        if check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                mismatched.append(str(rel))
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        count = f"{text.count(chr(10)) - 1} 件、" if path.suffix == ".csv" else ""
        print(f"作成: {rel}（{count}{len(text.encode('utf-8')):,} バイト）")
    return mismatched


def require(path):
    if not path.exists():
        raise SystemExit(f"原データがありません: {path.relative_to(PROJECT_DIR)}\n"
                         "先に python3 scripts/download_datasets.py を実行してください。")
    return path
