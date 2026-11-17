# C1：IP別の集計と、固定閾値による異常候補の検出
#
# 同じ集計を2つの方法で行い、性能を比較する。
#   count_linear : IPアドレスのリストを線形探索する（教科書 第3章の seq_search を使用）
#   count_dict   : Python の辞書（dict）を使う
#
# 注意：ここで検出するのは「調査が必要なIP」の候補である。
#       アクセス集中や404エラーの集中は、攻撃であるとは限らない。

from textbook.ssearch_while import seq_search


def count_linear(records):
    """線形探索による集計

    戻り値：(ips, access_counts, error_404_counts)
        3つのリストの同じ位置が、同じIPアドレスに対応する。
        ips[i] のアクセス回数が access_counts[i]、404エラー回数が error_404_counts[i]。
    """
    ips = []
    access_counts = []
    error_404_counts = []

    for record in records:
        ip = record["ip"]
        index = seq_search(ips, ip)     # リストの先頭から順に ip を探す

        if index == -1:                 # 初めて見たIP：末尾に追加する
            ips.append(ip)
            access_counts.append(0)
            error_404_counts.append(0)
            index = len(ips) - 1

        access_counts[index] += 1
        if record["status"] == 404:
            error_404_counts[index] += 1

    return ips, access_counts, error_404_counts


def count_dict(records):
    """辞書による集計

    戻り値：(access_counts, error_404_counts)
        どちらも {IPアドレス: 回数} の辞書。
        404エラーがなかったIPも、error_404_counts に 0 として含める。
    """
    access_counts = {}
    error_404_counts = {}

    for record in records:
        ip = record["ip"]
        access_counts[ip] = access_counts.get(ip, 0) + 1
        is_404 = 1 if record["status"] == 404 else 0
        error_404_counts[ip] = error_404_counts.get(ip, 0) + is_404

    return access_counts, error_404_counts


def find_over_threshold(counts, threshold):
    """回数が閾値以上のIPアドレスを、文字列として昇順に並べたリストで返す

    counts は {IPアドレス: 回数} の辞書。
    """
    return sorted(ip for ip, count in counts.items() if count >= threshold)
