# F5：自由テーマによるアルゴリズム研究 ― 比較の流れを確認するデモ
#
#   python3 starter.py
#
# 初期デモは「線形探索（Algorithm A）と二分探索（Algorithm B）」の比較です。
# これは研究テーマを固定するものではなく、「2 つのアルゴリズムを同じ課題で比べる方法」の教材例です。

from algorithms import algorithm_a as alg_a
from algorithms import algorithm_b as alg_b
from experiments.benchmark import benchmark, timed, summarize
from experiments.compare_algorithms import make_search_input, make_search_task, run_comparison, format_table

N = 1_000          # サンプルデータの要素数
SEED = 0           # 乱数シード（同じ値なら同じデータ）
REPEAT = 7         # 測定の回数（代表値は中央値）

TODOS = [
    "Choose your research topic.（研究テーマを選ぶ：docs/research_plan.md）",
    "Define your research question.（Research Question と仮説を書く：notebooks/01）",
    "Implement at least two algorithms.（algorithms/ に 2 種類以上を実装し、tests/ にテストを追加する）",
    "Compare complexity and performance.（理論計算量と実測時間を、同じ課題・同じ入力で比べる：notebooks/03）",
    "Present your results.（notebooks/04 で発表する。実験していない結果は書かない）",
]


def main():
    print("F5: Open Algorithm Research Project")
    print("（初期デモ：線形探索 vs 二分探索。研究テーマの例であり、固定ではありません）\n")

    # 1. サンプルデータ（重複のない整数 N 個。並びはランダム）
    inp, gen_s = timed(make_search_input, N, SEED, 1, 1.0)
    data = inp["data"]
    key = inp["queries"][0]                  # データに含まれる値を 1 つ探す
    missing = -1                             # データに含まれない値
    print(f"[1] Sample data: N = {N}, seed = {SEED}, first 8 = {data[:8]} ...  （生成 {gen_s * 1e3:.3f} ms）")
    print(f"    Key to search: {key}（含まれる）, {missing}（含まれない）\n")

    def ok_a(idx):
        return idx != -1 and data[idx] == key

    # 2. Algorithm A：線形探索（前処理なし）
    ma = benchmark(alg_a.linear_search, args=(data, key), verify=ok_a, repeat=REPEAT, number="auto")
    print(f"Algorithm A: {alg_a.NAME}（前提：{alg_a.PRECONDITION}）")
    print(f"  Result: index {ma['result']}（data[{ma['result']}] = {data[ma['result']]}）")
    print(f"  Execution Time: {summarize(ma, 'us')}")
    print(f"  Complexity: worst {alg_a.COMPLEXITY['worst']}, preprocessing {alg_a.COMPLEXITY['preprocess']}\n")

    # 3. Algorithm B：二分探索（前処理としてソートが必要）
    sorted_data, prep_once = timed(alg_b.prepare, data)
    mp = benchmark(alg_b.prepare, args=(data,), verify=alg_b.is_sorted, repeat=REPEAT, number="auto")

    def ok_b(idx):
        return idx != -1 and sorted_data[idx] == key

    mb = benchmark(alg_b.binary_search, args=(sorted_data, key), verify=ok_b, repeat=REPEAT, number="auto")
    print(f"Algorithm B: {alg_b.NAME}（前提：{alg_b.PRECONDITION}）")
    print(f"  Preprocessing (sort): {summarize(mp, 'us')}")
    print(f"  Result: index {mb['result']} in the sorted data（sorted[{mb['result']}] = {sorted_data[mb['result']]}）")
    print(f"  Execution Time: {summarize(mb, 'us')}")
    print(f"  Complexity: worst {alg_b.COMPLEXITY['worst']}, preprocessing {alg_b.COMPLEXITY['preprocess']}\n")

    # 4. 正しさの確認（添字は配列が違うので、「見つかったか」と「その位置の値」で比べる）
    checks = {
        "A の結果の位置に key がある": data[ma["result"]] == key,
        "B の結果の位置に key がある": sorted_data[mb["result"]] == key,
        "含まれない値は A も B も -1": alg_a.linear_search(data, missing) == -1 == alg_b.binary_search(sorted_data, missing),
        "前処理後のデータが昇順": alg_b.is_sorted(sorted_data),
        "空のデータでは A も B も -1": alg_a.linear_search([], key) == -1 == alg_b.binary_search([], key),
    }
    print("[4] Correctness checks")
    for name, ok in checks.items():
        print(f"  {'OK ' if ok else 'NG '} {name}")
    print()

    # 5〜6. 比較
    ratio = ma["median"] / mb["median"] if mb["median"] > 0 else float("inf")
    print("Comparison:（1 回の探索。この PC・この実行での実測値）")
    print(f"  A (linear)            : {ma['median'] * 1e6:10.3f} us")
    print(f"  B (binary, search only): {mb['median'] * 1e6:10.3f} us   → A / B = {ratio:.1f} 倍")
    print(f"  B (sort + 1 search)   : {(mp['median'] + mb['median']) * 1e6:10.3f} us   ← 前処理を含めると？")
    gain = ma["median"] - mb["median"]
    if gain > 0:
        print(f"  ソートの時間を取り戻すには、約 {mp['median'] / gain:.0f} 回以上の探索が必要（この key・この実測値からの概算）")
    print()

    # 入力サイズを変えた比較（experiments/compare_algorithms.py と同じ処理）
    print("Input sizes 100 / 1,000 / 10,000（100 回の探索、含まれる値 50%）")
    rows = run_comparison(make_search_task(queries=100), sizes=(100, 1_000, 10_000), repeat=5, seed=SEED)
    print(format_table(rows))
    print("  Run = 探索 100 回分の時間の中央値。Comparisons = key との比較回数（実行環境によらない）")
    print("  ※ 実測時間は実行環境で変わります。理論計算量（O 記法）とは区別してください。\n")

    # 7. 学生向け TODO
    print("Student Research TODOs:")
    for i, t in enumerate(TODOS, 1):
        print(f"  {i}. {t}")


if __name__ == "__main__":
    main()
