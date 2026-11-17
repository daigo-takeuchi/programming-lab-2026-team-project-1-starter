# C2：DFS・BFS のテスト

import unittest

import network
import traversal

# 2つの部分に分かれたグラフ（0-1-2-3 の道、4-5 のリンク）と孤立ノード 6
DISCONNECTED = {0: [1], 1: [0, 2], 2: [1, 3], 3: [2], 4: [5], 5: [4], 6: []}


class TestTraversal(unittest.TestCase):

    def test_dfs_visits_all_reachable(self):
        """1. DFS が到達可能なノードをすべて（1回ずつ）訪問する"""
        for graph in [network.star(6), network.ring(6), network.mesh(3, 3)]:
            with self.subTest(graph=graph):
                order = traversal.dfs(graph, 0)
                self.assertEqual(sorted(order), sorted(graph))
                self.assertEqual(order[0], 0)

    def test_bfs_visits_all_reachable(self):
        """2. BFS が到達可能なノードをすべて（1回ずつ）訪問する"""
        for graph in [network.star(6), network.ring(6), network.mesh(3, 3)]:
            with self.subTest(graph=graph):
                order, hops = traversal.bfs(graph, 0)
                self.assertEqual(sorted(order), sorted(graph))
                self.assertEqual(set(hops), set(graph))

    def test_dfs_and_bfs_reach_same_nodes(self):
        """3. DFS と BFS の到達可能ノード集合が一致する（訪問順序は違ってよい）"""
        graphs = [network.random_graph(30, p, seed=s) for p in (0.05, 0.1, 0.3) for s in range(5)]
        for graph in graphs + [DISCONNECTED]:
            for start in graph:
                self.assertEqual(set(traversal.dfs(graph, start)), set(traversal.bfs(graph, start)[0]))

    def test_visit_order(self):
        """DFS は深く、BFS は近い順に訪問する（隣接リストの順序が決まっている場合）"""
        graph = network.mesh(3, 3)
        self.assertEqual(traversal.dfs(graph, 0), [0, 1, 2, 5, 4, 3, 6, 7, 8])
        self.assertEqual(traversal.bfs(graph, 0)[0], [0, 1, 3, 2, 4, 6, 5, 7, 8])

    def test_bfs_shortest_hops(self):
        """4. BFS が重みなしグラフの最短ホップ数を返す"""
        _, hops = traversal.bfs(network.ring(6), 0)
        self.assertEqual(hops, {0: 0, 1: 1, 5: 1, 2: 2, 4: 2, 3: 3})
        _, hops = traversal.bfs(network.mesh(3, 3), 0)
        self.assertEqual(hops[8], 4)
        self.assertEqual(hops[4], 2)
        _, hops = traversal.bfs(network.star(6), 3)
        self.assertEqual(hops, {3: 0, 0: 1, 1: 2, 2: 2, 4: 2, 5: 2})

    def test_disconnected(self):
        """5. 非連結グラフでは、同じ部分のノードだけを訪問する"""
        self.assertEqual(sorted(traversal.dfs(DISCONNECTED, 0)), [0, 1, 2, 3])
        order, hops = traversal.bfs(DISCONNECTED, 5)
        self.assertEqual(sorted(order), [4, 5])
        self.assertNotIn(0, hops)

    def test_isolated_node(self):
        """6. 孤立ノードからの探索は、そのノードだけを訪問する"""
        self.assertEqual(traversal.dfs(DISCONNECTED, 6), [6])
        self.assertEqual(traversal.bfs(DISCONNECTED, 6), ([6], {6: 0}))

    def test_empty_graph(self):
        """7. 空のグラフや、存在しない開始ノードでも安全に動作する"""
        self.assertEqual(traversal.dfs({}, 0), [])
        self.assertEqual(traversal.bfs({}, 0), ([], {}))
        self.assertEqual(traversal.dfs(network.star(3), 99), [])

    def test_large_graph_no_overflow(self):
        """大きなグラフでも、スタック・キューが満杯にならない（再帰の深さの上限もない）"""
        graph = network.ring(5000)
        self.assertEqual(len(traversal.dfs(graph, 0)), 5000)
        complete = network.random_graph(60, 1.0, seed=0)
        self.assertEqual(len(traversal.dfs(complete, 0)), 60)
        self.assertEqual(len(traversal.bfs(complete, 0)[0]), 60)


if __name__ == "__main__":
    unittest.main()
