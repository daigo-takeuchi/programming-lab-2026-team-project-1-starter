# B1：2×2×2 ルービックキューブ（ポケットキューブ）のモデル
#
# ■ 状態の表し方
#   キューブ表面の 24 枚のステッカー（6面 × 4枚）の色を、長さ24のタプルで表す。
#   タプルなので == で比較でき、set や dict のキー（ハッシュ可能）にも使える。
#
#   ステッカーの並び順は U, R, F, D, L, B 面の順で、各面の4枚は展開図での読み順
#   （左上・右上・左下・右下）。
#     U：上（Up）  R：右（Right）  F：前（Front）
#     D：下（Down）L：左（Left）   B：後（Back）
#
# ■ 回転操作の作り方
#   各ステッカーを「小さなキューブ（キュービー）の中心座標」と「ステッカーの向き
#   （外向き法線）」の組で表し、実際に 3次元で 90度回転させて、回転後にどの位置へ
#   移動するかを計算している。数字を適当に入れ替えているのではなく、実物のキューブと
#   同じ動きになる。
#
# ■ 使う回転操作
#   R, U, F の3面だけを回す（R：右面を時計回りに90度、R'：反時計回り、R2：180度）。
#   2×2×2 には固定されたセンターがないため、L・D・B 面の回転は、R・U・F 面の回転と
#   キューブ全体の持ち替えの組合せで表せる。そこで「左・下・後ろのコーナー（DBL）を
#   動かさない」と決めて、R, U, F の9種類の操作だけを使う。
#   こうすると、キューブ全体の向きの違いを別の状態として数えずに済む。
#
# ■ 注意
#   これは 2×2×2 のモデルであり、3×3×3 や 4×4×4 の完全な代替モデルではない。
#   2×2×2 にはエッジとセンターがなく、コーナー8個だけで構成されている。

FACES = "URFDLB"

# 完成状態での各面の色
#   W：白  R：赤  G：緑  Y：黄  O：オレンジ  B：青
FACE_COLORS = {"U": "W", "R": "R", "F": "G", "D": "Y", "L": "O", "B": "B"}

# 各面の外向き法線（x：右方向、y：上方向、z：前方向）
FACE_NORMALS = {
    "U": (0, 1, 0),
    "D": (0, -1, 0),
    "R": (1, 0, 0),
    "L": (-1, 0, 0),
    "F": (0, 0, 1),
    "B": (0, 0, -1),
}

# 展開図での読み順（各面の4枚を、左上・右上・左下・右下の順に並べる）
#   キュービーの中心座標の各成分は -1 または +1
FACE_LAYOUT = {
    "U": [(-1, 1, -1), (1, 1, -1), (-1, 1, 1), (1, 1, 1)],
    "R": [(1, 1, 1), (1, 1, -1), (1, -1, 1), (1, -1, -1)],
    "F": [(-1, 1, 1), (1, 1, 1), (-1, -1, 1), (1, -1, 1)],
    "D": [(-1, -1, 1), (1, -1, 1), (-1, -1, -1), (1, -1, -1)],
    "L": [(-1, 1, -1), (-1, 1, 1), (-1, -1, -1), (-1, -1, 1)],
    "B": [(1, 1, -1), (-1, 1, -1), (1, -1, -1), (-1, -1, -1)],
}

# 24枚のステッカー：(キュービーの中心座標, ステッカーの向き)
STICKERS = [(pos, FACE_NORMALS[face]) for face in FACES for pos in FACE_LAYOUT[face]]

# 基本操作（R, U, F）と、それを組み合わせた全9操作
BASIC_MOVES = "RUF"
MOVE_NAMES = ("R", "R'", "R2", "U", "U'", "U2", "F", "F'", "F2")


def _cross(a, b):
    """ベクトルの外積 a × b"""
    return (a[1] * b[2] - a[2] * b[1],
            a[2] * b[0] - a[0] * b[2],
            a[0] * b[1] - a[1] * b[0])


def _dot(a, b):
    """ベクトルの内積 a · b"""
    return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]


def _rotate_clockwise(v, axis):
    """ベクトル v を、axis の方向から見て時計回りに90度回転する。

    ロドリゲスの回転公式に θ = -90° を代入した式：
        v' = (axis · v) axis − (axis × v)
    """
    c = _cross(axis, v)
    d = _dot(axis, v)
    return (d * axis[0] - c[0], d * axis[1] - c[1], d * axis[2] - c[2])


def _make_quarter_turn(face):
    """面 face を時計回りに90度回したときの、ステッカーの移動表を作る。

    戻り値 source は「回転後に位置 j にあるステッカーは、回転前は位置 source[j] に
    あった」ことを表すリスト。
    """
    axis = FACE_NORMALS[face]
    source = list(range(len(STICKERS)))
    for i, (pos, normal) in enumerate(STICKERS):
        if _dot(pos, axis) > 0:     # 回す面に属するキュービーだけが動く
            moved = (_rotate_clockwise(pos, axis), _rotate_clockwise(normal, axis))
            source[STICKERS.index(moved)] = i
    return source


# 各操作の移動表を作っておく（R2 は R を2回、R' は R を3回）
_MOVE_TABLE = {}
for _face in BASIC_MOVES:
    _quarter = _make_quarter_turn(_face)
    _table = list(range(len(STICKERS)))
    for _suffix in ["", "2", "'"]:
        _table = [_table[k] for k in _quarter]
        _MOVE_TABLE[_face + _suffix] = tuple(_table)


def solved_state():
    """完成状態を返す"""
    return tuple(FACE_COLORS[face] for face in FACES for _ in range(4))


def is_solved(state):
    """完成状態かどうか"""
    return state == solved_state()


def apply_move(state, move):
    """状態 state に操作 move（例："R", "U'", "F2"）を1回適用した新しい状態を返す"""
    table = _MOVE_TABLE[move]
    return tuple(state[k] for k in table)


def parse_moves(text):
    """"R U' F2" のような空白区切りの文字列を、操作のリストに変換する"""
    moves = text.split()
    for move in moves:
        if move not in _MOVE_TABLE:
            raise ValueError(f"unknown move: {move}")
    return moves


def apply_moves(state, moves):
    """操作の列（リストまたは "R U F" のような文字列）を順に適用する"""
    if isinstance(moves, str):
        moves = parse_moves(moves)
    for move in moves:
        state = apply_move(state, move)
    return state


def inverse_move(move):
    """1つの操作の逆操作を返す（R ↔ R'、R2 は R2 のまま）"""
    if move.endswith("'"):
        return move[0]
    if move.endswith("2"):
        return move
    return move + "'"


def inverse_moves(moves):
    """操作の列の逆操作列を返す（逆順にして、それぞれを逆操作にする）"""
    if isinstance(moves, str):
        moves = parse_moves(moves)
    return [inverse_move(move) for move in reversed(moves)]


def next_states(state, moves=MOVE_NAMES):
    """1手で移れる状態を (操作, 次の状態) のリストで返す"""
    return [(move, apply_move(state, move)) for move in moves]


def format_state(state):
    """状態を展開図の文字列にする

            U
          L F R B
            D
    """
    def row(face, r):
        i = FACES.index(face) * 4 + r * 2
        return f"{state[i]} {state[i + 1]}"

    lines = []
    for r in range(2):
        lines.append("      " + row("U", r))
    for r in range(2):
        lines.append("  ".join(row(face, r) for face in "LFRB"))
    for r in range(2):
        lines.append("      " + row("D", r))
    return "\n".join(lines)
