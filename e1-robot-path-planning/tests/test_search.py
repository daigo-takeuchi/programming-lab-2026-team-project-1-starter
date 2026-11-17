# E1：search.py のテスト

import unittest
from pathlib import Path

from grid_map import is_passable, is_valid_path, in_bounds, load_map, neighbors, parse_map, passable_cells
from search import ALGORITHMS, a_star, bfs, dfs, manhattan_distance

DATA_DIR = Path(__file__).parent.parent / "data"
SEARCHES = [f for _, f in ALGORITHMS]


def reference_shortest_length(grid_map):
    """テスト用：BFS とは独立した方法（距離の緩和を変化がなくなるまで繰り返す）で最短経路長を求める"""
    inf = float("inf")
    dist = {cell: inf for cell in passable_cells(grid_map)}
    dist[grid_map.start] = 0
    changed = True
    while changed:
        changed = False
        for cell in dist:
            for nxt in neighbors(grid_map, cell):
                if dist[cell] + 1 < dist[nxt]:
                    dist[nxt] = dist[cell] + 1
                    changed = True
    d = dist[grid_map.goal]
    return None if d == inf else d


class TestSampleMaps(unittest.TestCase):
    def setUp(self):
        self.maps = {name: load_map(DATA_DIR / f"{name}_map.txt") for name in ["simple", "maze", "blocked"]}

    def test_dfs_finds_valid_path(self):
        for name in ["simple", "maze"]:
            r = dfs(self.maps[name])
            self.assertTrue(r["found"])
            self.assertTrue(is_valid_path(self.maps[name], r["path"]))

    def test_bfs_and_a_star_shortest(self):
        expected = {"simple": 9, "maze": 50}
        for name, length in expected.items():
            m = self.maps[name]
            self.assertEqual(reference_shortest_length(m), length)
            for search in (bfs, a_star):
                r = search(m)
                self.assertEqual(r["length"], length, f"{search.__name__} on {name}")
                self.assertTrue(is_valid_path(m, r["path"]))

    def test_bfs_length_equals_a_star_length(self):
        for name in ["simple", "maze"]:
            self.assertEqual(bfs(self.maps[name])["length"], a_star(self.maps[name])["length"])

    def test_dfs_is_not_always_shortest(self):
        # サンプルマップでは DFS が BFS より長い経路を返す（実行して確認した値）
        self.assertEqual(dfs(self.maps["simple"])["length"], 19)
        self.assertEqual(dfs(self.maps["maze"])["length"], 78)
        for name in ["simple", "maze"]:
            self.assertGreater(dfs(self.maps[name])["length"], bfs(self.maps[name])["length"])

    def test_expanded_counts(self):
        # 展開ノード数（ゴールは数えない）。実行して確認した値
        expected = {
            "simple": {"DFS": 19, "BFS": 30, "A*": 9},
            "maze": {"DFS": 80, "BFS": 98, "A*": 61},
            "blocked": {"DFS": 12, "BFS": 12, "A*": 12},
        }
        for name, counts in expected.items():
            for alg, search in ALGORITHMS:
                self.assertEqual(search(self.maps[name])["expanded"], counts[alg], f"{alg} on {name}")

    def test_unreachable(self):
        m = self.maps["blocked"]
        for search in SEARCHES:
            r = search(m)
            self.assertFalse(r["found"])
            self.assertIsNone(r["path"])
            self.assertIsNone(r["length"])
            # 到達不能なら、スタートから到達できるセル（12個）をすべて展開して終わる
            self.assertEqual(r["expanded"], 12)


class TestCommonProperties(unittest.TestCase):
    MAPS = [
        "S.#\n..G",
        "S....\n.###.\n....G",
        "S#.\n.#.\n..G",
        "SG",
        "S\n.\n.\nG",
        "....#....\n.##.#.##.\n.#S.#.G#.\n.####.##.\n.........",
        "S.#.\n..#G",   # 到達不能
    ]

    def test_path_properties(self):
        for text in self.MAPS:
            m = parse_map(text)
            ref = reference_shortest_length(m)
            for search in SEARCHES:
                r = search(m)
                name = f"{search.__name__} on {text!r}"
                self.assertEqual(r["found"], ref is not None, name)
                if ref is None:
                    continue
                path = r["path"]
                # 経路の復元：S から始まり G で終わり、上下左右に1マスずつ移動
                self.assertTrue(is_valid_path(m, path), name)
                # 障害物・マップ外を通らない
                for cell in path:
                    self.assertTrue(in_bounds(m, cell), name)
                    self.assertTrue(is_passable(m, cell), name)
                # 経路長 = 移動回数 = セル数 - 1
                self.assertEqual(r["length"], len(path) - 1, name)
                # 同じセルを2回通らない
                self.assertEqual(len(set(path)), len(path), name)
                if search in (bfs, a_star):
                    self.assertEqual(r["length"], ref, name)
                else:
                    self.assertGreaterEqual(r["length"], ref, name)

    def test_expanded_and_order(self):
        for text in self.MAPS:
            m = parse_map(text)
            for search in SEARCHES:
                r = search(m)
                order = r["order"]
                self.assertEqual(r["expanded"], len(order))
                self.assertEqual(len(set(order)), len(order))      # 重複して展開しない
                self.assertNotIn(m.goal, order)                    # ゴールは展開しない
                if order:
                    self.assertEqual(order[0], m.start)            # 最初に展開するのはスタート
                for cell in order:
                    self.assertTrue(is_passable(m, cell))

    def test_start_equals_neighbor_of_goal(self):
        r = bfs(parse_map("SG"))
        self.assertEqual(r["path"], [(0, 0), (0, 1)])
        self.assertEqual((r["length"], r["expanded"], r["order"]), (1, 1, [(0, 0)]))


class TestOrder(unittest.TestCase):
    MAP = parse_map("...\n.S.\n..G")

    def test_bfs_order_up_right_down_left(self):
        order = bfs(self.MAP)["order"]
        self.assertEqual(order[:5], [(1, 1), (0, 1), (1, 2), (2, 1), (1, 0)])

    def test_dfs_order_goes_up_first(self):
        # スタックには逆順に push するので、取り出す順序は 上 → 右 → 下 → 左
        order = dfs(self.MAP)["order"]
        self.assertEqual(order[:3], [(1, 1), (0, 1), (0, 2)])

    def test_reproducible(self):
        m = load_map(DATA_DIR / "maze_map.txt")
        for search in SEARCHES:
            self.assertEqual(search(m), search(m))


class TestHeuristic(unittest.TestCase):
    def test_manhattan(self):
        self.assertEqual(manhattan_distance((1, 1), (5, 6)), 9)
        self.assertEqual(manhattan_distance((5, 6), (5, 6)), 0)

    def test_admissible_on_sample(self):
        # h(n) <= 実際の残り移動回数（ゴールからの BFS 距離）
        m = load_map(DATA_DIR / "maze_map.txt")
        from collections import deque
        dist = {m.goal: 0}
        q = deque([m.goal])
        while q:
            cell = q.popleft()
            for nxt in neighbors(m, cell):
                if nxt not in dist:
                    dist[nxt] = dist[cell] + 1
                    q.append(nxt)
        for cell, d in dist.items():
            self.assertLessEqual(manhattan_distance(cell, m.goal), d)

    def test_custom_heuristic_parameter(self):
        # h = 0 の A* も最短経路を返す（展開ノード数は増える）
        m = load_map(DATA_DIR / "simple_map.txt")
        r0 = a_star(m, heuristic=lambda cell, goal: 0)
        self.assertEqual(r0["length"], 9)
        self.assertGreaterEqual(r0["expanded"], a_star(m)["expanded"])


if __name__ == "__main__":
    unittest.main()
