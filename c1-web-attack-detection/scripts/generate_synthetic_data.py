"""C-1 教材用の人工データ（Tiny Dataset）を生成するスクリプト

このスクリプトが作るデータは、すべて教材用に人工的に作ったものである。
実在のネットワーク・利用者・Webサイト・ファイルとは関係がない。

- IPアドレスは、ドキュメント用に予約されたアドレス（RFC 5737）だけを使う。
    192.0.2.0/24（社内の端末として使う）
    198.51.100.0/24（社内のサーバーとして使う）
    203.0.113.0/24（社外の通信先として使う）
- label 列は「教材として意図した役割」であり、実環境の攻撃ラベルではない。
- 乱数のシードを固定しているため、何度実行しても同じファイルができる。

使い方（c1-web-attack-detection ディレクトリで実行する）:
    python3 scripts/generate_synthetic_data.py           # data/ 以下の Tiny CSV を作り直す
    python3 scripts/generate_synthetic_data.py --check   # 既存ファイルが再生成結果と一致するか確認する

Benchmark Dataset（大量の人工データ）は、Phase 4 でこのスクリプトに関数を追加する予定。
"""

import argparse
import csv
import io
import random
import sys
from datetime import datetime, timedelta
from pathlib import Path

SEED = 2026
BASE_TIME = datetime(2026, 11, 20, 10, 0, 0)
PROJECT_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = PROJECT_DIR / "data"


def ts(seconds):
    """BASE_TIME から seconds 秒後の時刻を ISO 8601 形式の文字列で返す"""
    return (BASE_TIME + timedelta(seconds=seconds)).isoformat()


def sort_and_number(rows, id_column):
    """時刻順に並べ替え、1 から始まる連番の ID を振る"""
    rows.sort(key=lambda r: r["timestamp"])
    for i, row in enumerate(rows, start=1):
        row[id_column] = i
    return rows


# ----------------------------------------------------------------------
# C-1A：ネットワーク通信フロー
# ----------------------------------------------------------------------
def make_c1a(rng):
    web, files = "198.51.100.10", "198.51.100.20"
    rows = []

    def add(t, src, dst, dport, proto, packets, nbytes, label):
        rows.append({
            "timestamp": ts(t), "src_ip": src, "dst_ip": dst,
            "src_port": rng.randint(49152, 65535), "dst_port": dport,
            "protocol": proto, "packet_count": packets, "byte_count": nbytes,
            "label": label,
        })

    # 通常の利用：4台の端末が Web サーバー・ファイルサーバーに少しずつ接続する
    normal_plan = {
        "192.0.2.11": [(web, 443), (web, 443), (web, 80), (files, 445)],
        "192.0.2.12": [(web, 443), (files, 445), (web, 443)],
        "192.0.2.13": [(web, 80), (web, 443), (web, 443), (files, 445), (web, 443)],
        "192.0.2.14": [(web, 443), (web, 443), (files, 445), (web, 443), (web, 80),
                       (web, 443), (web, 443), (web, 443)],   # 境界例：通信回数がちょうど 8 回
    }
    for src, plan in normal_plan.items():
        for dst, dport in plan:
            add(rng.randint(0, 3600), src, dst, dport, "TCP",
                rng.randint(8, 40), rng.randint(2_000, 60_000), "benign")

    # ポートスキャン：1台が短時間に多数の異なるポートへ 1 パケットずつ接続する
    scan_ports = [21, 22, 23, 25, 53, 80, 110, 139, 143, 443, 445, 3389]
    for i, port in enumerate(scan_ports):
        add(1800 + i * 2, "192.0.2.15", files, port, "TCP", 1, 60, "portscan")

    # 通信集中（DoS の兆候を模したもの）：1台が短時間に同じポートへ大量に接続する
    for i in range(10):
        add(2400 + i, "192.0.2.16", web, 80, "TCP", rng.randint(2, 4), rng.randint(120, 300), "dos")

    columns = ["record_id", "timestamp", "src_ip", "dst_ip", "src_port", "dst_port",
               "protocol", "packet_count", "byte_count", "label"]
    return {"c1a/network_flows_tiny.csv": (columns, sort_and_number(rows, "record_id"))}


# ----------------------------------------------------------------------
# C-1B：認証ログ
# ----------------------------------------------------------------------
def make_c1b(rng):
    server = "198.51.100.30"
    rows = []

    def add(t, user, src, result, label, auth_type="password"):
        rows.append({
            "timestamp": ts(t), "user_id": user, "src_host": src, "dst_host": server,
            "auth_type": auth_type, "result": result, "label": label,
        })

    # 通常の利用者：ほとんど成功し、まれに入力ミスで 1〜2 回失敗する
    normal = {
        "user01": ("192.0.2.21", ["success", "success", "success"]),
        "user02": ("192.0.2.22", ["failure", "success", "success"]),          # 入力ミス 1 回
        "user03": ("192.0.2.23", ["success", "success"]),
        "user05": ("192.0.2.25", ["failure", "failure", "success", "success"]),  # 境界例：2 回失敗
        "user06": ("192.0.2.26", ["success", "success", "success"]),
    }
    for user, (src, results) in normal.items():
        t = rng.randint(0, 2400)
        for result in results:
            add(t, user, src, result, "benign")
            t += rng.randint(20, 900)

    # 総当たり（ブルートフォース）を模したもの：1 アカウントへの連続失敗の後に成功
    t = 3000
    for _ in range(8):
        add(t, "user04", "203.0.113.50", "failure", "bruteforce")
        t += 3
    add(t, "user04", "203.0.113.50", "success", "bruteforce")   # 失敗の後の成功（要注意）

    # パスワードスプレーを模したもの：1 つの接続元から多数のアカウントへ 1 回ずつ失敗
    for i, user in enumerate(["user01", "user02", "user03", "user05", "user06",
                              "user07", "user08", "admin"]):
        add(4000 + i * 5, user, "203.0.113.77", "failure", "spraying")

    columns = ["record_id", "timestamp", "user_id", "src_host", "dst_host",
               "auth_type", "result", "label"]
    return {"c1b/authentication_tiny.csv": (columns, sort_and_number(rows, "record_id"))}


# ----------------------------------------------------------------------
# C-1C：HTTP リクエスト
# ----------------------------------------------------------------------
def make_c1c(rng):
    # 注意：攻撃に似た文字列は「ただのテキスト」として保存しているだけである。
    #       この教材では、これらを実際の Web サイトへ送信したり、実行したりしない。
    benign = [
        ("GET", "/"), ("GET", "/index.html"), ("GET", "/products"),
        ("GET", "/products?id=12"), ("GET", "/products?id=31&sort=price"),
        ("GET", "/search?q=keyboard"), ("GET", "/search?q=usb+cable&page=2"),
        ("POST", "/login"), ("GET", "/cart"), ("POST", "/cart/add?id=12"),
        ("GET", "/news/2026-11"), ("GET", "/contact"), ("GET", "/about"),
        ("GET", "/images/logo.png"), ("GET", "/search?q=50%25+off+sale"),
        ("GET", "/products?id=7"), ("POST", "/contact/send"), ("GET", "/help/faq"),
        ("GET", "/search?q=it's+a+gift"),          # 誤検出の例：普通の英文でも ' を含む
        ("GET", "/products?category=books&sort=new&page=3&lang=ja&view=list"),
    ]
    suspicious = [
        ("GET", "/products?id=1' OR '1'='1", "sqli"),
        ("GET", "/products?id=1 UNION SELECT name, password FROM users", "sqli"),
        ("GET", "/search?q=' OR 1=1 --", "sqli"),
        ("GET", "/search?q=<script>alert(1)</script>", "xss"),
        ("GET", "/comment?text=<img src=x onerror=alert(1)>", "xss"),
        ("GET", "/download?file=../../etc/passwd", "traversal"),
        ("GET", "/download?file=..%2F..%2Fconfig.ini", "traversal"),
        ("GET", "/search?q=" + "A" * 220, "long_url"),
        ("GET", "/api/items?filter=" + "x" * 150 + "&debug=true", "long_url"),
        ("GET", "/admin", "scan"),
        ("GET", "/admin/login.php", "scan"),
        ("GET", "/backup.zip", "scan"),
    ]
    rows = []
    for method, url in benign:
        rows.append({"timestamp": ts(rng.randint(0, 3600)), "src_ip": rng.choice(
            ["192.0.2.31", "192.0.2.32", "192.0.2.33", "192.0.2.34"]),
            "method": method, "url": url, "status": 200, "label": "benign"})
    for i, (method, url, label) in enumerate(suspicious):
        status = 404 if label == "scan" else rng.choice([200, 400, 500])
        rows.append({"timestamp": ts(1500 + i * 7), "src_ip": "203.0.113.66",
                     "method": method, "url": url, "status": status, "label": label})
    columns = ["request_id", "timestamp", "src_ip", "method", "url", "status", "label"]
    return {"c1c/http_requests_tiny.csv": (columns, sort_and_number(rows, "request_id"))}


# ----------------------------------------------------------------------
# C-1D：ファイル状態（変更前・変更後）
# ----------------------------------------------------------------------
def make_c1d(rng):
    # hash 列は教材用の疑似ハッシュ値（H001 など）であり、実際の暗号学的ハッシュ値ではない。
    names = ["config.ini", "users.csv", "report_2026_10.docx", "report_2026_11.docx",
             "budget.xlsx", "photo_001.jpg", "photo_002.jpg", "memo.txt",
             "schedule.txt", "app.log", "readme.txt", "hosts.txt"]
    before = [{"file_id": name, "hash": f"H{i:03d}"} for i, name in enumerate(names, start=1)]

    after = []
    next_hash = len(names) + 1
    for row in before:
        name = row["file_id"]
        if name in ("users.csv",):                    # 削除されたファイル
            continue
        if name in ("config.ini", "app.log", "hosts.txt"):   # 内容が変更されたファイル
            after.append({"file_id": name, "hash": f"H{next_hash:03d}"})
            next_hash += 1
        elif name in ("photo_001.jpg", "photo_002.jpg"):
            # ランサムウェア被害の兆候を模したもの：元のファイルが消え、.locked のファイルが増える
            after.append({"file_id": name + ".locked", "hash": f"H{next_hash:03d}"})
            next_hash += 1
        else:
            after.append(dict(row))
    after.append({"file_id": "unknown_tool.exe", "hash": f"H{next_hash:03d}"})   # 追加されたファイル
    after.append({"file_id": "README_RESTORE.txt", "hash": f"H{next_hash + 1:03d}"})
    columns = ["file_id", "hash"]
    return {
        "c1d/file_states_before_tiny.csv": (columns, before),
        "c1d/file_states_after_tiny.csv": (columns, after),
    }


# ----------------------------------------------------------------------
# C-1E：データ転送量
# ----------------------------------------------------------------------
def make_c1e(rng):
    rows = []

    def add(t, src, dst, nbytes, label):
        rows.append({"timestamp": ts(t), "src_host": src, "dst_host": dst,
                     "byte_count": nbytes, "label": label})

    internal = ["198.51.100.10", "198.51.100.20"]
    # 通常の利用：各端末が社内サーバーへ小〜中程度の量を送信する
    for src, n in [("192.0.2.41", 6), ("192.0.2.42", 5), ("192.0.2.43", 6),
                   ("192.0.2.44", 5), ("192.0.2.45", 5)]:
        for _ in range(n):
            add(rng.randint(0, 3600), src, rng.choice(internal),
                rng.randint(1_000, 40_000), "benign")
    # 正常だが量が多い例（誤検出の例）：夜間バックアップでバックアップサーバーへ大量送信
    for i in range(3):
        add(3000 + i * 60, "192.0.2.44", "198.51.100.90", 900_000, "benign")
    # 情報流出を模したもの：1台が社外の通信先へ大量のデータを送信する
    for i in range(6):
        add(2000 + i * 30, "192.0.2.43", "203.0.113.200", rng.randint(400_000, 600_000),
            "exfiltration")
    columns = ["record_id", "timestamp", "src_host", "dst_host", "byte_count", "label"]
    return {"c1e/data_transfer_tiny.csv": (columns, sort_and_number(rows, "record_id"))}


# ----------------------------------------------------------------------
def build_all():
    """すべての Tiny Dataset を {相対パス: CSV文字列} の辞書として作る"""
    outputs = {}
    for maker in (make_c1a, make_c1b, make_c1c, make_c1d, make_c1e):
        rng = random.Random(f"{SEED}-{maker.__name__}")   # テーマごとに独立した乱数列
        for rel_path, (columns, rows) in maker(rng).items():
            buffer = io.StringIO()
            writer = csv.DictWriter(buffer, fieldnames=columns, lineterminator="\n")
            writer.writeheader()
            writer.writerows(rows)
            outputs[rel_path] = buffer.getvalue()
    return outputs


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--check", action="store_true",
                        help="ファイルを書き換えず、既存ファイルが再生成結果と一致するか確認する")
    args = parser.parse_args()

    outputs = build_all()
    mismatched = []
    for rel_path, text in outputs.items():
        path = DATA_DIR / rel_path
        if args.check:
            if not path.exists() or path.read_text(encoding="utf-8") != text:
                mismatched.append(rel_path)
            continue
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(text, encoding="utf-8")
        print(f"作成: data/{rel_path}（{text.count(chr(10)) - 1} 件）")

    if args.check:
        if mismatched:
            print("再生成結果と一致しないファイル:", ", ".join(mismatched))
            sys.exit(1)
        print(f"OK: {len(outputs)} 個のファイルが再生成結果と一致しました。")


if __name__ == "__main__":
    main()
