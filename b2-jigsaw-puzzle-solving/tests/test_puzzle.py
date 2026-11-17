# B2：パズルモデルのテスト

import unittest

import puzzle as pz


class TestPuzzle(unittest.TestCase):

    def test_pieces_generated(self):
        """1. ピース情報が正しく生成される"""
        for puzzle, n in [(pz.puzzle_a(), 4), (pz.puzzle_b(), 8)]:
            with self.subTest(name=puzzle["name"]):
                self.assertEqual(len(puzzle["pieces"]), n)
                self.assertEqual(puzzle["rows"] * puzzle["cols"], n)
                for k, piece in enumerate(puzzle["pieces"]):
                    self.assertEqual(piece["id"], k)
                    for side in pz.SIDES:
                        self.assertIsInstance(piece[side], int)
        self.assertEqual(pz.make_piece(0, 0, 2, -3, 0),
                         {"id": 0, "top": 0, "right": 2, "bottom": -3, "left": 0})

    def test_edges_match(self):
        """2. 隣接辺の整合性：絶対値が等しく符号が逆なら接続できる（0 どうしは不可）"""
        self.assertTrue(pz.edges_match(2, -2))
        self.assertTrue(pz.edges_match(-5, 5))
        self.assertFalse(pz.edges_match(2, 2))
        self.assertFalse(pz.edges_match(2, -3))
        self.assertFalse(pz.edges_match(0, 0))

    def test_border(self):
        """3. 外周条件：外側に面した辺が 0 か"""
        corner = pz.make_piece(0, 0, 1, 3, 0)       # 左上の角
        self.assertTrue(pz.border_ok(corner, 0, 0, 2, 2))
        self.assertFalse(pz.border_ok(corner, 0, 1, 2, 2))   # 右上には置けない（右が 0 でない）
        self.assertFalse(pz.border_ok(corner, 1, 0, 2, 2))   # 左下には置けない（下が 0 でない）

    def test_fits(self):
        """2・3. fits()：外周条件と、置いてあるピースとの整合性"""
        puzzle = pz.puzzle_a()
        board = [2, None, None, None]                       # 左上に正解のピース2
        self.assertTrue(pz.fits(puzzle, board, 1, 0))       # 右上に正解のピース0
        self.assertFalse(pz.fits(puzzle, board, 1, 3))      # ピース3は右上に合わない
        self.assertFalse(pz.fits(puzzle, [None] * 4, 0, 1)) # ピース1は左上の外周条件を満たさない

    def test_accept_correct_solution(self):
        """4. 正しい完成配置を受理する"""
        self.assertTrue(pz.is_solved(pz.puzzle_a(), pz.SOLUTION_A))
        self.assertTrue(pz.is_solved(pz.puzzle_b(), pz.SOLUTION_B))
        self.assertTrue(pz.is_solved(pz.puzzle_a(), list(pz.SOLUTION_A)))

    def test_reject_wrong_arrangement(self):
        """5. 不正な配置を拒否する"""
        puzzle = pz.puzzle_a()
        self.assertFalse(pz.is_solved(puzzle, (0, 1, 2, 3)))
        self.assertFalse(pz.is_solved(puzzle, (0, 2, 3, 1)))    # 左上と右上を入れ替え
        # Puzzle B：形の似たピース 5 と 1 を入れ替えると不正
        self.assertFalse(pz.is_solved(pz.puzzle_b(), (4, 1, 5, 6, 0, 7, 3, 2)))
        # 解のないパズルでは、元の正解配置も不正
        self.assertFalse(pz.is_solved(pz.puzzle_unsolvable(), pz.SOLUTION_A))

    def test_reject_duplicate_pieces(self):
        """6. 同じピースを複数回使用した配置を拒否する"""
        self.assertFalse(pz.is_solved(pz.puzzle_a(), (2, 0, 2, 1)))
        self.assertFalse(pz.is_solved(pz.puzzle_a(), (2, 2, 2, 2)))

    def test_reject_missing_pieces(self):
        """7. ピースが不足した配置を拒否する"""
        self.assertFalse(pz.is_solved(pz.puzzle_a(), (2, 0, 3)))
        self.assertFalse(pz.is_solved(pz.puzzle_a(), (2, 0, 3, None)))
        self.assertFalse(pz.is_solved(pz.puzzle_a(), ()))


if __name__ == "__main__":
    unittest.main()
