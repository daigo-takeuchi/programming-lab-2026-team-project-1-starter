# B2：ジグソーパズルの解法と計算量 — starter code
#
# 2×2 のパズル（Puzzle A）を全探索で解き、候補配置数と探索結果を表示する。
# バックトラッキングと貪欲法は solvers.py の TODO を見て、学生が実装する。

import complexity
import puzzle as pz
import solvers

print("=== B2：ジグソーパズルの解法と計算量 ===")
print()

puzzle = pz.puzzle_a()
n = len(puzzle["pieces"])

print(f"{puzzle['name']} のピース情報（0 は外周の平らな辺）：")
print(pz.format_pieces(puzzle))
print()
print("ピース数 N              :", n)
print("候補配置数（回転なし） N!      :", complexity.count_arrangements(n))
print("候補配置数（回転あり） N!×4^N  :", complexity.count_arrangements_with_rotation(n))
print()

result = solvers.brute_force(puzzle)

print("=== 全探索の結果 ===")
print("状態            :", result["status"])
if result["board"] is not None:
    print("解（ピースの id）:")
    print(pz.format_board(puzzle, result["board"]))
    print("解の正確性      :", pz.is_solved(puzzle, result["board"]))
print("探索した候補配置数:", result["candidates"])
print(f"探索時間        : {result['time']:.6f} 秒")


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# TODO 1：solvers.backtracking() を実装する。
# TODO 2：solvers.greedy() を実装する（局所評価関数をチームで考える）。
# TODO 3：全探索・バックトラッキング・貪欲法の探索時間を比較する。
# TODO 4：探索ノード数（候補配置数・評価回数）を比較する。定義を明記すること。
# TODO 5：ピース数を増やす（pz.puzzle_b() は 2×4 で 8! = 40,320 通り）。
#         大きなパズルを自動生成する関数を作ってもよい。
# TODO 6：回転ありのパズルに拡張する（pz.rotate_piece() を実装する）。
# TODO 7：貪欲法が失敗する問題を作る（Puzzle B を参考に）。
# TODO 8：探索空間の理論値（complexity.py）と実測値を比較する。
# TODO 9：探索順序（外周から置く等）や制約条件を工夫して、探索を速くする。
