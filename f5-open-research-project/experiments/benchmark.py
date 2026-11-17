# F5：汎用の実行時間測定
#
# ■ 使い方
#   from experiments.benchmark import measure
#   m = measure(linear_search, args=(data, key), repeat=7, warmup=1)
#   print(m["median"])            # 1 回の呼び出しあたりの時間（秒）の中央値
#
# ■ 約束
#   ・時間は time.perf_counter() で測る（壁時計の時間。OS や他のプログラムの影響を受ける）。
#   ・同じ測定を repeat 回くり返し、代表値には中央値（median）を使う（外れ値に強い）。
#   ・warmup 回は「慣らし運転」として実行し、測定値に含めない。
#   ・とても短い処理は、1 回の測定の中で number 回まとめて呼び出し、1 回あたりの時間に直す。
#     number="auto" なら、1 回の測定が min_time 秒以上になるように number を決める。
#   ・アルゴリズムが入力を変更する（例：その場でソートする）ときは setup を使う。
#     setup() は測定のたびに新しい入力（引数のタプル）を作る。setup の時間は測定値に含めない
#     （別に setup_median として記録する）。
#   ・性能を評価する前に、結果が正しいことを verify で確かめる（benchmark 関数）。
#
# 計算量（理論）と実測時間は別のものです。実測時間は CPU・Python のバージョン・他の処理などで変わります。

import time

__all__ = ["median", "timed", "autorange", "measure", "benchmark", "summarize"]


def median(values):
    """中央値。要素数が偶数なら中央の 2 つの平均。空なら ValueError"""
    if len(values) == 0:
        raise ValueError("中央値を計算する値がありません")
    s = sorted(values)
    n = len(s)
    mid = n // 2
    return s[mid] if n % 2 == 1 else (s[mid - 1] + s[mid]) / 2


def _check_count(name, value, minimum):
    if isinstance(value, bool) or not isinstance(value, int) or value < minimum:
        raise ValueError(f"{name} は {minimum} 以上の整数にしてください（{value!r}）")


def timed(func, *args, **kwargs):
    """func(*args, **kwargs) を 1 回実行し、(結果, 経過秒) を返す

    データ生成・前処理・検証など、各段階の時間を 1 回だけ測るときに使う。
    """
    t0 = time.perf_counter()
    result = func(*args, **kwargs)
    return result, time.perf_counter() - t0


def autorange(func, args=(), kwargs=None, min_time=0.002, max_number=1_000_000):
    """1 回の測定が min_time 秒以上になる呼び出し回数 number（1, 2, 5, 10, 20, 50, ...）"""
    kwargs = kwargs or {}
    number = 1
    while True:
        for factor in (1, 2, 5):
            n = number * factor
            t0 = time.perf_counter()
            for _ in range(n):
                func(*args, **kwargs)
            if time.perf_counter() - t0 >= min_time or n >= max_number:
                return n
        number *= 10


def measure(func, args=(), kwargs=None, repeat=5, warmup=1, number=1, setup=None, min_time=0.002):
    """func の実行時間を repeat 回測定する

    引数
      func    : 測定する関数
      args    : 位置引数のタプル（setup を使うときは不要）
      kwargs  : キーワード引数の辞書
      repeat  : 測定の回数（1 以上）
      warmup  : 測定前の慣らし運転の回数（0 以上。測定値に含めない）
      number  : 1 回の測定で呼び出す回数（1 以上、または "auto"）
      setup   : 測定ごとに新しい引数のタプルを返す関数（入力を変更するアルゴリズム用。時間は含めない）
    戻り値（時間はすべて「1 回の呼び出しあたり」の秒）
      {"times": [...], "median", "min", "max", "mean", "repeat", "warmup", "number", "setup_median"}
    """
    _check_count("repeat", repeat, 1)
    _check_count("warmup", warmup, 0)
    kwargs = kwargs or {}
    if number == "auto":
        if setup is not None:
            raise ValueError('setup を使うときは number="auto" ではなく整数を指定してください')
        number = autorange(func, args, kwargs, min_time)
    _check_count("number", number, 1)
    if setup is not None and number != 1:
        raise ValueError("setup を使うときは number=1 にしてください（入力を毎回作り直すため）")

    for _ in range(warmup):
        func(*(setup() if setup else args), **kwargs)

    times, setup_times = [], []
    for _ in range(repeat):
        if setup is not None:
            t0 = time.perf_counter()
            call_args = setup()                       # 入力のコピーなど（測定値には含めない）
            setup_times.append(time.perf_counter() - t0)
        else:
            call_args = args
        t0 = time.perf_counter()
        for _ in range(number):
            func(*call_args, **kwargs)
        times.append((time.perf_counter() - t0) / number)
    return {"times": times, "median": median(times), "min": min(times), "max": max(times),
            "mean": sum(times) / len(times), "repeat": repeat, "warmup": warmup, "number": number,
            "setup_median": median(setup_times) if setup_times else None}


def benchmark(func, args=(), kwargs=None, verify=None, **measure_kw):
    """結果を verify で確かめてから、実行時間を測定する

    verify(結果) が False なら AssertionError（正しくないアルゴリズムの速さは比べない）。
    戻り値：measure の結果に "result"・"verified" を加えた辞書
    """
    kwargs = kwargs or {}
    setup = measure_kw.get("setup")
    result = func(*(setup() if setup else args), **kwargs)
    if verify is not None and not verify(result):
        raise AssertionError(f"{getattr(func, '__name__', func)} の結果が正しくありません：{result!r}")
    m = measure(func, args, kwargs, **measure_kw)
    m["result"] = result
    m["verified"] = verify is not None
    return m


def summarize(m, unit="ms"):
    """測定結果を短い文字列にする（例：'median 0.123 ms (min 0.120, max 0.140, n=5)'）"""
    scale = {"s": 1, "ms": 1e3, "us": 1e6}[unit]
    return (f"median {m['median'] * scale:.4g} {unit} (min {m['min'] * scale:.4g}, max {m['max'] * scale:.4g}, "
            f"repeat={m['repeat']}, number={m['number']})")
