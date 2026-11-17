# E3：学生向け研究実験の入口（Experiment 1〜5）
#
# 各実験は「最小限の観察」だけを行う。条件を広げた実験、表・グラフ化、考察は学生が行う（各関数の TODO）。
# 実験の目的・操作変数・評価指標・予想される結果は README の 14章を参照。
#
#   python3 experiments.py        すべての実験を実行
#   python3 experiments.py 3      Experiment 3 だけ実行

import json
import os
import sys

from ann import ann_operation_counts, dense_forward
from benchmark import compare_ann_and_lut
from lif_snn import simulate_lif
from spike_encoding import spike_counts, spike_order
from spike_lut import SpikeLUT, lut_forward, lut_operation_counts

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_patterns.json")


def load_data():
    with open(DATA_FILE, encoding="utf-8") as f:
        return json.load(f)


def experiment1_ann(data):
    """Experiment 1：ANN の情報表現 ―― 連続値入力に対する出力を観察する"""
    print("=== Experiment 1：ANN の情報表現 ===")
    ex = data["ann_example"]
    W, b = ex["W"], ex["b"]
    for scale in [0.0, 0.5, 1.0, 2.0]:
        x = [scale * v for v in ex["x"]]
        print(f"  x = {[round(v, 2) for v in x]} → y = {[round(v, 3) for v in dense_forward(x, W, b)]}")
    print(f"  演算回数: {ann_operation_counts(len(ex['x']), len(W))}")
    # TODO 1-1：入力を少しずつ変えたとき、出力が連続的に変わることを確かめる（グラフにする）。
    # TODO 1-2：ReLU で 0 になる出力（発火しない、に近い）が、どの入力で起こるか調べる。
    # TODO 1-3：入力の「順序」だけを入れ替えたとき、ANN の出力がどう変わるか調べる。


def experiment2_lif(data):
    """Experiment 2：LIF の発火 ―― 入力電流を変えて、膜電位とスパイクを調べる"""
    print("=== Experiment 2：LIF の発火 ===")
    steps = 100
    print(f"  {'current':>8}{'spikes':>8}{'first spike':>13}")
    for current in [0.5, 1.0, 1.05, 1.2, 1.5, 2.0, 3.0]:
        record = simulate_lif([current] * steps)
        first = record["spike_times"][0] if record["spike_times"] else "-"
        print(f"  {current:>8}{record['spike_count']:>8}{first!s:>13}")
    # TODO 2-1：R × I が閾値（v_th = 1.0）以下だと発火しない理由を、式から説明する。
    # TODO 2-2：tau・dt を変えて、発火率と最初のスパイク時刻の変化を表にする。
    # TODO 2-3：時間とともに変わる入力（パルス、ノイズ）で膜電位をグラフにする。


def experiment3_spike_order(data):
    """Experiment 3：Spike order ―― 発火数が同じで順序が違う2つの入力を比べる"""
    print("=== Experiment 3：Spike order ===")
    window = data["window"]
    for name in ["pattern_a", "pattern_b"]:
        lat = data[name]
        print(f"  {name}: latencies {lat}  counts {spike_counts(lat, window)}  order {spike_order(lat)}")
    # TODO 3-1：発火数（発火率）では区別できないが、順序では区別できるパターンを他にも作る。
    # TODO 3-2：発火時刻にノイズを加え、順序が変わる確率を、ノイズの大きさごとに測る（シードを記録）。
    # TODO 3-3：発火時刻の分解能（spike_encoding.quantize）を粗くしたとき、同時発火がどれだけ増えるか調べる。


def experiment4_lut_index(data):
    """Experiment 4：LUT index ―― spike timing を変えたとき、選ばれる index がどう変わるか"""
    print("=== Experiment 4：LUT index ===")
    ex = data["lut_example"]
    table = SpikeLUT(ex["n_inputs"], ex["anchor_pairs"], ex["rows"])
    base = list(data["latency_example"])
    print(f"  anchors {table.anchors}、x[0] だけを 0.0 → 0.5 に動かす（他は {base[1:]}）")
    for t0 in [0.0, 0.05, 0.1, 0.15, 0.2, 0.3, 0.5]:
        lat = [t0] + base[1:]
        r = lut_forward(lat, [table])
        print(f"  x[0] = {t0:.2f}: bits {r['bits'][0]}  index {r['indices'][0]}  output {r['output']}")
    # TODO 4-1：x[0] = x[1]（同時発火）のとき、ビットが 0 になることを確かめ、その影響を考える。
    # TODO 4-2：小さなノイズで index が変わりやすい入力（比較する2つの発火時刻が近い入力）を探す。
    # TODO 4-3：anchors を [(0,1), (1,2), (0,2)] にして、n = 3 のすべての発火順序（3! = 6 通り）で
    #           どの index が出るか列挙し、2^3 = 8 個の index のうち到達できないものを調べる。


def experiment5_cost(data):
    """Experiment 5：計算コスト ―― ANN と LUT の演算回数と forward 時間を比べる"""
    print("=== Experiment 5：計算コスト ===")
    for n, nt, nc in [(16, 4, 4), (64, 16, 6)]:
        compare_ann_and_lut(n, nt, nc, repeats=50)
        print()
    print(f"  参考：LUT（nt=16, nc=6, m=64）の演算回数 {lut_operation_counts(16, 6, 64)}")
    # TODO 5-1：n・nt・nc・m を系統的に変えて、演算回数・時間・保存容量を表にする。
    # TODO 5-2：「保存している値の数」と「1回の forward で読み出す値の数」の違いをグラフにする。
    # TODO 5-3：時間の比較が実装（Python の for ループ）に依存することを、NumPy 版の ANN と比べて確かめる（任意）。


EXPERIMENTS = {
    "1": experiment1_ann,
    "2": experiment2_lif,
    "3": experiment3_spike_order,
    "4": experiment4_lut_index,
    "5": experiment5_cost,
}

if __name__ == "__main__":
    data = load_data()
    selected = sys.argv[1:] or list(EXPERIMENTS)
    for key in selected:
        if key not in EXPERIMENTS:
            raise SystemExit(f"Experiment {key} はありません（1〜5）")
        EXPERIMENTS[key](data)
        print()
