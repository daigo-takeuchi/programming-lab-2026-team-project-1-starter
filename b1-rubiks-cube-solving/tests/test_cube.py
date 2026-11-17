# B1：2×2×2 キューブモデルのテスト

import random
import unittest
from collections import Counter

import cube


def corner_color_sets(state):
    """各コーナー（キュービー）に付いている3色の組を、位置ごとに返す"""
    corners = {}
    for i, (pos, _) in enumerate(cube.STICKERS):
        corners.setdefault(pos, []).append(state[i])
    return {pos: frozenset(colors) for pos, colors in corners.items()}


class TestCube(unittest.TestCase):

    def test_solved_state(self):
        """完成状態：24枚、各面が1色、6色が4枚ずつ"""
        state = cube.solved_state()
        self.assertEqual(len(state), 24)
        for k in range(6):
            self.assertEqual(len(set(state[k * 4:(k + 1) * 4])), 1)
        self.assertEqual(sorted(Counter(state).values()), [4] * 6)
        self.assertTrue(cube.is_solved(state))

    def test_moves_change_state(self):
        """どの回転操作も完成状態を変える"""
        solved = cube.solved_state()
        for move in cube.MOVE_NAMES:
            with self.subTest(move=move):
                self.assertNotEqual(cube.apply_move(solved, move), solved)

    def test_r_move_cycles_stickers(self):
        """R：前面の右列 → 上面の右列 → 後面の左列 → 下面の右列 → 前面の右列"""
        state = cube.apply_move(cube.solved_state(), "R")
        net = cube.format_state(state).splitlines()
        self.assertEqual(net[0].split(), ["W", "G"])          # 上面の右列が緑（前面の色）
        self.assertEqual(net[2].split(), ["O", "O", "G", "Y", "R", "R", "W", "B"])
        self.assertEqual(net[4].split(), ["Y", "B"])          # 下面の右列が青（後面の色）

    def test_inverse_move(self):
        """操作の後に逆操作をすると元に戻る"""
        solved = cube.solved_state()
        for move in cube.MOVE_NAMES:
            with self.subTest(move=move):
                undone = cube.apply_move(cube.apply_move(solved, move), cube.inverse_move(move))
                self.assertEqual(undone, solved)

    def test_inverse_sequence(self):
        """操作列の後に逆操作列をすると元に戻る"""
        rng = random.Random(1)
        for _ in range(20):
            moves = [rng.choice(cube.MOVE_NAMES) for _ in range(8)]
            state = cube.apply_moves(cube.solved_state(), moves)
            self.assertTrue(cube.is_solved(cube.apply_moves(state, cube.inverse_moves(moves))))

    def test_four_quarter_turns_identity(self):
        """同じ面の90度回転を4回行うと元に戻る（途中では戻らない）"""
        rng = random.Random(2)
        start = cube.apply_moves(cube.solved_state(), [rng.choice(cube.MOVE_NAMES) for _ in range(10)])
        for face in cube.BASIC_MOVES:
            with self.subTest(face=face):
                state = start
                for k in range(1, 5):
                    state = cube.apply_move(state, face)
                    if k < 4:
                        self.assertNotEqual(state, start)
                self.assertEqual(state, start)

    def test_half_turn_is_two_quarter_turns(self):
        """R2 = R R、R' = R R R"""
        solved = cube.solved_state()
        for face in cube.BASIC_MOVES:
            with self.subTest(face=face):
                self.assertEqual(cube.apply_move(solved, face + "2"), cube.apply_moves(solved, [face] * 2))
                self.assertEqual(cube.apply_move(solved, face + "'"), cube.apply_moves(solved, [face] * 3))

    def test_hashable(self):
        """状態はハッシュ可能で、同じ状態は set の中で1つにまとまる"""
        a = cube.apply_moves(cube.solved_state(), "R U")
        b = cube.apply_moves(cube.solved_state(), "R U")
        self.assertEqual(a, b)
        self.assertEqual(len({a, b, cube.solved_state()}), 2)
        self.assertEqual(hash(a), hash(b))

    def test_next_states(self):
        """次状態の列挙：9種類の操作それぞれに1つ、すべて異なる状態"""
        children = cube.next_states(cube.solved_state())
        self.assertEqual([move for move, _ in children], list(cube.MOVE_NAMES))
        self.assertEqual(len({state for _, state in children}), 9)

    def test_no_illegal_states(self):
        """ランダムに回しても、不正な状態（実物では作れない状態）にならない"""
        solved = cube.solved_state()
        solved_corners = Counter(corner_color_sets(solved).values())
        dbl = (-1, -1, -1)
        rng = random.Random(3)
        state = solved
        for _ in range(200):
            state = cube.apply_move(state, rng.choice(cube.MOVE_NAMES))
            # 色の枚数は変わらない
            self.assertEqual(Counter(state), Counter(solved))
            # 各コーナーの3色の組は、完成状態にあるコーナーのどれかと一致する（色がばらけない）
            self.assertEqual(Counter(corner_color_sets(state).values()), solved_corners)
            # 回さない左・下・後ろのコーナー（DBL）は動かない
            for i, (pos, _) in enumerate(cube.STICKERS):
                if pos == dbl:
                    self.assertEqual(state[i], solved[i])

    def test_unknown_move(self):
        """存在しない操作名はエラーになる"""
        with self.assertRaises(ValueError):
            cube.parse_moves("R X")


if __name__ == "__main__":
    unittest.main()
