# E1：探索結果を ASCII マップで表示する
#
# 表示記号（優先度の高い順）
#   S  スタート
#   G  ゴール
#   #  障害物
#   *  最終経路
#   o  探索済みセル（展開したが最終経路には含まれないセル）
#   .  未探索の通行可能セル
#
# 元のマップ（GridMap.rows）は変更せず、新しい文字列を作って返す。


def render(grid_map, path=None, explored=None):
    """マップに経路・探索済みセルを重ねた文字列を返す

    path     : 最終経路（セル座標のリスト）または None
    explored : 探索済みセル（座標の集合・リスト。search の結果の "order" など）または None
    """
    path_cells = set(path or [])
    explored_cells = set(explored or [])
    lines = []
    for r, row in enumerate(grid_map.rows):
        chars = []
        for c, ch in enumerate(row):
            if ch in ("S", "G", "#"):
                chars.append(ch)
            elif (r, c) in path_cells:
                chars.append("*")
            elif (r, c) in explored_cells:
                chars.append("o")
            else:
                chars.append(".")
        lines.append("".join(chars))
    return "\n".join(lines)


def render_result(grid_map, result):
    """search の結果の辞書（path・order）をそのまま表示用の文字列にする"""
    return render(grid_map, path=result["path"], explored=result["order"])
