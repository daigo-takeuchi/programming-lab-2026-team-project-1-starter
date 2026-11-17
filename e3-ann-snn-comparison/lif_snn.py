# E3：LIF（Leaky Integrate-and-Fire）ニューロン
#
# 離散時間モデル（オイラー法）：
#   V[t+1] = V[t] + dt/tau * ( -(V[t] - V_rest) + R * I[t] )
#   V[t+1] >= V_th なら スパイクを出し、V[t+1] = V_reset にリセットする
#
# ※ LIF は「ニューロンがどのように発火するか」を理解するための導入モデルであり、
#   Spiking Manifesto（論文 Section II）のモデルそのものではない。
#   論文のモデルは、膜電位を時間ステップごとにシミュレーションせず、
#   latency vector（各ニューロンの発火時刻）から次の latency vector への変換を LUT で表す（spike_lut.py）。
#
# 単位は教育用の任意単位（時間は「ステップ」または ms 相当）。


def simulate_lif(currents, dt=1.0, tau=10.0, v_rest=0.0, v_reset=0.0, v_th=1.0, r=1.0):
    """入力電流の列 currents（I[0], I[1], …）に対する LIF ニューロンの応答を記録する

    k ステップ目（k = 0, 1, …）は 入力 I[k] で V[k] → V[k+1] に更新し、時刻 (k+1)*dt の値として記録する。
    初期値は V[0] = v_rest（時刻 0）。

    返り値（辞書）
      times       : 各ステップの時刻 (k+1)*dt
      v           : 各ステップの膜電位（スパイクした場合はリセット後の値）
      currents    : 各ステップの入力電流
      spikes      : 各ステップでスパイクが出たか（True / False）
      spike_times : スパイク時刻のリスト
      spike_count : スパイク数
    """
    if dt <= 0 or tau <= 0:
        raise ValueError("dt と tau は正の値にしてください")
    if v_th <= v_reset:
        raise ValueError("閾値 v_th はリセット電位 v_reset より大きくしてください")

    v = v_rest
    record = {"times": [], "v": [], "currents": [], "spikes": [], "spike_times": [], "spike_count": 0}
    for k, current in enumerate(currents):
        v = v + dt / tau * (-(v - v_rest) + r * current)
        t = (k + 1) * dt
        spiked = v >= v_th
        if spiked:
            v = v_reset
            record["spike_times"].append(t)
        record["times"].append(t)
        record["v"].append(v)
        record["currents"].append(current)
        record["spikes"].append(spiked)
    record["spike_count"] = len(record["spike_times"])
    return record


def firing_rate(record):
    """発火率 = スパイク数 ÷ 観測時間"""
    duration = record["times"][-1] if record["times"] else 0
    return record["spike_count"] / duration if duration > 0 else 0.0


def first_spike_latency(current, steps=100, **params):
    """一定の入力電流を与えたときの最初のスパイク時刻（発火しなければ None）

    入力が強いほど早く発火する。強さを「発火の早さ（latency）」に変換する例。
    論文の Appendix VIII-E でも、強い入力ほど発火の latency が短くなるという
    皮質ニューロンの性質が紹介されている。
    """
    record = simulate_lif([current] * steps, **params)
    return record["spike_times"][0] if record["spike_times"] else None


def latency_encode(values, steps=100, **params):
    """入力値のリストを、それぞれ LIF の最初のスパイク時刻（latency vector）に変換する

    発火しない入力の latency は None になる。
    （論文では、発火しないニューロンは「大きな latency」として扱うと説明されている）
    """
    return [first_spike_latency(value, steps, **params) for value in values]


# TODO（学生）：入力電流を時間とともに変えて（パルス、ノイズ入り など）膜電位の変化を観察する。
# TODO（学生）：tau・v_th を変えて、発火率と最初のスパイク時刻がどう変わるか調べる。
# TODO（学生）：複数の LIF ニューロンをつないだ小さなネットワークを作る（Advanced B）。
