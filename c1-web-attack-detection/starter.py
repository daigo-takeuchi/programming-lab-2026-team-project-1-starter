# C1：Webサーバーへのサイバー攻撃の検出 — starter code
#
# 架空のアクセスログ（data/sample_access.log）を読み込み、
# IP別のアクセス回数と404エラー回数を、線形探索と辞書の2つの方法で集計して、
# 閾値以上のIPを「調査が必要なIP」として表示する。

from pathlib import Path

import detection
import log_parser

# 閾値（教育用の仮設定であり、実際の攻撃検出の基準ではない）
ACCESS_THRESHOLD = 10       # アクセス回数がこの値以上なら「アクセス集中」
ERROR_404_THRESHOLD = 5     # 404エラー回数がこの値以上なら「404エラー集中」

# このファイルと同じ場所にある data フォルダのログを読む
LOG_FILE = Path(__file__).parent / "data" / "sample_access.log"

print("C1: Web Access Log Anomaly Detection")
print()

records, invalid_lines = log_parser.load_log(LOG_FILE)

# 2つの方法で集計する
ips, linear_access, linear_404 = detection.count_linear(records)
dict_access, dict_404 = detection.count_dict(records)

print("Total records:", len(records))
print("Invalid lines:", len(invalid_lines))
for line_number, line in invalid_lines:
    print(f"  line {line_number}: {line}")
print("Unique IPs:", len(ips))
print()

print(f"{'IP Address':<17}{'Accesses':>9}{'404 Errors':>12}")
for i in range(len(ips)):
    print(f"{ips[i]:<17}{linear_access[i]:>9}{linear_404[i]:>12}")
print()

# 線形探索版のリストを {IP: 回数} の辞書にして、辞書版と比べる（IPの順序は問わない）
same = (dict(zip(ips, linear_access)) == dict_access
        and dict(zip(ips, linear_404)) == dict_404)
print("Linear vs Dictionary:", "MATCH" if same else "MISMATCH")
print()

print(f"Thresholds (educational examples only): accesses >= {ACCESS_THRESHOLD}, "
      f"404 errors >= {ERROR_404_THRESHOLD}")
print()

print("アクセス集中を検出（調査が必要なIP）:")
for ip in detection.find_over_threshold(dict_access, ACCESS_THRESHOLD):
    print(f"  {ip}  ({dict_access[ip]} accesses)")

print("404エラー集中を検出（調査が必要なIP）:")
for ip in detection.find_over_threshold(dict_404, ERROR_404_THRESHOLD):
    print(f"  {ip}  ({dict_404[ip]} errors / {dict_access[ip]} accesses)")

print()
print("※ 検出されたIPは調査が必要な候補であり、攻撃であると確定したものではありません。")


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：閾値を変えて、検出結果がどう変わるかを調べる。
# TODO 2：IP別の404エラー率（404エラー回数 / アクセス回数）を計算して表示する。
# TODO 3：benchmark.py を使って、線形探索版と辞書版の処理時間を比較する。
# TODO 4：時間窓（例：1分間）ごとのアクセス数で検出する（Advanced A）。
