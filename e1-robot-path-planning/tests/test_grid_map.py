# E1：grid_map.py のテスト

import unittest
from pathlib import Path

from grid_map import (
    MapError, count_edges, in_bounds, is_obstacle, is_passable, is_valid_path,
    load_map, neighbors, parse_map, passable_cells,
)

DATA_DIR = Path(__file__).parent.parent / "data"

SMALL = "S.#\n..G"   # 枠の壁がないマップ（マップ外への移動を確かめる）


class TestLoad(unittest.TestCase):
    def test_load_sample_maps(self):
        m = load_map(DATA_DIR / "simple_map.txt")
        self.assertEqual((m.width, m.height), (10, 7))
        for name in ["maze_map.txt", "blocked_map.txt"]:
            load_map(DATA_DIR / name)   # 例外が出なければよい

    def test_start_and_goal(self):
        m = load_map(DATA_DIR / "simple_map.txt")
        self.assertEqual(m.start, (1, 1))
        self.assertEqual(m.goal, (5, 6))
        m = parse_map(SMALL)
        self.assertEqual((m.start, m.goal), ((0, 0), (1, 2)))

    def test_trailing_newline_and_crlf(self):
        m = parse_map("S.\r\n.G\r\n")
        self.assertEqual((m.width, m.height), (2, 2))


class TestCells(unittest.TestCase):
    def setUp(self):
        self.m = parse_map(SMALL)

    def test_obstacle(self):
        self.assertTrue(is_obstacle(self.m, (0, 2)))
        self.assertFalse(is_obstacle(self.m, (0, 1)))
        self.assertFalse(is_obstacle(self.m, (0, 0)))   # S は通行可能
        self.assertFalse(is_obstacle(self.m, (1, 2)))   # G は通行可能
        self.assertFalse(is_passable(self.m, (0, 2)))

    def test_neighbors(self):
        # 上・右・下・左の順。障害物 (0, 2) は含まない
        self.assertEqual(neighbors(self.m, (1, 1)), [(0, 1), (1, 2), (1, 0)])
        self.assertEqual(neighbors(self.m, (0, 1)), [(1, 1), (0, 0)])

    def test_out_of_bounds(self):
        self.assertFalse(in_bounds(self.m, (-1, 0)))
        self.assertFalse(in_bounds(self.m, (0, 3)))
        self.assertFalse(is_passable(self.m, (2, 0)))
        # 角のセルからマップの外へは移動しない
        self.assertEqual(neighbors(self.m, (0, 0)), [(0, 1), (1, 0)])
        for cell in passable_cells(self.m):
            for nxt in neighbors(self.m, cell):
                self.assertTrue(in_bounds(self.m, nxt))

    def test_v_and_e(self):
        self.assertEqual(len(passable_cells(self.m)), 5)
        # (0,0)-(0,1)、(1,0)-(1,1)、(1,1)-(1,2)、(0,0)-(1,0)、(0,1)-(1,1) の5組
        self.assertEqual(count_edges(self.m), 5)

    def test_is_valid_path(self):
        self.assertTrue(is_valid_path(self.m, [(0, 0), (0, 1), (1, 1), (1, 2)]))
        self.assertFalse(is_valid_path(self.m, [(0, 0), (0, 1), (0, 2), (1, 2)]))   # 障害物
        self.assertFalse(is_valid_path(self.m, [(0, 0), (1, 1), (1, 2)]))           # 斜め
        self.assertFalse(is_valid_path(self.m, [(0, 1), (1, 1), (1, 2)]))           # S から始まらない


class TestValidation(unittest.TestCase):
    def assertRejects(self, text):
        with self.assertRaises(MapError):
            parse_map(text)

    def test_empty(self):
        self.assertRejects("")
        self.assertRejects("\n\n")

    def test_uneven_rows(self):
        self.assertRejects("S..\n.G")

    def test_invalid_char(self):
        self.assertRejects("S.x\n..G")
        self.assertRejects("S. \n..G")

    def test_no_start(self):
        self.assertRejects("...\n..G")

    def test_no_goal(self):
        self.assertRejects("S..\n...")

    def test_multiple_start_or_goal(self):
        self.assertRejects("S.S\n..G")
        self.assertRejects("S.G\n..G")

    def test_map_error_is_value_error(self):
        self.assertTrue(issubclass(MapError, ValueError))


if __name__ == "__main__":
    unittest.main()
