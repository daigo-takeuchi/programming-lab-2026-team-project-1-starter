# B1：探索アルゴリズム
#
# Core     ：幅優先探索（BFS）… 実装済み
# Advanced ：双方向BFS、A*、IDA* … 学生が実装する（下の TODO を参照）
#
# BFS のキューには、教科書 第4章の FixedQueue（リングバッファによる固定長キュー）を使う。
#   - FixedQueue は満杯で enque すると例外 FixedQueue.Full を送出する（データは黙って消えない）。
#   - この BFS では、1つの状態をキューに入れるのは「初めて見つけたとき」の1回だけで、
#     見つけた状態の数は max_states 以下に制限している。
#     そのため、容量 max_states のキューが満杯になることはない。
#   - 教科書の Queue（deque(maxlen) 版）は、満杯のとき先頭のデータを黙って捨てるため、
#     未探索の状態が失われる危険がある。BFS には使わない。

import time

from textbook.fixed_queue import FixedQueue

import cube


def bfs(start, moves=cube.MOVE_NAMES, max_states=200_000):
    """start から完成状態までの最短手順を幅優先探索で求める。

    引数
        start      : 開始状態
        moves      : 使ってよい操作の一覧
        max_states : 訪問する状態数の上限（これを超えそうになったら探索を打ち切る）

    戻り値（dict）
        status       : "solved"（解けた）/ "limit"（上限で打ち切り＝未解決）/
                       "no_solution"（到達できる状態をすべて調べたが解がない）
        solution     : 解の操作列（solved のときのみ。それ以外は None）
        expanded     : 展開ノード数（キューから取り出して次の状態を調べた回数）
        visited      : 訪問状態数（一度でも見つけた状態の数）
        max_frontier : キューに同時に入っていた状態の最大数
        time         : 探索時間（秒）
    """
    start_time = time.perf_counter()
    goal = cube.solved_state()

    queue = FixedQueue(max_states)
    visited = {start}                # 訪問済みの状態（set）
    parent = {start: None}           # 状態 → (1つ前の状態, そこからの操作)
    expanded = 0
    max_frontier = 1

    if start == goal:
        status = "solved"
    else:
        status = "searching"
        queue.enque(start)

    while status == "searching" and not queue.is_empty():
        state = queue.deque()
        expanded += 1

        for move, child in cube.next_states(state, moves):
            if child in visited:
                continue
            if len(visited) >= max_states:
                status = "limit"     # 上限に達した：未解決として打ち切る
                break
            visited.add(child)
            parent[child] = (state, move)
            if child == goal:
                status = "solved"
                break
            queue.enque(child)

        max_frontier = max(max_frontier, len(queue))

    if status == "searching":
        status = "no_solution"       # キューが空になった＝到達できる状態をすべて調べた

    solution = None
    if status == "solved":
        solution = _reconstruct_path(parent, goal)

    return {
        "status": status,
        "solution": solution,
        "expanded": expanded,
        "visited": len(visited),
        "max_frontier": max_frontier,
        "time": time.perf_counter() - start_time,
    }


def _reconstruct_path(parent, goal):
    """parent をゴールから開始状態までたどり、操作列を復元する"""
    path = []
    state = goal
    while parent[state] is not None:
        state, move = parent[state]
        path.append(move)
    path.reverse()
    return path


# ------------------------------------------------------------
# Advanced Research：学生が実装する探索アルゴリズム
# ------------------------------------------------------------
# 比較のため、bfs() と同じ形の戻り値（status, solution, expanded, visited,
# max_frontier, time）を返すように作ると、結果を表にまとめやすい。

def bidirectional_bfs(start, moves=cube.MOVE_NAMES, max_states=200_000):
    """TODO（Advanced C）：双方向BFS

    - 開始状態からの前向き探索と、完成状態からの後ろ向き探索を交互に進める
      （後ろ向きの1手は、操作の逆操作 cube.inverse_move() で考える）
    - 2つの探索のフロンティアが出会った状態で、経路をつなぐ
    - 両側の parent をたどって操作列を復元する（後ろ側は逆操作に直す）
    - 一方向の bfs() と、展開ノード数・訪問状態数・時間を比較する
    """
    raise NotImplementedError("双方向BFSは学生の課題です")


def heuristic(state):
    """TODO（Advanced C）：A* / IDA* 用のヒューリスティック関数 h(n)

    - 完成状態までの残り手数の「見積もり」を返す
    - 最短解を保証したい場合は、実際の残り手数を超えない（許容的な）値にすること
    - 例：位置や向きが正しくないコーナーの数をもとに考える
      （1手で最大何個のコーナーが動くかを考えないと、許容性は保証できない）
    """
    raise NotImplementedError("ヒューリスティック関数は学生の課題です")


def a_star(start, moves=cube.MOVE_NAMES, max_states=200_000):
    """TODO（Advanced C）：A* 探索

    - g(n)：開始状態からの手数
    - h(n)：heuristic(n)
    - f(n) = g(n) + h(n) が小さい状態から優先して展開する
    - 優先度付きキューには heapq モジュールが使える
    - h(n) が常に 0 のときは BFS（均一コスト探索）と同じ動きになることを確認する
    """
    raise NotImplementedError("A*は学生の課題です")


def ida_star(start, moves=cube.MOVE_NAMES, max_depth=14):
    """TODO（Advanced C）：IDA*（反復深化A*）

    - f(n) = g(n) + h(n) の上限（しきい値）を決めて、深さ優先探索（再帰）を行う
    - しきい値を超えた枝は打ち切り（枝刈り）、次の反復ではしきい値を増やす
    - 訪問済みの set を持たないため、メモリ使用量が小さい
    - 教科書 第5章（再帰的アルゴリズム）の考え方が参考になる
    - BFS・A* とメモリ使用量（最大保持状態数）を比較する
    """
    raise NotImplementedError("IDA*は学生の課題です")
