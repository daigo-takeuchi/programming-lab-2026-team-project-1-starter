# B2：ジグソーパズルのモデル（エッジ情報付きピースモデル）
#
# ■ ピース
#   上下左右の4辺に「接続条件を表す整数」を持つ dict で表す。
#     {"id": 0, "top": 0, "right": 2, "bottom": -3, "left": 0}
#   - 0 は外周の平らな辺
#   - 隣り合う2辺は、絶対値が等しく符号が逆（例：2 と -2）なら接続できる
#
# ■ パズル
#   {"name": ..., "rows": 行数, "cols": 列数, "pieces": ピースのリスト} の dict。
#   pieces[k]["id"] == k となるように並べる。
#
# ■ ボード（配置）
#   長さ rows × cols のリスト（またはタプル）で、左上から行優先の順に、
#   各位置に置いたピースの id を入れる。まだ置いていない位置は None。
#     2×2 の場合：位置 0 1
#                      2 3
#
# ■ 注意
#   これは実際のジグソーパズルの形状や画像を単純化したモデルである。
#   回転は考えない（Core Research）。回転は Advanced Research で拡張する。

SIDES = ("top", "right", "bottom", "left")


def make_piece(piece_id, top, right, bottom, left):
    """ピースを作る"""
    return {"id": piece_id, "top": top, "right": right, "bottom": bottom, "left": left}


def edges_match(a, b):
    """隣り合う2辺 a, b が接続できるか（0 どうしは接続できない）"""
    return a != 0 and a == -b


def border_ok(piece, row, col, rows, cols):
    """外周条件：ボードの外側に面した辺が、すべて 0（平ら）か"""
    if row == 0 and piece["top"] != 0:
        return False
    if row == rows - 1 and piece["bottom"] != 0:
        return False
    if col == 0 and piece["left"] != 0:
        return False
    if col == cols - 1 and piece["right"] != 0:
        return False
    return True


def fits(puzzle, board, index, piece_id):
    """ピース piece_id を位置 index に置いたとき、外周条件と、
    すでに置かれている上下左右のピースとの整合性を満たすか。
    （内側を向いた辺が 0 の場合も、置けないと判定する）

    （同じピースを2回使っていないかは、この関数では調べない）
    """
    rows, cols = puzzle["rows"], puzzle["cols"]
    row, col = divmod(index, cols)
    piece = puzzle["pieces"][piece_id]

    if not border_ok(piece, row, col, rows, cols):
        return False

    # (隣の位置の行, 列, このピースの辺, 隣のピースの辺)
    neighbors = [
        (row - 1, col, "top", "bottom"),
        (row + 1, col, "bottom", "top"),
        (row, col - 1, "left", "right"),
        (row, col + 1, "right", "left"),
    ]
    for r, c, my_side, other_side in neighbors:
        if 0 <= r < rows and 0 <= c < cols:
            if piece[my_side] == 0:     # 内側に平らな辺が向いていたら、何とも接続できない
                return False
            other_id = board[r * cols + c]
            if other_id is not None:
                other = puzzle["pieces"][other_id]
                if not edges_match(piece[my_side], other[other_side]):
                    return False
    return True


def is_solved(puzzle, board):
    """完成状態の正解判定

    - 全位置にピースが置かれている（不足がない）
    - すべてのピースをちょうど1回ずつ使っている
    - 外周の辺はすべて 0
    - 隣り合うすべての辺が接続できる
    """
    rows, cols = puzzle["rows"], puzzle["cols"]
    n = rows * cols
    if len(board) != n or None in board:
        return False
    if sorted(board) != list(range(n)):
        return False

    pieces = puzzle["pieces"]
    for index, piece_id in enumerate(board):
        row, col = divmod(index, cols)
        piece = pieces[piece_id]
        if not border_ok(piece, row, col, rows, cols):
            return False
        if col + 1 < cols:          # 右隣と比べる
            if not edges_match(piece["right"], pieces[board[index + 1]]["left"]):
                return False
        if row + 1 < rows:          # 下隣と比べる
            if not edges_match(piece["bottom"], pieces[board[index + cols]]["top"]):
                return False
    return True


def format_pieces(puzzle):
    """ピース情報を表の文字列にする"""
    lines = ["  id   top right bottom  left"]
    for p in puzzle["pieces"]:
        lines.append(f"{p['id']:4} {p['top']:5} {p['right']:5} {p['bottom']:6} {p['left']:5}")
    return "\n".join(lines)


def format_board(puzzle, board):
    """ボードを格子状の文字列にする（未配置は .）"""
    cols = puzzle["cols"]
    lines = []
    for r in range(puzzle["rows"]):
        cells = board[r * cols:(r + 1) * cols]
        lines.append(" ".join(" ." if c is None else f"{c:2}" for c in cells))
    return "\n".join(lines)


def rotate_piece(piece, times):
    """TODO（Advanced）：ピースを時計回りに 90° × times 回転したピースを返す

    ヒント：時計回りに90度回すと、元の left の辺が top に来る。
           top ← left, right ← top, bottom ← right, left ← bottom
    回転を扱う場合、ボードには「ピースの id」と「回転数」の組を置く必要がある。
    """
    raise NotImplementedError("回転は Advanced Research の課題です")


# ------------------------------------------------------------
# サンプル問題
# ------------------------------------------------------------

def _make_puzzle(name, rows, cols, solution, edges):
    """正解の配置 solution の順に並んだ辺の値 edges から、パズルを作る"""
    pieces = [None] * len(solution)
    for piece_id, (top, right, bottom, left) in zip(solution, edges):
        pieces[piece_id] = make_piece(piece_id, top, right, bottom, left)
    return {"name": name, "rows": rows, "cols": cols, "pieces": pieces}


# Puzzle A の正解の配置（テスト・確認用）
SOLUTION_A = (2, 0, 3, 1)


def puzzle_a():
    """Puzzle A：2×2、4ピース、回転なし。正しい配置がちょうど1つある。

    正解の配置：  2 0
                 3 1
    """
    edges = [
        # top, right, bottom, left
        (0, 1, 3, 0),       # 左上
        (0, 0, 4, -1),      # 右上
        (-3, 2, 0, 0),      # 左下
        (-4, 0, 0, -2),     # 右下
    ]
    return _make_puzzle("Puzzle A (2x2)", 2, 2, SOLUTION_A, edges)


# Puzzle B の正解の配置（テスト・確認用）
SOLUTION_B = (4, 5, 1, 6, 0, 7, 3, 2)


def puzzle_b():
    """Puzzle B：2×4、8ピース、回転なし。貪欲法が失敗し得る問題。

    正解の配置：  4 5 1 6
                 0 7 3 2

    上段の中央2か所に入るピース 5 と 1 は、どちらも「上が平ら、左が -1」で、
    位置 1 にはどちらも置けるように見える。
    しかし、位置 1 にピース 1 を置くと、位置 2 に置けるピースがなくなる。

    「行優先の順に、置けるピースのうち id が最小のものを選ぶ」貪欲法は、
    位置 1 でピース 1 を選んで行き詰まる（ピース 5 を選び直すには、
    過去の選択を戻すバックトラッキングが必要）。
    """
    edges = [
        # top, right, bottom, left
        (0, 1, 3, 0),       # 上段 左端
        (0, 1, 4, -1),      # 上段 2番目（ピース5）
        (0, 2, 8, -1),      # 上段 3番目（ピース1）：左の辺がピース5と同じ
        (0, 0, 9, -2),      # 上段 右端
        (-3, 5, 0, 0),      # 下段 左端
        (-4, 6, 0, -5),     # 下段 2番目
        (-8, 7, 0, -6),     # 下段 3番目
        (-9, 0, 0, -7),     # 下段 右端
    ]
    return _make_puzzle("Puzzle B (2x4)", 2, 4, SOLUTION_B, edges)


def puzzle_unsolvable():
    """解が存在しない 2×2 パズル（Puzzle A の1辺だけ値を変えたもの）"""
    puzzle = puzzle_a()
    puzzle["name"] = "Unsolvable (2x2)"
    puzzle["pieces"][1]["top"] = -9     # 右上のピース 0 と合わなくなる
    return puzzle
