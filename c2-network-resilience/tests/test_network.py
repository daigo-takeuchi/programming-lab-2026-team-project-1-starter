# C2：ネットワーク生成のテスト

import unittest

import network


def assert_simple_undirected(test, graph):
    """自己ループなし・重複リンクなし・隣接関係が対称であることを確認する"""
    for u, neighbors in graph.items():
        test.assertNotIn(u, neighbors, f"自己ループ: {u}")
        test.assertEqual(len(neighbors), len(set(neighbors)), f"重複リンク: {u}")
        for v in neighbors:
            test.assertIn(v, graph)
            test.assertIn(u, graph[v], f"非対称: {u} -> {v}")


ALL_GRAPHS = [
    network.star(6), network.star(2), network.ring(6), network.ring(3), network.ring(2),
    network.mesh(3, 3), network.mesh(2, 4), network.mesh(1, 5),
    network.random_graph(10, 0.3, seed=1), network.random_graph(10, 1.0, seed=1),
]


class TestNetwork(unittest.TestCase):

    def test_star(self):
        """1. スター型：中心0がすべてのノードとつながる"""
        graph = network.star(6)
        self.assertEqual(graph[0], [1, 2, 3, 4, 5])
        for node in range(1, 6):
            self.assertEqual(graph[node], [0])
        self.assertEqual(network.count_edges(graph), 5)

    def test_ring(self):
        """2. リング型：各ノードが両隣とつながり、最後と最初もつながる"""
        graph = network.ring(6)
        self.assertEqual(graph[0], [1, 5])
        self.assertEqual(graph[3], [2, 4])
        self.assertEqual(graph[5], [0, 4])
        self.assertEqual(network.count_edges(graph), 6)
        self.assertTrue(all(d == 2 for d in network.degrees(graph).values()))

    def test_mesh(self):
        """3. メッシュ型（3×3）：上下左右の隣とつながる（完全グラフではない）"""
        graph = network.mesh(3, 3)
        self.assertEqual(graph[0], [1, 3])          # 角
        self.assertEqual(graph[1], [0, 2, 4])       # 辺
        self.assertEqual(graph[4], [1, 3, 5, 7])    # 中央
        self.assertEqual(graph[8], [5, 7])
        self.assertEqual(network.count_edges(graph), 12)   # 完全グラフなら 36

    def test_random_reproducible(self):
        """4. ランダム型：同じシードなら同じグラフ、p=0 ならリンクなし、p=1 なら完全グラフ"""
        self.assertEqual(network.random_graph(10, 0.3, seed=7), network.random_graph(10, 0.3, seed=7))
        self.assertEqual(network.count_edges(network.random_graph(10, 0.0, seed=7)), 0)
        self.assertEqual(network.count_edges(network.random_graph(10, 1.0, seed=7)), 45)

    def test_no_self_loops_or_duplicates_and_symmetric(self):
        """5・6・7. 自己ループなし・重複リンクなし・隣接関係が対称"""
        for graph in ALL_GRAPHS:
            with self.subTest(graph=graph):
                assert_simple_undirected(self, graph)

    def test_isolated_nodes_kept(self):
        """8. 孤立ノードも辞書に保持される"""
        graph = network.random_graph(5, 0.0, seed=0)
        self.assertEqual(graph, {0: [], 1: [], 2: [], 3: [], 4: []})

    def test_small_sizes(self):
        """9. ノード数 0・1・2 などの境界条件"""
        self.assertEqual(network.star(0), {})
        self.assertEqual(network.star(1), {0: []})
        self.assertEqual(network.ring(0), {})
        self.assertEqual(network.ring(1), {0: []})          # 自己ループを作らない
        self.assertEqual(network.ring(2), {0: [1], 1: [0]}) # 重複リンクを作らない
        self.assertEqual(network.mesh(0, 3), {})
        self.assertEqual(network.mesh(1, 1), {0: []})
        self.assertEqual(network.random_graph(0, 0.5, seed=0), {})
        self.assertEqual(network.count_edges({}), 0)


if __name__ == "__main__":
    unittest.main()
