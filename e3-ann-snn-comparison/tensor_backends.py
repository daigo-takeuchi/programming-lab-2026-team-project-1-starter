# E3：ANN と Spiking Manifesto 型 LUT の Tensor（配列）実装 ―― CPU・GPU・TPU 比較用
#
# 基準実装（アルゴリズムの正解）は ann.py・spike_lut.py（Python 標準ライブラリだけ）。
# このモジュールは、同じ計算を「バッチ（複数入力をまとめた2次元配列）」で一度に行う版を
#   ・NumPy（CPU）
#   ・PyTorch（CPU / CUDA GPU）
#   ・JAX（CPU / GPU / TPU、jax.jit でコンパイル）
# で提供する。notebooks/04_colab_cpu_gpu_tpu.ipynb と 05_research_experiments.ipynb から使う。
#
# ■ 依存ライブラリ
#   NumPy は必須。PyTorch・JAX は「インストールされていれば使う」（なければその部分を使わない）。
#   starter.py・tests の既存部分は、このモジュールがなくても標準ライブラリだけで動く。
#
# ■ Tensor 版 LUT の計算（spike_lut.lut_forward と同じ結果になる）
#   X        : (B, n)        B 個の latency vector（バッチ）
#   anchors  : (nt, nc, 2)   各 LUT の anchor pair (a, b)
#   rows     : (nt, 2^nc, m) 各 LUT の行
#   bits     = X[:, a] > X[:, b]                   → (B, nt, nc)  比較（等しいときは 0）
#   index    = Σ_r bits[..., r] * 2^(nc-1-r)       → (B, nt)      1つ目の比較が最上位ビット
#   selected = rows[t, index[:, t]]                → (B, nt, m)   行の選択（gather）
#   Y        = Σ_t selected[:, t]                  → (B, m)       行の加算
#   Python の for ループは使わず、比較・整数演算・gather・総和の Tensor 演算だけで書いている。
#
# ■ 制約（静的 shape）
#   Tensor 版では、すべての LUT の比較回数 nc と出力次元 m が同じである必要がある
#   （make_random_tables で作った LUT は必ずそうなる）。JAX の jit は shape ごとにコンパイルする。

import statistics
import time

import numpy as np


# ------------------------------------------------------------
# 基準実装（ann.py・spike_lut.py）のデータを配列に変換する
# ------------------------------------------------------------
def tables_to_arrays(tables, dtype=np.float32):
    """SpikeLUT のリストを (anchors, rows) の NumPy 配列に変換する

    anchors : int32 (nt, nc, 2)
    rows    : dtype (nt, 2^nc, m)
    """
    if not tables:
        raise ValueError("LUT が1つもありません")
    nc = tables[0].n_comparisons
    m = tables[0].out_dim
    for t in tables:
        if t.n_comparisons != nc or t.out_dim != m:
            raise ValueError("Tensor 版では、すべての LUT の比較回数 nc と出力次元 m をそろえてください")
    anchors = np.array([t.anchors for t in tables], dtype=np.int32)
    rows = np.array([t.rows for t in tables], dtype=dtype)
    return anchors, rows


def bit_weights(nc):
    """[2^(nc-1), …, 2, 1]：1つ目の比較を最上位ビットにするための重み（spike_lut.bits_to_index と同じ）"""
    return (2 ** np.arange(nc - 1, -1, -1)).astype(np.int32)


def make_batch(batch_size, n_inputs, seed, low=0.0, high=1.0, dtype=np.float32):
    """一様乱数の入力バッチ (B, n) を作る（seed 固定）"""
    rng = np.random.default_rng(seed)
    return rng.uniform(low, high, size=(batch_size, n_inputs)).astype(dtype)


def make_ann_arrays(n, m, seed, dtype=np.float32):
    """benchmark.make_ann と同じ乱数で ANN の重みを作り、配列にする"""
    from benchmark import make_ann   # 基準実装の乱数生成をそのまま使う
    W, b = make_ann(n, m, seed)
    return np.array(W, dtype=dtype), np.array(b, dtype=dtype)


# ------------------------------------------------------------
# NumPy（CPU）
# ------------------------------------------------------------
def numpy_ann_forward(X, W, b):
    """Y = ReLU(X W^T + b)   X:(B,n)  W:(m,n)  b:(m,)  → (B,m)"""
    return np.maximum(X @ W.T + b, 0)


def numpy_lut_indices(X, anchors):
    """各入力・各 LUT の index (B, nt)"""
    xa = X[:, anchors[..., 0]]                 # (B, nt, nc)
    xb = X[:, anchors[..., 1]]
    bits = (xa > xb).astype(np.int32)          # 比較（等しいときは 0）
    return (bits * bit_weights(anchors.shape[1])).sum(axis=-1)


def numpy_lut_forward(X, anchors, rows):
    """Y = Σ_t rows[t, index_t]   → (B, m)"""
    idx = numpy_lut_indices(X, anchors)                     # (B, nt)
    selected = rows[np.arange(rows.shape[0])[None, :], idx]  # (B, nt, m)
    return selected.sum(axis=1)


# ------------------------------------------------------------
# PyTorch（CPU / CUDA）―― インストールされている場合だけ使える
# ------------------------------------------------------------
def torch_ann_forward(X, W, b):
    import torch
    return torch.relu(X @ W.T + b)


def torch_lut_indices(X, anchors, weights):
    """X:(B,n) float、anchors:(nt,nc,2) long、weights:(nc,) long → (B, nt) long"""
    xa = X[:, anchors[..., 0]]
    xb = X[:, anchors[..., 1]]
    bits = (xa > xb).long()
    return (bits * weights).sum(dim=-1)


def torch_lut_forward(X, anchors, rows, weights):
    import torch
    idx = torch_lut_indices(X, anchors, weights)                          # (B, nt)
    t_ids = torch.arange(rows.shape[0], device=rows.device).unsqueeze(0)  # (1, nt)
    selected = rows[t_ids, idx]                                           # (B, nt, m)
    return selected.sum(dim=1)


# ------------------------------------------------------------
# JAX（CPU / GPU / TPU）―― インストールされている場合だけ使える
# ------------------------------------------------------------
def jax_functions():
    """jit する前の JAX 版 (ann_forward, lut_forward) を返す（jax がなければ ImportError）"""
    import jax.numpy as jnp

    def ann_forward(X, W, b):
        return jnp.maximum(X @ W.T + b, 0)

    def lut_forward(X, anchors, rows):
        nt, nc = anchors.shape[0], anchors.shape[1]          # shape は jit 時に固定（静的）
        weights = 2 ** jnp.arange(nc - 1, -1, -1, dtype=jnp.int32)
        bits = (X[:, anchors[..., 0]] > X[:, anchors[..., 1]]).astype(jnp.int32)
        idx = (bits * weights).sum(axis=-1)                  # (B, nt)
        selected = rows[jnp.arange(nt)[None, :], idx]        # (B, nt, m)
        return selected.sum(axis=1)

    return ann_forward, lut_forward


# ------------------------------------------------------------
# 実行環境の検出
# ------------------------------------------------------------
def detect_environment():
    """Python・PyTorch・JAX のバージョンと、使える計算デバイスを調べる（測定はしない）"""
    import platform
    import sys

    info = {
        "python": sys.version.split()[0],
        "platform": platform.platform(),
        "cpu": platform.processor() or platform.machine(),
        "numpy": np.__version__,
        "torch": None, "cuda_available": False, "gpu_name": None,
        "jax": None, "jax_backend": None, "jax_devices": [], "tpu_available": False,
    }
    try:
        import torch
        info["torch"] = torch.__version__
        info["cuda_available"] = torch.cuda.is_available()
        if info["cuda_available"]:
            info["gpu_name"] = torch.cuda.get_device_name(0)
    except ImportError:
        pass
    try:
        import jax
        info["jax"] = jax.__version__
        info["jax_backend"] = jax.default_backend()
        info["jax_devices"] = [f"{d.platform}:{d.device_kind}" for d in jax.devices()]
        info["tpu_available"] = any(d.platform == "tpu" for d in jax.devices())
    except Exception:   # jax がない、または TPU の初期化に失敗した場合
        pass
    return info


# ------------------------------------------------------------
# 時間測定
# ------------------------------------------------------------
def time_call(fn, sync=None, warmup=3, repeats=20):
    """fn() の 初回時間・ウォームアップ後の中央値・全測定値（秒）を返す

    sync(result) は「計算が本当に終わるまで待つ」関数。
      PyTorch CUDA : lambda r: torch.cuda.synchronize()
      JAX          : lambda r: r.block_until_ready()
    GPU・TPU は非同期に実行されるため、同期せずに時間を測ると「命令を出した時間」しか測れない。
    """
    def run_once():
        t0 = time.perf_counter()
        result = fn()
        if sync is not None:
            sync(result)
        return time.perf_counter() - t0

    first = run_once()                 # 初回（JAX ではコンパイル、CUDA では初期化を含むことがある）
    for _ in range(warmup):
        run_once()
    times = [run_once() for _ in range(repeats)]
    return {"first": first, "median": statistics.median(times), "times": times}
