# C2：障害シミュレーションと接続性評価のテスト

import copy
import unittest

import network
import resilience


class TestFailures(unittest.TestCase):

    def test_remove_node(self):
        """1. ノード削除：ノードと、そのノードにつながるリンクが消える"""
        graph = resilience.remove_node(network.ring(6), 0)
        self.assertNotIn(0, graph)
        self.assertEqual(graph[1], [2])
        self.assertEqual(graph[5], [4])
        self.assertEqual(network.count_edges(graph), 4)

    def test_remove_edge(self):
        """2. リンク削除：両方向の隣接関係が消え、ノードは残る"""
        graph = resilience.remove_edge(network.ring(6), 0, 1)
        self.assertEqual(graph[0], [5])
        self.assertEqual(graph[1], [2])
        self.assertEqual(len(graph), 6)
        self.assertEqual(network.count_edges(graph), 5)
        # 存在しないリンクを指定しても壊れない
        self.assertEqual(resilience.remove_edge(network.star(4), 1, 2), network.star(4))

    def test_original_unchanged(self):
        """3. 元のグラフは変更されない"""
        graph = network.mesh(3, 3)
        backup = copy.deepcopy(graph)
        resilience.remove_node(graph, 4)
        resilience.remove_edge(graph, 0, 1)
        self.assertEqual(graph, backup)

    def test_star_center_failure(self):
        """4. スター型の中心ノード削除で連結性が失われる"""
        graph = resilience.remove_node(network.star(6), 0)
        self.assertFalse(resilience.is_connected(graph))
        self.assertEqual(len(resilience.connected_components(graph)), 5)

    def test_star_leaf_failure(self):
        """5. スター型の末端ノード削除では、残りのネットワークは連結のまま"""
        graph = resilience.remove_node(network.star(6), 5)
        self.assertTrue(resilience.is_connected(graph))
        self.assertEqual(len(graph), 5)

    def test_ring_single_link_failure(self):
        """6. リング型の単一リンク削除では連結性が維持される（2本切ると分断される）"""
        graph = resilience.remove_edge(network.ring(6), 0, 1)
        self.assertTrue(resilience.is_connected(graph))
        graph = resilience.remove_edge(graph, 3, 4)
        self.assertFalse(resilience.is_connected(graph))


class TestConnectivity(unittest.TestCase):

    GRAPH = {0: [1], 1: [0, 2], 2: [1], 3: [4], 4: [3], 5: []}   # 成分 {0,1,2} {3,4} {5}

    def test_component_count(self):
        """7. 連結成分数"""
        self.assertEqual(len(resilience.connected_components(self.GRAPH)), 3)
        self.assertEqual(len(resilience.connected_components(network.mesh(3, 3))), 1)
        self.assertEqual(len(resilience.connected_components(network.random_graph(7, 0.0, seed=0))), 7)

    def test_components_partition_nodes(self):
        """連結成分は、すべてのノードを重複なく分ける"""
        graph = network.random_graph(40, 0.05, seed=3)
        nodes = [n for c in resilience.connected_components(graph) for n in c]
        self.assertEqual(sorted(nodes), sorted(graph))

    def test_largest_component_size(self):
        """8. 最大連結成分サイズ"""
        self.assertEqual(resilience.largest_component_size(self.GRAPH), 3)
        self.assertEqual(resilience.largest_component_size(network.ring(6)), 6)

    def test_largest_component_ratio(self):
        """9. 最大連結成分の割合（分母を指定する）"""
        before = network.star(6)
        after = resilience.remove_node(before, 5)                  # 5ノードが連結
        self.assertAlmostEqual(resilience.largest_component_ratio(after, len(before)), 5 / 6)
        self.assertAlmostEqual(resilience.largest_component_ratio(after, len(after)), 1.0)
        after = resilience.remove_node(before, 0)                  # 1ノードずつ孤立
        self.assertAlmostEqual(resilience.largest_component_ratio(after, len(before)), 1 / 6)
        self.assertAlmostEqual(resilience.largest_component_ratio(self.GRAPH, 6), 0.5)

    def test_all_nodes_lost(self):
        """10. すべてのノードが失われた場合も安全に動作する"""
        graph = network.star(3)
        for node in [0, 1, 2]:
            graph = resilience.remove_node(graph, node)
        self.assertEqual(graph, {})
        self.assertEqual(resilience.connected_components(graph), [])
        self.assertFalse(resilience.is_connected(graph))
        self.assertEqual(resilience.largest_component_size(graph), 0)
        self.assertEqual(resilience.largest_component_ratio(graph, 3), 0.0)
        self.assertEqual(resilience.largest_component_ratio(graph, 0), 0.0)


if __name__ == "__main__":
    unittest.main()
