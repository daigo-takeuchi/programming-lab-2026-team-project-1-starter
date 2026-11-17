# E3：Spiking Manifesto 型の Look-Up Table（LUT）―― 本課題の中心
#
# 参考：E. Izhikevich, "Spiking Manifesto", arXiv:2512.11843（v2）Section II、Fig. 6、式 (1)〜(3)
#
#   Input latencies x（各ニューロンの発火時刻）
#       ↓  各 LUT i が持つ anchor pair (a, b) ごとに  x[a] > x[b] を比べる（pairwise comparison）
#   Comparison bits（0 / 1 の列）
#       ↓  ビット列を2進数として読む（binary index）           ← 式 (1)
#   LUT index j（0 〜 2^nc − 1）
#       ↓  LUT i の j 行目（出力ベクトル）を取り出す（row selection）
#   y[k] = Σ_i LUT_i[j_i][k]（すべての LUT の選ばれた行を足す）   ← 式 (2)・(3)
#
# ■ この教材での約束（論文と同じ点・違う点は README の 6〜8章、17章を参照）
#   ・比較：latencies[a] > latencies[b] なら 1、それ以外（等しい場合を含む）は 0
#   ・ビットの並び：1つ目の比較を最上位ビットとする。bits = [0, 1, 1] → "011" → index 3
#     （論文 Fig. 6 の例と同じ読み方。著者の公開コードは1つ目の比較を最下位ビットにしているが、
#       どちらでも「行の並び方」が変わるだけで、モデルの表現力は変わらない）
#   ・出力次元 m は自由に決められる（論文では出力は次の latency vector なので、m = 入力次元 n）
#   ・学習（論文 Section III の surrogate gradient・誤差逆伝播）は含めない（Advanced C）

import random


class SpikeLUT:
    """1つの LUT：anchor pair の列と、2^nc 行の出力ベクトルの表

    n_inputs : 入力（latency vector）の次元 n
    anchors  : anchor pair (a, b) のリスト。長さが比較回数 nc
    rows     : 2^nc 個の行。各行は長さ m の出力ベクトル
    """

    def __init__(self, n_inputs, anchors, rows):
        self.n_inputs = n_inputs
        self.anchors = [tuple(pair) for pair in anchors]
        self.rows = [list(row) for row in rows]

        if not self.anchors:
            raise ValueError("anchor pair が1つもありません")
        for a, b in self.anchors:
            if not (0 <= a < n_inputs and 0 <= b < n_inputs):
                raise ValueError(f"anchor pair {(a, b)} が入力次元 {n_inputs} の範囲外です")
            if a == b:
                raise ValueError(f"anchor pair {(a, b)} は異なる2つのニューロンにしてください")
        expected_rows = 2 ** len(self.anchors)
        if len(self.rows) != expected_rows:
            raise ValueError(f"比較回数 {len(self.anchors)} の LUT には {expected_rows} 行必要です"
                             f"（{len(self.rows)} 行あります）")
        widths = {len(row) for row in self.rows}
        if len(widths) != 1 or 0 in widths:
            raise ValueError("LUT のすべての行は、同じ長さ（1以上）にしてください")

    @property
    def n_comparisons(self):
        return len(self.anchors)

    @property
    def out_dim(self):
        return len(self.rows[0])


def compare_pairs(latencies, anchors):
    """各 anchor pair (a, b) について latencies[a] > latencies[b] なら 1、そうでなければ 0"""
    bits = []
    for a, b in anchors:
        bits.append(1 if latencies[a] > latencies[b] else 0)
    return bits


def bits_to_index(bits):
    """ビット列を、1つ目を最上位ビットとする2進数として整数に変換する（[0, 1, 1] → 3）"""
    index = 0
    for bit in bits:
        if bit not in (0, 1):
            raise ValueError(f"ビットは 0 か 1 です（{bit!r}）")
        index = index * 2 + bit
    return index


def index_to_bits(index, n_comparisons):
    """bits_to_index の逆：整数を n_comparisons 桁のビット列に戻す（3, 3桁 → [0, 1, 1]）"""
    if not 0 <= index < 2 ** n_comparisons:
        raise ValueError(f"index {index} は {n_comparisons} ビットで表せません")
    return [(index >> (n_comparisons - 1 - r)) & 1 for r in range(n_comparisons)]


def select_row(rows, index):
    """LUT の index 行目を返す。範囲外・整数でない index は IndexError

    Python のリストは rows[-1] のような負の index でもエラーにならないので、明示的に確認する。
    """
    if not isinstance(index, int) or isinstance(index, bool) or not 0 <= index < len(rows):
        raise IndexError(f"LUT の index {index!r} が不正です（0 〜 {len(rows) - 1}）")
    return rows[index]


def lut_forward(latencies, tables):
    """複数の LUT による forward 計算

    返り値（辞書）
      output  : 出力ベクトル y（y[k] = Σ_i LUT_i[index_i][k]）
      bits    : 各 LUT の比較結果のビット列
      indices : 各 LUT で選ばれた行の index
    """
    if not tables:
        raise ValueError("LUT が1つもありません")
    m = tables[0].out_dim
    for table in tables:
        if len(latencies) != table.n_inputs:
            raise ValueError(f"入力の次元 {len(latencies)} が LUT の入力次元 {table.n_inputs} と一致しません")
        if table.out_dim != m:
            raise ValueError("すべての LUT の出力次元をそろえてください")

    output = [0.0] * m
    all_bits, indices = [], []
    for table in tables:
        bits = compare_pairs(latencies, table.anchors)
        index = bits_to_index(bits)
        row = select_row(table.rows, index)
        for k in range(m):
            output[k] += row[k]
        all_bits.append(bits)
        indices.append(index)
    return {"output": output, "bits": all_bits, "indices": indices}


def make_random_tables(n_inputs, n_tables, n_comparisons, out_dim, seed, low=0.0, high=0.5):
    """乱数で LUT を作る（anchor pair はランダムな異なる2ニューロン、行の値は [low, high) の一様乱数）

    同じ seed なら同じ LUT ができる。論文でも anchor pair は初期化時にランダムに選ぶ。
    （行の値は本来は学習で決める。ここでは動作確認用に乱数を入れているだけ）
    """
    if n_inputs < 2:
        raise ValueError("anchor pair を作るには、入力が2つ以上必要です")
    rng = random.Random(seed)
    tables = []
    for _ in range(n_tables):
        anchors = [tuple(rng.sample(range(n_inputs), 2)) for _ in range(n_comparisons)]
        rows = [[round(rng.uniform(low, high), 2) for _ in range(out_dim)]
                for _ in range(2 ** n_comparisons)]
        tables.append(SpikeLUT(n_inputs, anchors, rows))
    return tables


def lut_operation_counts(n_tables, n_comparisons, out_dim):
    """この実装の LUT による forward（nt 個の LUT、各 nc 回の比較、出力 m 次元）の演算回数と容量"""
    nt, nc, m = n_tables, n_comparisons, out_dim
    return {
        "multiplications": 0,
        "additions": nt * m,                 # 選んだ行を出力に足す
        "comparisons": nt * nc,              # anchor pair の比較
        "lut_accesses": nt,                  # LUT の行を読み出す回数
        "parameters": nt * (2 ** nc) * m,    # LUT に保存している値の総数（anchor の番号 2·nt·nc 個は含めない）
        "values_read": nt * m,               # 1回の forward で実際に読み出す値の数
    }


# ------------------------------------------------------------
# 学生向け TODO
# ------------------------------------------------------------
# TODO 1：anchor pair 数 nc を変える（行数 2^nc がどう増えるか）。
# TODO 2：LUT 数 nt を変える。
# TODO 3：出力次元 m を変える（論文と同じ m = n にして、出力を次の latency vector として繰り返し使う）。
# TODO 4：spike timing を少しずつ変えて、選ばれる index が変わる境目を調べる。
# TODO 5：index が変わると出力ベクトルがどれだけ変わるか分析する。
# TODO 6：LUT のメモリ使用量を測る（値の数、sys.getsizeof、tracemalloc）。
# TODO 7：発火数が同じで順序が違う入力（data/sample_patterns.json の pattern_a・pattern_b など）を比べる。
# TODO 8：ある anchor pair の集合で、実際に到達できる index を、すべての発火順序を列挙して調べる（Advanced A）。
