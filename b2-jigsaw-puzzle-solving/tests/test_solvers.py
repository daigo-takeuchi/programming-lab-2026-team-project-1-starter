# B2：探索アルゴリズムと候補配置数のテスト
#
# バックトラッキングと貪欲法は学生の課題なので、未実装（NotImplementedError）の間は
# テストをスキップする。実装すると、自動的にテストが実行されるようになる。

import unittest

import complexity
import puzzle as pz
import solvers


class TestBruteForce(unittest.TestCase):

    def test_solves_puzzle_a(self):
        """1・2. 全探索で Puzzle A を解け、得られた解が正しい"""
        puzzle = pz.puzzle_a()
        result = solvers.brute_force(puzzle)
        self.assertEqual(result["status"], "solved")
        self.assertTrue(pz.is_solved(puzzle, result["board"]))
        self.assertEqual(tuple(result["board"]), pz.SOLUTION_A)
        self.assertLessEqual(result["candidates"], 24)

    def test_solves_puzzle_b(self):
        """全探索で Puzzle B（8! = 40,320 通り）も解ける"""
        puzzle = pz.puzzle_b()
        result = solvers.brute_force(puzzle)
        self.assertEqual(result["status"], "solved")
        self.assertTrue(pz.is_solved(puzzle, result["board"]))

    def test_no_solution(self):
        """3. 解のない問題で探索を完了したら「解なし」と判定する"""
        result = solvers.brute_force(pz.puzzle_unsolvable())
        self.assertEqual(result["status"], "no_solution")
        self.assertIsNone(result["board"])
        self.assertEqual(result["candidates"], 24)      # 4! 通りをすべて調べた

    def test_limit(self):
        """4. 探索上限で安全に停止する"""
        result = solvers.brute_force(pz.puzzle_b(), max_candidates=100)
        self.assertEqual(result["status"], "limit")
        self.assertIsNone(result["board"])
        self.assertEqual(result["candidates"], 100)

    def test_limit_differs_from_no_solution(self):
        """5. 探索上限に達した場合と、解が存在しない場合を区別する"""
        puzzle = pz.puzzle_unsolvable()
        self.assertEqual(solvers.brute_force(puzzle, max_candidates=5)["status"], "limit")
        self.assertEqual(solvers.brute_force(puzzle, max_candidates=24)["status"], "no_solution")


class TestComplexity(unittest.TestCase):

    def test_count_arrangements(self):
        """6. 候補配置数 N! の計算"""
        expected = {1: 1, 2: 2, 4: 24, 6: 720, 9: 362880, 12: 479001600}
        for n, value in expected.items():
            with self.subTest(n=n):
                self.assertEqual(complexity.count_arrangements(n), value)

    def test_count_arrangements_with_rotation(self):
        """6. 回転ありの候補配置数 N! × 4^N の計算"""
        self.assertEqual(complexity.count_arrangements_with_rotation(1), 4)
        self.assertEqual(complexity.count_arrangements_with_rotation(2), 2 * 16)
        self.assertEqual(complexity.count_arrangements_with_rotation(4), 24 * 256)

    def test_brute_force_matches_theory(self):
        """解なしの問題では、全探索の候補配置数が N! と一致する"""
        result = solvers.brute_force(pz.puzzle_unsolvable())
        self.assertEqual(result["candidates"], complexity.count_arrangements(4))


class TestStudentSolvers(unittest.TestCase):
    """学生が実装したら実行されるテスト（未実装の間はスキップ）"""

    def run_or_skip(self, solver, puzzle):
        try:
            return solver(puzzle)
        except NotImplementedError:
            self.skipTest(f"{solver.__name__} は未実装")

    def test_backtracking(self):
        """バックトラッキング：Puzzle A・B を解き、解なしの問題を判定できる"""
        for puzzle in [pz.puzzle_a(), pz.puzzle_b()]:
            result = self.run_or_skip(solvers.backtracking, puzzle)
            self.assertEqual(result["status"], "solved")
            self.assertTrue(pz.is_solved(puzzle, result["board"]))
        result = self.run_or_skip(solvers.backtracking, pz.puzzle_unsolvable())
        self.assertEqual(result["status"], "no_solution")

    def test_greedy(self):
        """貪欲法："solved" と報告したなら、その配置は正しい"""
        for puzzle in [pz.puzzle_a(), pz.puzzle_b(), pz.puzzle_unsolvable()]:
            result = self.run_or_skip(solvers.greedy, puzzle)
            self.assertIn(result["status"], ("solved", "failed"))
            if result["status"] == "solved":
                self.assertTrue(pz.is_solved(puzzle, result["board"]))


if __name__ == "__main__":
    unittest.main()
