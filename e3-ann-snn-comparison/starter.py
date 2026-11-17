# E3：ANN・SNN 比較と Spiking Manifesto の LUT ―― 一連のデモ
#
# 1. 簡易 ANN の forward
# 2. LIF ニューロンのシミュレーション
# 3〜4. spike latency vector と spike order
# 5〜8. pairwise comparison → binary index → LUT 行の選択 → 出力ベクトル
# 9. ANN と LUT の演算回数の概算
# 10. 学生向け研究 TODO

import json
import os

from ann import ann_operation_counts, dense_forward, weighted_sum
from lif_snn import firing_rate, latency_encode, simulate_lif
from spike_encoding import format_order, num_orders, spike_counts, spike_order
from spike_lut import SpikeLUT, lut_forward, lut_operation_counts, make_random_tables

DATA_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "sample_patterns.json")


def fmt(values, digits=3):
    return "[" + ", ".join(f"{v:.{digits}f}" for v in values) + "]"


with open(DATA_FILE, encoding="utf-8") as f:
    data = json.load(f)

print("E3: ANN vs SNN / Spiking Manifesto")
print("（教育用の簡略モデルです。論文のモデル・実装そのものではありません）")
print()

# ------------------------------------------------------------
print("=== ANN ===")
ex = data["ann_example"]
x, W, b = ex["x"], ex["W"], ex["b"]
print(f"Input x: {x}")
print(f"Weights W: {W}")
print(f"Bias b: {b}")
print(f"Wx + b: {fmt(weighted_sum(x, W, b))}")
print(f"Output ReLU(Wx + b): {fmt(dense_forward(x, W, b))}   ← 連続値の activation vector")
print()

# ------------------------------------------------------------
print("=== LIF-SNN ===")
ex = data["lif_example"]
record = simulate_lif([ex["current"]] * ex["steps"], dt=ex["dt"], tau=ex["tau"], v_th=ex["v_th"])
print(f"Constant input current: {ex['current']}   steps: {ex['steps']}   tau: {ex['tau']}   V_th: {ex['v_th']}")
print("Membrane potential (first 12 steps):")
for t, v, s in list(zip(record["times"], record["v"], record["spikes"]))[:12]:
    bar = "#" * int(v * 30)
    print(f"  t={t:4.0f}  V={v:.3f} {bar}{'  ← spike, reset' if s else ''}")
print(f"Spike times: {record['spike_times']}")
print(f"Spike count: {record['spike_count']}   Firing rate: {firing_rate(record):.3f} spikes/step")
currents = [1.2, 1.5, 2.0, 3.0]
print(f"First-spike latency for currents {currents}: {latency_encode(currents)}   ← 強い入力ほど早く発火")
print()

# ------------------------------------------------------------
print("=== Spike Timing ===")
latencies = data["latency_example"]
print(f"Latency vector: {latencies}")
print(f"Spike order: {format_order(spike_order(latencies))}")
print()
window = data["window"]
pattern_a, pattern_b = data["pattern_a"], data["pattern_b"]
counts_a, counts_b = spike_counts(pattern_a, window), spike_counts(pattern_b, window)
order_a, order_b = spike_order(pattern_a), spike_order(pattern_b)
print(f"Pattern A: {pattern_a}   counts: {counts_a}   order: {order_a}")
print(f"Pattern B: {pattern_b}   counts: {counts_b}   order: {order_b}")
print(f"Spike counts: {'same' if counts_a == counts_b else 'different'}")
print(f"Spike order: {'same' if order_a == order_b else 'different'}")
print("Number of possible orders n!（理論上の順列数。安定して識別できる数とは限らない）:")
for n in [3, 4, 5, 6, 10]:
    print(f"  n = {n:2d}: {num_orders(n):,}")
print()

# ------------------------------------------------------------
print("=== Spike LUT ===")
ex = data["lut_example"]
table = SpikeLUT(ex["n_inputs"], ex["anchor_pairs"], ex["rows"])
print(f"Anchor pairs: {table.anchors}   (nc = {table.n_comparisons}, rows = 2^{table.n_comparisons} = {len(table.rows)})")
for name, lat in [("Latency example", latencies), ("Pattern A", pattern_a), ("Pattern B", pattern_b)]:
    result = lut_forward(lat, [table])
    bits = result["bits"][0]
    comparisons = ", ".join(f"x[{a}]>x[{b}]:{bit}" for (a, b), bit in zip(table.anchors, bits))
    print(f"{name}: {lat}")
    print(f"  Comparisons: {comparisons}")
    print(f"  Comparison bits: {bits}  → binary {''.join(map(str, bits))}")
    print(f"  LUT index: {result['indices'][0]}")
    print(f"  Output (selected row): {result['output']}")
print("  → Pattern A と B は発火数が同じでも、異なる行が選ばれる")
print()

ex = data["multi_lut_example"]
tables = make_random_tables(ex["n_inputs"], ex["n_tables"], ex["n_comparisons"], ex["out_dim"], seed=ex["seed"])
result = lut_forward(latencies, tables)
print(f"Multiple LUTs: nt = {ex['n_tables']}, nc = {ex['n_comparisons']}, m = {ex['out_dim']}（seed = {ex['seed']}）")
for i, t in enumerate(tables):
    row = t.rows[result["indices"][i]]
    print(f"  LUT {i}: anchors {t.anchors}  bits {result['bits'][i]}  index {result['indices'][i]}  row {row}")
print(f"Output latencies y = Σ selected rows: {fmt(result['output'], 2)}")
print(f"Next spike order: {format_order(spike_order(result['output']))}")
print()

# ------------------------------------------------------------
print("=== Complexity（この実装での演算回数の概算）===")
n = m = ex["n_inputs"]
ann_ops = ann_operation_counts(n, m)
lut_ops = lut_operation_counts(ex["n_tables"], ex["n_comparisons"], m)
print(f"ANN: n = {n}, m = {m}   LUT: nt = {ex['n_tables']}, nc = {ex['n_comparisons']}, m = {m}")
print(f"{'':22}{'ANN':>8}{'LUT':>8}")
for key, label in [("multiplications", "multiplications"), ("additions", "additions"),
                   ("comparisons", "comparisons"), ("lut_accesses", "LUT row accesses"),
                   ("parameters", "parameters (stored)"), ("values_read", "values read / forward")]:
    print(f"{label:22}{ann_ops.get(key, 0):>8}{lut_ops.get(key, 0):>8}")
print("※ 演算回数・保存容量の比較であり、同じ機能・精度・消費電力を意味するものではありません。")
print()

# ------------------------------------------------------------
print("Student Research TODOs:")
for todo in [
    "1. experiments.py の Experiment 1〜5 を実行し、TODO を実装する",
    "2. 発火時刻にノイズを加え、発火順序・LUT index がどれだけ変わるか調べる（spike_encoding.py）",
    "3. anchor pair 数 nc・LUT 数 nt・出力次元 m を変え、演算回数と保存容量を比べる（benchmark.py）",
    "4. ANN と LUT の forward 時間を複数回測定し、中央値で比べる（benchmark.py）",
    "5. 論文 Section II・Fig. 6・式 (1)〜(3) と、このコードの対応を説明する（README 17章）",
]:
    print(f"  {todo}")
