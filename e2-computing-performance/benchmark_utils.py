# E2：共通の時間計測ユーティリティ（Python 標準ライブラリのみ）
#
# ■ 計測の約束
#   ・time.perf_counter() で 1 回ずつ測る（高分解能の経過時間）
#   ・最初の warmup 回は捨てる（キャッシュ・初期化・JIT などの影響を除く）
#   ・repeats 回測って、中央値（median）を代表値にする（外れ値に強い）。平均・標準偏差も記録する
#   ・データの生成は setup() で行い、計算時間には含めない（setup の時間は別に記録する）
#   ・GPU・TPU のように非同期に実行される計算では、sync(result) で計算の終了を待ってから時計を止める

import csv
import statistics
import time


def measure(func, repeats=5, warmup=1, setup=None, sync=None):
    """func の実行時間を測る

    setup : 毎回の測定の前に呼ぶ関数（返り値を func に渡す）。ソートのように入力を書き換える処理では、
            setup で毎回新しいコピーを作る。setup の時間は計算時間に含めない。
    sync  : sync(result) で計算の終了を待つ関数（PyTorch の GPU、JAX など）。
    返り値（辞書）：median, mean, stdev, min, max（秒）、repeats, warmup, times, setup_median
    """
    if repeats < 1:
        raise ValueError("repeats は 1 以上にしてください")
    if warmup < 0:
        raise ValueError("warmup は 0 以上にしてください")

    times, setup_times = [], []
    for k in range(warmup + repeats):
        if setup is not None:
            s0 = time.perf_counter()
            arg = setup()
            s1 = time.perf_counter()
            t0 = time.perf_counter()
            result = func(arg)
        else:
            s0 = s1 = 0.0
            t0 = time.perf_counter()
            result = func()
        if sync is not None:
            sync(result)
        elapsed = time.perf_counter() - t0
        if k >= warmup:
            times.append(elapsed)
            setup_times.append(s1 - s0)

    return {
        "median": statistics.median(times),
        "mean": statistics.mean(times),
        "stdev": statistics.stdev(times) if len(times) > 1 else 0.0,
        "min": min(times),
        "max": max(times),
        "repeats": repeats,
        "warmup": warmup,
        "times": times,
        "setup_median": statistics.median(setup_times) if setup is not None else None,
    }


def format_seconds(seconds):
    """秒を読みやすい単位（s, ms, µs, ns）の文字列にする"""
    if seconds is None:
        return "-"
    for unit, scale in [("s", 1), ("ms", 1e-3), ("µs", 1e-6)]:
        if seconds >= scale:
            return f"{seconds / scale:.3g} {unit}"
    return f"{seconds / 1e-9:.3g} ns"


def format_table(rows, columns):
    """辞書のリストを、列名 columns の表（文字列）にする。秒の列は format_seconds で表示する

    columns : [(キー, 見出し), ...]。キーが "_s" で終わる列は秒として整形する
    """
    def cell(row, key):
        v = row.get(key)
        if key.endswith("_s"):
            return format_seconds(v)
        if isinstance(v, bool):          # bool は int の一種なので先に判定する
            return str(v)
        if isinstance(v, float):
            return f"{v:.3g}"
        if isinstance(v, int):
            return f"{v:,}"
        return "-" if v is None else str(v)

    body = [[cell(r, k) for k, _ in columns] for r in rows]
    heads = [h for _, h in columns]
    widths = [max(len(h), *(len(b[i]) for b in body)) if body else len(h) for i, h in enumerate(heads)]
    lines = ["  ".join(h.rjust(w) for h, w in zip(heads, widths)),
             "  ".join("-" * w for w in widths)]
    lines += ["  ".join(c.rjust(w) for c, w in zip(b, widths)) for b in body]
    return "\n".join(lines)


def save_csv(rows, path):
    """辞書のリストを CSV に保存する（times のようなリストの列は保存しない）"""
    keys = []
    for r in rows:
        for k, v in r.items():
            if k not in keys and not isinstance(v, (list, tuple)):
                keys.append(k)
    with open(path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)
    return path


# TODO（学生）：四分位範囲（statistics.quantiles）を返すようにして、ばらつきを表に加える。
# TODO（学生）：測定 1 回の時間が短すぎる（例：1 µs 未満）場合に、1 回の測定で number 回まとめて実行し、
#              1 回あたりの時間に直す（timeit と同じ考え方）。
