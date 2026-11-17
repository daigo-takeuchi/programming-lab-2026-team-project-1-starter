# B1：ルービックキューブの解法アルゴリズムと計算量の比較 — starter code
#
# 1. 3×3×3 と 4×4×4 の状態数を比較する（state_space.py）
# 2. 2×2×2 キューブをスクランブルし、BFS で最短解を探す（cube.py, search.py）
#
# 短時間で終わる設定にしてある。大きなスクランブルや比較実験は、学生が追加する。

import cube
import search
import state_space

# ------------------------------------------------------------
# 1. 状態数の比較
# ------------------------------------------------------------
s2 = state_space.states_2x2x2()
s3 = state_space.states_3x3x3()
s4 = state_space.states_4x4x4()

print("=== 状態数（キューブ全体の向きの違いは同一視、4×4×4 は同色センターを区別しない）===")
print(f"2×2×2: {s2:,}")
print(f"3×3×3: {s3:,}  (約 {s3:.2e})")
print(f"4×4×4: {s4:,}  (約 {s4:.2e})")
print(f"4×4×4 / 3×3×3 = 約 {s4 / s3:.2e} 倍")
print()

# ------------------------------------------------------------
# 2. 2×2×2 キューブを BFS で解く
# ------------------------------------------------------------
scramble = "R U F'"            # 3手のスクランブル（変更して実験してみよう）

start = cube.apply_moves(cube.solved_state(), scramble)

print("=== 2×2×2 キューブ ===")
print("完成状態：")
print(cube.format_state(cube.solved_state()))
print()
print(f"スクランブル（{scramble}）後の状態：")
print(cube.format_state(start))
print()

result = search.bfs(start, max_states=200_000)

print("=== BFS の結果 ===")
print("状態          :", result["status"])
if result["solution"] is not None:
    print("解            :", " ".join(result["solution"]) or "（0手）")
    print("解の手数      :", len(result["solution"]))
    print("解を適用して完成するか:", cube.is_solved(cube.apply_moves(start, result["solution"])))
print("展開ノード数  :", result["expanded"])
print("訪問状態数    :", result["visited"])
print("最大キュー長  :", result["max_frontier"])
print(f"探索時間      : {result['time']:.4f} 秒")


# ------------------------------------------------------------
# 学生が取り組む課題（ここから先は各チームで実装する）
# ------------------------------------------------------------
# --- Core Research ---
# TODO 1：スクランブルの手数を 1, 2, 3, 4, 5 ... と増やし、探索時間・展開ノード数・
#         訪問状態数がどう増えるかを表にまとめる。
#         （ヒント：random.choice(cube.MOVE_NAMES) でランダムなスクランブルを作れる。
#           乱数シードを記録すること）
# TODO 2：max_states を変えて、どの手数から "limit"（未解決）になるかを調べる。
# TODO 3：同じスクランブル手数でも、スクランブルによって結果がどのくらいばらつくか調べる。
# TODO 4：BFS の理論計算量 O(b^d) と実測結果を比較する。
#         （b：分岐数。9種類の操作があるが、同じ面を続けて回すのは無駄なので実質はもっと小さい）
# TODO 5：BFS と、少なくとも1つの別の探索方法・解法戦略を比較する（実装または理論）。
#
# --- Advanced Research（search.py / state_space.py の TODO を参照）---
# TODO A：状態数の比・全状態列挙にかかる仮想的な時間とメモリを計算する。
# TODO B：N×N×N の構造と状態数の増え方を調べる（推測で一般式を作らない）。
# TODO C：双方向BFS・A*・IDA* を実装し、BFS と同じスクランブルで比較する。
# TODO D：4×4×4 の段階的解法（Reduction Method）を調べ、探索アルゴリズムと比較・考察する。
