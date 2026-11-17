# B1：BFS のテスト

import unittest

import cube
import search


def scrambled(moves):
    return cube.apply_moves(cube.solved_state(), moves)


class TestBFS(unittest.TestCase):

    def assert_valid_solution(self, start, result):
        """解が見つかっていて、その解を適用すると完成状態に戻る"""
        self.assertEqual(result["status"], "solved")
        self.assertTrue(cube.is_solved(cube.apply_moves(start, result["solution"])))

    def test_solved_state_needs_zero_moves(self):
        """完成状態からの BFS は0手"""
        result = search.bfs(cube.solved_state())
        self.assertEqual(result["status"], "solved")
        self.assertEqual(result["solution"], [])
        self.assertEqual(result["expanded"], 0)

    def test_one_move_scrambles(self):
        """1手スクランブルは、その逆操作1手で解ける"""
        for move in cube.MOVE_NAMES:
            with self.subTest(move=move):
                start = scrambled([move])
                result = search.bfs(start)
                self.assert_valid_solution(start, result)
                self.assertEqual(result["solution"], [cube.inverse_move(move)])

    def test_two_move_scrambles(self):
        """異なる面の2手スクランブルは、2手で解ける"""
        for moves in ["R U", "U F'", "F2 R'", "R' U2"]:
            with self.subTest(moves=moves):
                start = scrambled(moves)
                result = search.bfs(start)
                self.assert_valid_solution(start, result)
                self.assertEqual(len(result["solution"]), 2)

    def test_solution_restores_solved_state(self):
        """3〜4手のスクランブルでも、得られた解で完成状態に戻る"""
        for moves in ["R U F'", "F R2 U'", "R U R' U'"]:
            with self.subTest(moves=moves):
                start = scrambled(moves)
                result = search.bfs(start)
                self.assert_valid_solution(start, result)
                self.assertLessEqual(len(result["solution"]), len(cube.parse_moves(moves)))

    def test_shortest_solution(self):
        """BFS はスクランブルより短い解があればそれを見つける（最短解）"""
        # R を2回 = R2 の1手で表せる
        result = search.bfs(scrambled("R R"))
        self.assertEqual(result["solution"], ["R2"])
        # R U U' は R と同じ状態なので、1手で解ける
        result = search.bfs(scrambled("R U U'"))
        self.assertEqual(result["solution"], ["R'"])
        # R U は1手では解けないので、最短は2手
        start = scrambled("R U")
        for _, child in cube.next_states(start):
            self.assertFalse(cube.is_solved(child))
        self.assertEqual(len(search.bfs(start)["solution"]), 2)

    def test_limit_stops_safely(self):
        """訪問状態数の上限に達したら、"limit"（未解決）として安全に停止する"""
        start = scrambled("R U F R' U2 F'")
        result = search.bfs(start, max_states=100)
        self.assertEqual(result["status"], "limit")
        self.assertIsNone(result["solution"])
        self.assertLessEqual(result["visited"], 100)

    def test_limit_differs_from_no_solution(self):
        """「上限で打ち切り」と「解が存在しない」を区別する

        U 面の操作だけを使う場合、到達できる状態は4つしかない。
        R で崩した状態は U だけでは戻せないので、探索し尽くして "no_solution" になる。
        """
        start = scrambled("R")
        result = search.bfs(start, moves=("U", "U'", "U2"), max_states=1000)
        self.assertEqual(result["status"], "no_solution")
        self.assertIsNone(result["solution"])
        self.assertEqual(result["visited"], 4)

        # 同じ問題でも、上限が小さすぎると "limit" になる
        result = search.bfs(start, moves=("U", "U'", "U2"), max_states=2)
        self.assertEqual(result["status"], "limit")

    def test_statistics_are_recorded(self):
        """展開ノード数・訪問状態数・最大キュー長・時間が記録される"""
        result = search.bfs(scrambled("R U F'"))
        self.assertGreater(result["expanded"], 0)
        self.assertGreaterEqual(result["visited"], result["expanded"])
        self.assertGreater(result["max_frontier"], 0)
        self.assertGreaterEqual(result["time"], 0)


if __name__ == "__main__":
    unittest.main()
