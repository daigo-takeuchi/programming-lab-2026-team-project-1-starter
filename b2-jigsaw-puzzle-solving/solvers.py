# B2：ジグソーパズルの解法
#
# Core：全探索（brute_force）… 実装済み
# Core：バックトラッキング（backtracking）… 学生が実装する
# Core：貪欲法（greedy）… 学生が実装する
#
# 比較しやすいように、どの関数も同じ形の dict を返すようにする。
#   status : "solved"      … 正しい配置が見つかった
#            "no_solution" … 探索を最後まで終えたが、正しい配置はなかった
#            "limit"       … 探索上限に達して打ち切った（解があるかどうかは不明）
#            "failed"      … （貪欲法）途中で置けるピースがなくなった
#   board  : 見つかった配置（solved のときのみ。それ以外は None）
#   time   : 探索時間（秒）
#   その他、各アルゴリズムで数えた回数（定義を docstring に明記する）

import time
from itertools import permutations

import puzzle as pz


def brute_force(puzzle, max_candidates=1_000_000):
    """全探索：ピースのすべての並べ方（順列）を、1つずつ完成判定する。

    引数
        puzzle         : パズル
        max_candidates : 調べる完全配置の数の上限

    戻り値（dict）
        status     : "solved" / "no_solution" / "limit"
        board      : 見つかった配置（タプル）または None
        candidates : 完成判定を行った完全配置の数（＝ is_solved を呼んだ回数）
        time       : 探索時間（秒）
    """
    start_time = time.perf_counter()
    n = len(puzzle["pieces"])
    candidates = 0
    status = "no_solution"
    found = None

    for board in permutations(range(n)):    # n! 通りの並べ方を順に作る
        if candidates >= max_candidates:
            status = "limit"
            break
        candidates += 1
        if pz.is_solved(puzzle, board):
            status = "solved"
            found = board
            break

    return {
        "status": status,
        "board": found,
        "candidates": candidates,
        "time": time.perf_counter() - start_time,
    }


def backtracking(puzzle, max_nodes=1_000_000):
    """TODO（Core 3）：バックトラッキング

    考え方
        1. 位置 0 から順に（行優先で）、ピースを1つずつ置いていく。
        2. 置こうとしたピースが、外周条件や、すでに置いたピースと矛盾したら、
           その先は調べずに打ち切る（枝刈り）。→ pz.fits(puzzle, board, index, piece_id)
        3. 次の位置に置けるピースがなくなったら、1つ前の位置に戻って別の候補を試す。
        4. 最後の位置まで置けたら完成。

    実装のヒント
        - board = [None] * n から始め、使用済みのピースは used = [False] * n などで管理する
          （教科書 第5章 8queen_bb.py の flag 配列と同じ考え方）。
        - 再帰関数 place(index) を作ると書きやすい（教科書 第5章 8queen.py の set(i) と同じ形）。
        - 戻るときは、board[index] = None、used[piece_id] = False のように元に戻すこと。
        - 再帰を使わない場合は、スタック（教科書 第4章 fixed_stack.py）で書くこともできる。

    戻り値（dict）：brute_force() と同じ形にする
        status : "solved" / "no_solution" / "limit"
        board  : 見つかった配置 または None
        nodes  : 探索ノード数（pz.fits() で調べた「位置とピースの組」の数、など。
                 何を1ノードと数えたかを README に明記すること）
        time   : 探索時間（秒）
    """
    raise NotImplementedError("バックトラッキングは学生の課題です")


def greedy(puzzle):
    """TODO（Core 4）：貪欲法

    考え方
        1. 位置 0 から順に（行優先で）、その位置に置けるピースの候補を調べる。
        2. 候補の中から、局所評価関数の値が最も良いピースを1つ選んで置く。
        3. 選んだピースは再利用しない。原則として、過去の選択は戻さない。
        4. 置ける候補がなくなったら、"failed"（失敗）として終了する。

    局所評価関数の例（チームで考案すること）
        - すでに置いたピースと一致した辺の数
        - 外周条件を満たすか
        - 同点のときにどれを選ぶか（id の小さい順など）
      評価関数の選び方によって、解が得られるかどうかが変わる。
      例えば「置けるピースのうち id が最小のもの」を選ぶと、Puzzle B で失敗する。

    戻り値（dict）：brute_force() と同じ形にする
        status      : "solved" / "failed"
        board       : 完成した配置 または None（失敗時は途中までの配置を別のキーで返してもよい）
        evaluations : 局所候補の評価回数（評価関数を呼んだ回数、など。定義を明記すること）
        time        : 探索時間（秒）
    """
    raise NotImplementedError("貪欲法は学生の課題です")
