# E1：visualization.py のテスト

import unittest

from grid_map import parse_map
from search import bfs
from visualization import render, render_result

TEXT = "S..#\n.#..\n...G"


class TestRender(unittest.TestCase):
    def setUp(self):
        self.m = parse_map(TEXT)

    def cell(self, rendered, r, c):
        return rendered.split("\n")[r][c]

    def test_plain_map_is_unchanged(self):
        self.assertEqual(render(self.m), TEXT)

    def test_start_and_goal(self):
        path = [(0, 0), (1, 0), (2, 0), (2, 1), (2, 2), (2, 3)]
        out = render(self.m, path=path, explored=path)
        self.assertEqual(self.cell(out, 0, 0), "S")   # 経路・探索済みより S を優先
        self.assertEqual(self.cell(out, 2, 3), "G")

    def test_obstacles(self):
        out = render(self.m, path=[(0, 3)], explored=[(1, 1)])   # 障害物に重ねても # のまま
        self.assertEqual(self.cell(out, 0, 3), "#")
        self.assertEqual(self.cell(out, 1, 1), "#")

    def test_path_and_explored(self):
        path = [(0, 0), (0, 1), (0, 2), (1, 2), (1, 3), (2, 3)]
        explored = [(0, 0), (1, 0), (0, 1), (2, 0), (0, 2), (1, 2)]
        out = render(self.m, path=path, explored=explored)
        self.assertEqual(out, "S**#\no#**\no..G")

    def test_render_result(self):
        r = bfs(self.m)
        out = render_result(self.m, r)
        self.assertEqual(out.count("*"), r["length"] - 1)   # S・G を除く経路のセル
        self.assertEqual(out.split("\n")[0][0], "S")

    def test_unreachable_result(self):
        m = parse_map("S#.\n.#G")
        out = render_result(m, bfs(m))
        self.assertEqual(out, "S#.\no#G")

    def test_does_not_modify_map(self):
        rows_before = self.m.rows
        render(self.m, path=[(0, 0), (0, 1)], explored=[(1, 0)])
        self.assertEqual(self.m.rows, rows_before)
        self.assertEqual(render(self.m), TEXT)


if __name__ == "__main__":
    unittest.main()
