#!/usr/bin/env python3

import unittest
from graphtheory.structures.edges import Edge
from graphtheory.structures.graphs import Graph
from graphtheory.algorithms.acyclic import is_acyclic
from graphtheory.connectivity.connected import is_connected
from graphtheory.traversing.bfs import SimpleBFS

#         6---7    tree, to nie jest interval graph
#         |        trzeba dodac krawedz (3,7)
# 1---2---3---4---5
#
# 12--23--367--34--45  path decomposition

class TestPathDecomposition(unittest.TestCase):

    def setUp(self):
        self.N = 7   # number of nodes
        self.G = Graph(n=self.N)
        self.nodes = [1,2,3,4,5,6,7]
        self.edges = [
            Edge(1, 2), Edge(2, 3), Edge(3, 4), Edge(4, 5), 
            Edge(3, 6), Edge(6, 7)]
        for node in self.nodes:
            self.G.add_node(node)
        for edge in self.edges:
            self.G.add_edge(edge)
        self.T = Graph(n=5)   # path decomposition
        b0 = (1, 2)
        b1 = (2, 3)
        b2 = (3, 6, 7)
        b3 = (3, 4)
        b4 = (4, 5)
        bags = [b0, b1, b2, b3, b4]
        tdedges = [Edge(b0, b1), Edge(b1, b2), Edge(b2, b3), Edge(b3, b4)]
        for bag in bags:
            self.T.add_node(bag)
        for edge in tdedges:
            self.T.add_edge(edge)
        #self.T.show()

    def test_is_path(self):
        self.assertTrue(is_acyclic(self.T))
        self.assertTrue(is_connected(self.T))
        degree_dict = dict()
        for bag in self.T.iternodes():
            deg = self.T.degree(bag)
            degree_dict[deg] = degree_dict.get(deg, 0) + 1
        self.assertEqual(degree_dict[1], 2)
        self.assertEqual(degree_dict[2], self.T.v()-2)

    def test_bags_cover_vertices(self):
        set1 = set(self.G.iternodes())
        set2 = set()
        for bag in self.T.iternodes():
            set2.update(bag)   # po worku moge iterowac
        self.assertEqual(set1, set2)

    def test_bags_cover_edges(self):
        # Buduje graf wiekszy niz G (tu akurat rowny G).
        H = Graph(n=self.N)
        for node in self.G.iternodes():
            H.add_node(node)
        for bag in self.T.iternodes():
            for node1 in bag:
                for node2 in bag:
                    if node1 < node2:
                        edge = Edge(node1, node2)
                        if not H.has_edge(edge):
                            H.add_edge(edge)
        #H.show()
        # Kazda krawedz G ma zawierac sie w H.
        for edge in self.G.iteredges():
            self.assertTrue(H.has_edge(edge))

    def test_path_property(self):
        # Szukam krancowego worka degree 1.
        for bag in self.T.iternodes():
            if self.T.degree(bag) == 1:
                root_bag = bag
                break
        bag_order = []   # kolejnosc odkrywania przez BFS
        algorithm = SimpleBFS(self.T)
        algorithm.run(root_bag, pre_action=lambda node: bag_order.append(node))
        self.assertEqual(root_bag, bag_order[0])
        #print("bag_order {}".format(bag_order))
        # Dla kazdego wierzcholka grafu G buduje subpath (list).
        subpath = dict((node, []) for node in self.G.iternodes())
        # Zaczynam pierwsze subpath.
        for node in root_bag:
            subpath[node].append(root_bag)
        # Przetwarzam nastepne bags.
        is_pd = True   # flaga sprawdzajaca poprawnosc PD
        for bag in bag_order[1:]:
            for node in bag:
                if len(subpath[node]) == 0:   # new subpath
                    subpath[node].append(bag)
                elif algorithm.parent[bag] == subpath[node][-1]:   # kontynuacja
                    subpath[node].append(bag)
                else:   # rozlaczne subpaths, wlasnosc nie jest spelniona
                    is_pd = False
        self.assertTrue(is_pd)
        #print("subpath {}".format(subpath))

    def test_pathwidth(self):
        pathwidth = max(len(bag) for bag in self.T.iternodes()) -1
        self.assertEqual(pathwidth, 2)

    def tearDown(self): pass

if __name__ == "__main__":

    unittest.main()

# EOF
