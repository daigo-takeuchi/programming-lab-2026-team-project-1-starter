# E1：2次元グリッドマップの読み込み・検証・隣接セルの取得
#
# マップの記号
#   .  通行可能セル
#   #  障害物
#   S  スタート（ちょうど1つ）
#   G  ゴール（ちょうど1つ）
#
# 座標は (row, col)。row は上から 0, 1, 2, …、col は左から 0, 1, 2, … と数える。
# ロボットは上下左右の4方向に1セルずつ移動し、移動コストはすべて1（Core Research）。

ALLOWED_CHARS = {".", "#", "S", "G"}

# 隣接セルを調べる順序（固定）：上 → 右 → 下 → 左
# この順序を変えると DFS の探索順序や、BFS・A* が同じ長さの経路のうちどれを返すかが変わる。
DIRECTIONS = [(-1, 0), (0, 1), (1, 0), (0, -1)]


class MapError(ValueError):
    """マップの形式が正しくないときに送出する例外"""


class GridMap:
    """読み込んで検証済みの2次元グリッドマップ

    rows   : 各行の文字列のタプル（変更できない）
    height : 行数 H
    width  : 列数 W
    start  : スタートの座標 (row, col)
    goal   : ゴールの座標 (row, col)
    """

    def __init__(self, rows, start, goal):
        self.rows = tuple(rows)
        self.height = len(self.rows)
        self.width = len(self.rows[0])
        self.start = start
        self.goal = goal

    def __repr__(self):
        return f"GridMap({self.width} x {self.height}, start={self.start}, goal={self.goal})"


def parse_map(text):
    """マップの文字列を検証して GridMap を返す（不正なら MapError）

    空行は無視する（ファイル末尾の改行などに対応するため）。
    """
    rows = [line.rstrip("\r") for line in text.split("\n")]
    rows = [row for row in rows if row != ""]
    if not rows:
        raise MapError("マップが空です（高さ 0）")

    width = len(rows[0])
    for r, row in enumerate(rows):
        if len(row) != width:
            raise MapError(f"{r} 行目の長さ {len(row)} が 1 行目の長さ {width} と一致しません")

    starts, goals = [], []
    for r, row in enumerate(rows):
        for c, ch in enumerate(row):
            if ch not in ALLOWED_CHARS:
                raise MapError(f"許可されていない文字 {ch!r} があります（位置 {(r, c)}）")
            if ch == "S":
                starts.append((r, c))
            elif ch == "G":
                goals.append((r, c))

    if len(starts) != 1:
        raise MapError(f"スタート S はちょうど1つ必要です（{len(starts)} 個あります）")
    if len(goals) != 1:
        raise MapError(f"ゴール G はちょうど1つ必要です（{len(goals)} 個あります）")
    # S・G は1文字で1セルを表すので、障害物 # と同じセルになることはない。

    return GridMap(rows, starts[0], goals[0])


def load_map(path):
    """テキストファイルからマップを読み込む"""
    with open(path, encoding="utf-8") as f:
        return parse_map(f.read())


def in_bounds(grid_map, cell):
    """セルがマップの内側にあるか"""
    r, c = cell
    return 0 <= r < grid_map.height and 0 <= c < grid_map.width


def is_obstacle(grid_map, cell):
    """セルが障害物か（マップの外は障害物と同じく進入できないものとして True）"""
    if not in_bounds(grid_map, cell):
        return True
    r, c = cell
    return grid_map.rows[r][c] == "#"


def is_passable(grid_map, cell):
    """ロボットが進入できるセルか（マップの内側で、障害物でない）"""
    return not is_obstacle(grid_map, cell)


def neighbors(grid_map, cell):
    """cell から1回の移動で行ける通行可能セルのリスト（上・右・下・左の順）"""
    r, c = cell
    result = []
    for dr, dc in DIRECTIONS:
        nxt = (r + dr, c + dc)
        if is_passable(grid_map, nxt):
            result.append(nxt)
    return result


def passable_cells(grid_map):
    """通行可能セル（S・G を含む）の一覧。これがグラフのノード集合 V"""
    return [
        (r, c)
        for r in range(grid_map.height)
        for c in range(grid_map.width)
        if grid_map.rows[r][c] != "#"
    ]


def count_edges(grid_map):
    """移動可能な隣接関係（無向）の数 E。隣り合う通行可能セルの組を1本と数える"""
    total = sum(len(neighbors(grid_map, cell)) for cell in passable_cells(grid_map))
    return total // 2   # 各組を両側から1回ずつ数えているので2で割る


def is_valid_path(grid_map, path):
    """path がスタートからゴールまでの有効な経路か

    ・先頭がスタート、末尾がゴール
    ・すべてのセルがマップ内の通行可能セル
    ・隣り合うセルが上下左右に1マスずつ離れている
    """
    if not path or path[0] != grid_map.start or path[-1] != grid_map.goal:
        return False
    if not all(is_passable(grid_map, cell) for cell in path):
        return False
    for (r1, c1), (r2, c2) in zip(path, path[1:]):
        if abs(r1 - r2) + abs(c1 - c2) != 1:
            return False
    return True
