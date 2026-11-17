# C1：アクセスログの読み込み
#
# ■ ログの形式（Apache Common Log Format に近い形式）
#   IPアドレス - - [日時] "メソッド パス プロトコル" ステータスコード サイズ
#
#   例：
#   192.0.2.10 - - [15/Nov/2026:10:00:01 +0900] "GET /index.html HTTP/1.1" 200 1024
#
#   - 日時は「日/月の英語略称/年:時:分:秒 タイムゾーン」
#   - サイズは整数、または送信データがないことを表す "-"
#
# ■ 読み込み結果
#   1行を、次のような辞書に変換する。
#   {"ip": "192.0.2.10", "timestamp": datetime(...), "method": "GET",
#    "path": "/index.html", "status": 200, "size": 1024}
#
#   形式に合わない行は、正常なデータとして扱わず、行番号と内容を別に記録する。

import ipaddress
import re
from datetime import datetime

# 1行のログを分解する正規表現
LOG_PATTERN = re.compile(
    r'^(?P<ip>\S+) \S+ \S+ '
    r'\[(?P<time>[^\]]+)\] '
    r'"(?P<method>[A-Z]+) (?P<path>\S+) (?P<protocol>[^"]+)" '
    r'(?P<status>\d{3}) '
    r'(?P<size>\d+|-)$'
)

TIME_FORMAT = "%d/%b/%Y:%H:%M:%S %z"


def parse_line(line):
    """ログ1行を辞書に変換する。形式が正しくない行は None を返す。"""
    match = LOG_PATTERN.match(line.strip())
    if match is None:
        return None

    try:
        ipaddress.ip_address(match["ip"])                       # IPアドレスとして正しいか
        timestamp = datetime.strptime(match["time"], TIME_FORMAT)
    except ValueError:
        return None

    size = match["size"]
    return {
        "ip": match["ip"],
        "timestamp": timestamp,
        "method": match["method"],
        "path": match["path"],
        "status": int(match["status"]),
        "size": None if size == "-" else int(size),
    }


def load_log(path):
    """ログファイルを読み込む。

    戻り値：(records, invalid_lines)
        records       : 正しく読み込めた行の辞書のリスト
        invalid_lines : 読み込めなかった行の (行番号, 行の内容) のリスト
    空行は無視する。
    """
    records = []
    invalid_lines = []
    with open(path, encoding="utf-8") as f:
        for line_number, line in enumerate(f, start=1):
            if line.strip() == "":
                continue
            record = parse_line(line)
            if record is None:
                invalid_lines.append((line_number, line.rstrip("\n")))
            else:
                records.append(record)
    return records, invalid_lines
