# E3：スパイク時刻（spike timing）と発火順序（spike order）による情報表現
#
# Core Research では「各ニューロンが観測時間内に1回だけ発火する」場合を考える。
#   latencies[i] = ニューロン i の発火時刻（観測区間の始まりからの時間）
# Python の index に合わせて、ニューロンの番号は 0 始まり。
#
# ■ 同時発火（発火時刻が等しい）の規則（この教材での定義）
#   ・発火順序：発火時刻が等しいニューロンは、番号の小さい方を先に並べる
#   ・pairwise comparison（spike_lut.py）：latencies[a] > latencies[b] が偽なので、ビットは 0

import math

from textbook.insertion_sort import insertion_sort


def spike_order(latencies):
    """発火順序（先に発火したニューロンの番号から順に並べたリスト）

    (発火時刻, ニューロン番号) の組を、教科書 第6章の単純挿入ソートで昇順に並べる。
    組で比べるので、発火時刻が等しいときは番号の小さい方が先になる。
    """
    pairs = [(t, i) for i, t in enumerate(latencies)]
    insertion_sort(pairs)
    return [i for _t, i in pairs]


def format_order(order):
    """[1, 3, 0, 2] → 'Neuron 1 → Neuron 3 → Neuron 0 → Neuron 2'"""
    return " → ".join(f"Neuron {i}" for i in order)


def has_simultaneous_spikes(latencies):
    """同じ時刻に発火したニューロンの組があるか"""
    return len(set(latencies)) != len(latencies)


def spike_counts(latencies, window):
    """観測時間 [0, window) の中での各ニューロンの発火数（1回発火のモデルなので 0 か 1）"""
    return [1 if 0 <= t < window else 0 for t in latencies]


def firing_rates(latencies, window):
    """各ニューロンの発火率 = 発火数 ÷ 観測時間"""
    return [count / window for count in spike_counts(latencies, window)]


def num_orders(n):
    """n 個のニューロンが1回ずつ、同時発火なしで発火するときの、発火順序の理論上の数 n!

    これは「順列の数」であり、ノイズのある実際のスパイクで安定して識別・学習・利用できる
    パターンの数とは限らない。
    """
    return math.factorial(n)


def quantize(latencies, resolution):
    """発火時刻を分解能 resolution の倍数に丸める（時間を細かく測れない場合のモデル）

    丸めると、近い時刻に発火したニューロンが同時発火になることがある。
    """
    if resolution <= 0:
        raise ValueError("分解能は正の値にしてください")
    return [round(t / resolution) * resolution for t in latencies]


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：n 個のニューロンのすべての発火順序を列挙する（itertools.permutations、または再帰で）。
# TODO 2：発火時刻に乱数のノイズを加える関数を作る（random.Random(seed) を使い、シードを記録する）。
# TODO 3：ノイズを加えたときに、発火順序が変わる割合（順序の変化率）を測る。
# TODO 4：quantize() の分解能を変えて、区別できる発火順序の数がどう変わるか調べる。
# TODO 5：同時発火がある場合の扱い（番号順にする／同順位として扱う／パターンを捨てる）を比べる。
