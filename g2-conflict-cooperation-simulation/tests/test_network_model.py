import unittest

from tests import _helpers  # noqa: F401
import network_model as nm

NODES = ["A", "B", "C", "D", "E"]


class TestNetworkModel(unittest.TestCase):
    def test_generators(self):
        self.assertEqual(nm.make_network("line", NODES), [("A", "B"), ("B", "C"), ("C", "D"), ("D", "E")])
        self.assertEqual(len(nm.make_network("ring", NODES)), 5)
        self.assertEqual(nm.make_network("star", NODES), [("A", "B"), ("A", "C"), ("A", "D"), ("A", "E")])
        r1 = nm.make_network("random", NODES, 0.5, 3)
        self.assertEqual(r1, nm.make_network("random", NODES, 0.5, 3))
        self.assertEqual(len(nm.make_network("random", NODES, 1.0)), 10)
        self.assertEqual(nm.make_network("random", NODES, 0.0), [])
        with self.assertRaises(ValueError):
            nm.make_network("tree", NODES)
        with self.assertRaises(ValueError):
            nm.validate_edges(NODES, [("A", "B"), ("B", "A")])

    def test_adjacency_list(self):
        adj = nm.adjacency_list(NODES, nm.make_network("ring", NODES))
        self.assertEqual(adj["A"], ["B", "E"])
        self.assertEqual(sum(len(v) for v in adj.values()), 10)                 # 2E

    def test_adjacency_matrix(self):
        order, mat = nm.adjacency_matrix(NODES, nm.make_network("star", NODES))
        self.assertEqual(mat[0], [0, 1, 1, 1, 1])
        self.assertTrue(all(mat[i][j] == mat[j][i] for i in range(5) for j in range(5)))   # 無向 → 対称
        self.assertEqual(nm.neighbors_from_matrix(order, mat, "C"), ["A"])
        self.assertEqual(nm.memory_estimate(NODES, nm.make_network("star", NODES)),
                         {"adjacency_list": 13, "adjacency_matrix": 25})

    def test_dfs(self):
        adj = nm.adjacency_list(NODES, nm.make_network("ring", NODES))
        d = nm.dfs(adj, "A")
        self.assertEqual(d["order"], ["A", "B", "C", "D", "E"])
        self.assertEqual(nm.dfs_recursive(adj, "A")["order"], d["order"])        # 再帰版と同じ順
        self.assertEqual(nm.path_to(d["parent"], "D"), ["A", "B", "C", "D"])
        with self.assertRaises(KeyError):
            nm.dfs(adj, "Z")

    def test_bfs(self):
        adj = nm.adjacency_list(NODES, nm.make_network("ring", NODES))
        b = nm.bfs(adj, "A")
        self.assertEqual(b["order"], ["A", "B", "E", "C", "D"])
        self.assertEqual(b["dist"], {"A": 0, "B": 1, "E": 1, "C": 2, "D": 2})
        self.assertEqual(nm.path_to(b["parent"], "D"), ["A", "E", "D"])          # 最短経路
        self.assertTrue(nm.reachable(adj, "A", "D", "dfs") and nm.reachable(adj, "A", "D", "bfs"))
        line = nm.adjacency_list(list("ABCDEFGH"), nm.make_network("line", list("ABCDEFGH")))
        self.assertEqual(nm.bfs(line, "A")["dist"]["H"], 7)

    def test_components_and_isolated(self):
        nodes = NODES + ["F"]                                                   # F は孤立ノード
        edges = [("A", "B"), ("C", "D")]
        adj = nm.adjacency_list(nodes, edges)
        comps = nm.connected_components(adj)
        self.assertEqual(comps, [["A", "B"], ["C", "D"], ["E"], ["F"]])
        self.assertFalse(nm.reachable(adj, "A", "C"))
        self.assertEqual(nm.bfs(adj, "F")["order"], ["F"])
        self.assertEqual(nm.path_to(nm.bfs(adj, "A")["parent"], "C"), None)
        met = nm.network_metrics(nodes, edges)
        self.assertEqual((met["components"], met["largest_component"]), (4, 2))
        self.assertAlmostEqual(met["average_degree"], 4 / 6)

    def test_empty_graph(self):
        met = nm.network_metrics([], [])
        self.assertEqual((met["nodes"], met["edges"], met["components"], met["largest_component"]), (0, 0, 0, 0))
        self.assertEqual(nm.connected_components({}), [])
        met2 = nm.network_metrics(NODES, [], states={})
        self.assertEqual(met2["components"], 5)
        self.assertIsNone(met2["cooperation_edge_ratio"])

    def test_cooperation_metrics(self):
        edges = nm.make_network("line", NODES)
        states = {("A", "B"): "Cooperation", ("B", "C"): "Cooperation", ("C", "D"): "Tension", ("D", "E"): "Neutral"}
        met = nm.network_metrics(NODES, edges, states)
        self.assertEqual(met["cooperation_edge_ratio"], 0.5)
        self.assertEqual(met["cooperation_largest_component"], 3)
        self.assertEqual(met["cooperation_components"], 3)                       # {A,B,C} {D} {E}

    def test_large_graph(self):
        nodes = nm.node_names(2000)
        adj = nm.adjacency_list(nodes, nm.make_network("line", nodes))
        self.assertEqual(nm.dfs(adj, nodes[0])["visited"], 2000)                # スタック版は深くても動く
        self.assertEqual(nm.bfs(adj, nodes[0])["visited"], 2000)


if __name__ == "__main__":
    unittest.main()
