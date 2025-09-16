#!/usr/bin/env python3

import unittest
from graphtheory.structures.edges import Edge
from graphtheory.structures.graphs import Graph
from graphtheory.flow.fordfulkerson import FordFulkerson
from graphtheory.flow.fordfulkerson import FordFulkersonSparse
from graphtheory.flow.fordfulkerson import FordFulkersonWithEdges
from graphtheory.flow.fordfulkerson import FordFulkersonRecursive
from graphtheory.flow.fordfulkerson import FordFulkersonRecursiveWithEdges

#     10
#  0 ---o 1
#  |   /  |
#10|  /1  |10
#  o o    o
#  2 ---o 3
#     10

class TestMaximumFlow1(unittest.TestCase):

    def setUp(self):
        self.N = 4           # number of nodes
        self.G = Graph(n=self.N, directed=True)
        self.nodes = range(self.N)
        self.edges = [
            Edge(0, 1, 10), Edge(0, 2, 10), Edge(1, 2, 1), Edge(1, 3, 10), 
            Edge(2, 3, 10)]
        for node in self.nodes:
            self.G.add_node(node)
        for edge in self.edges:
            self.G.add_edge(edge)
        #self.G.show()

    def test_ford_fulkerson(self):
        algorithm = FordFulkerson(self.G)
        algorithm.run(0, 3)
        expected_max_flow = 20
        expected_flow = {
            0: {0: 0, 2: 10, 1: 10, 3: 0}, 
            1: {0: -10, 2: 0, 1: 0, 3: 10}, 
            2: {0: -10, 2: 0, 1: 0, 3: 10}, 
            3: {0: 0, 2: -10, 1: -10, 3: 0}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_sparse(self):
        algorithm = FordFulkersonSparse(self.G)
        algorithm.run(0, 3)
        expected_max_flow = 20
        expected_flow = {
            0: {1: 10, 2: 10},
            1: {0: -10, 2: 0, 3: 10},
            2: {0: -10, 1: 0, 3: 10},
            3: {1: -10, 2: -10}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_with_edges(self):
        algorithm = FordFulkersonWithEdges(self.G)
        algorithm.run(0, 3)
        expected_max_flow = 20
        expected_flow = {
            Edge(0, 1, 10): 10, Edge(0, 2, 10): 10,
            Edge(1, 0, 0): -10, Edge(1, 2): 0, Edge(1, 3, 10): 10,
            Edge(2, 0, 0): -10, Edge(2, 1, 0): 0, Edge(2, 3, 10): 10,
            Edge(3, 1, 0): -10, Edge(3, 2, 0): -10}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_recursive(self):
        algorithm = FordFulkersonRecursive(self.G)
        algorithm.run(0, 3)
        expected_max_flow = 20
        expected_flow = {
            0: {0: 0, 2: 10, 1: 10, 3: 0}, 
            1: {0: -10, 2: 0, 1: 0, 3: 10}, 
            2: {0: -10, 2: 0, 1: 0, 3: 10}, 
            3: {0: 0, 2: -10, 1: -10, 3: 0}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_recursive_with_edges(self):
        algorithm = FordFulkersonRecursiveWithEdges(self.G)
        algorithm.run(0, 3)
        expected_max_flow = 20
        expected_flow = {
            Edge(0, 1, 10): 10, Edge(0, 2, 10): 10,
            Edge(1, 0, 0): -10, Edge(1, 2): 0, Edge(1, 3, 10): 10,
            Edge(2, 0, 0): -10, Edge(2, 1, 0): 0, Edge(2, 3, 10): 10,
            Edge(3, 1, 0): -10, Edge(3, 2, 0): -10}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

# https://en.wikipedia.org/wiki/Edmonds%E2%80%93Karp_algorithm
#
# 0 ----o 3 --o 5
# | o   o |     |
# |  \ /  |     |
# |   2   |     |
# |  o \  |     |
# | /   o |     o
# 1 o---- 4 --o 6

class TestMaximumFlow2(unittest.TestCase):

    def setUp(self):
        self.N = 7           # number of nodes
        self.G = Graph(n=self.N, directed=True)
        self.nodes = range(self.N)
        self.edges = [
            Edge(0, 1, 3), Edge(0, 3, 3), Edge(1, 2, 4), Edge(2, 0, 3), 
            Edge(2, 3, 1), Edge(2, 4, 2), Edge(3, 4, 2), Edge(3, 5, 6), 
            Edge(4, 1, 1), Edge(4, 6, 1), Edge(5, 6, 9)]
        for node in self.nodes:
            self.G.add_node(node)
        for edge in self.edges:
            self.G.add_edge(edge)
        #self.G.show()

    def test_ford_fulkerson(self):
        algorithm = FordFulkerson(self.G)
        algorithm.run(0, 6)
        expected_max_flow = 5
        expected_flow = {
            0: {0: 0, 2: 0, 1: 2, 4: 0, 3: 3, 6: 0, 5: 0}, 
            1: {0: -2, 2: 2, 1: 0, 4: 0, 3: 0, 6: 0, 5: 0}, 
            2: {0: 0, 2: 0, 1: -2, 4: 1, 3: 1, 6: 0, 5: 0}, 
            3: {0: -3, 2: -1, 1: 0, 4: 0, 3: 0, 6: 0, 5: 4}, 
            4: {0: 0, 2: -1, 1: 0, 4: 0, 3: 0, 6: 1, 5: 0}, 
            5: {0: 0, 2: 0, 1: 0, 4: 0, 3: -4, 6: 4, 5: 0}, 
            6: {0: 0, 2: 0, 1: 0, 4: -1, 3: 0, 6: 0, 5: -4}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_sparse(self):
        algorithm = FordFulkersonSparse(self.G)
        algorithm.run(0, 6)
        expected_max_flow = 5
        expected_flow = {
            0: {1: 2, 2: 0, 3: 3},
            1: {0: -2, 2: 2, 4: 0},
            2: {0: 0, 1: -2, 3: 1, 4: 1},
            3: {0: -3, 2: -1, 4: 0, 5: 4},
            4: {1: 0, 2: -1, 3: 0, 6: 1},
            5: {3: -4, 6: 4},
            6: {4: -1, 5: -4}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_with_edges(self):
        algorithm = FordFulkersonWithEdges(self.G)
        algorithm.run(0, 6)
        expected_max_flow = 5
        expected_flow = {
            Edge(0, 1, 3): 2, Edge(0, 2, 0): 0, Edge(0, 3, 3): 3,
            Edge(1, 0, 0): -2, Edge(1, 2, 4): 2, Edge(1, 4, 0): 0,
            Edge(2, 0, 3): 0, Edge(2, 1, 0): -2, 
            Edge(2, 3): 1, Edge(2, 4, 2): 1,
            Edge(3, 0, 0): -3, Edge(3, 2, 0): -1,
            Edge(3, 4, 2): 0, Edge(3, 5, 6): 4,
            Edge(4, 1): 0, Edge(4, 2, 0): -1,
            Edge(4, 3, 0): 0, Edge(4, 6): 1,
            Edge(5, 3, 0): -4, Edge(5, 6, 9): 4,
            Edge(6, 4, 0): -1, Edge(6, 5, 0): -4}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_recursive(self):
        algorithm = FordFulkersonRecursive(self.G)
        algorithm.run(0, 6)
        expected_max_flow = 5
        expected_flow = {
            0: {0: 0, 1: 2, 2: 0, 3: 3, 4: 0, 5: 0, 6: 0},
            1: {0: -2, 1: 0, 2: 2, 3: 0, 4: 0, 5: 0, 6: 0},
            2: {0: 0, 1: -2, 2: 0, 3: 1, 4: 1, 5: 0, 6: 0},
            3: {0: -3, 1: 0, 2: -1, 3: 0, 4: 0, 5: 4, 6: 0},
            4: {0: 0, 1: 0, 2: -1, 3: 0, 4: 0, 5: 0, 6: 1},
            5: {0: 0, 1: 0, 2: 0, 3: -4, 4: 0, 5: 0, 6: 4},
            6: {0: 0, 1: 0, 2: 0, 3: 0, 4: -1, 5: -4, 6: 0}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_recursive_with_edges(self):
        algorithm = FordFulkersonRecursiveWithEdges(self.G)
        algorithm.run(0, 6)
        expected_max_flow = 5
        expected_flow = {
            Edge(0, 1, 3): 2, Edge(0, 2, 0): 0, Edge(0, 3, 3): 3,
            Edge(1, 0, 0): -2, Edge(1, 2, 4): 2, Edge(1, 4, 0): 0,
            Edge(2, 0, 3): 0, Edge(2, 1, 0): -2,
            Edge(2, 3): 1, Edge(2, 4, 2): 1,
            Edge(3, 0, 0): -3, Edge(3, 2, 0): -1,
            Edge(3, 4, 2): 0, Edge(3, 5, 6): 4,
            Edge(4, 1): 0, Edge(4, 2, 0): -1,
            Edge(4, 3, 0): 0, Edge(4, 6): 1,
            Edge(5, 3, 0): -4, Edge(5, 6, 9): 4,
            Edge(6, 4, 0): -1, Edge(6, 5, 0): -4}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

#    10     4      10
# 0 ---o 1 ---o 3 ---o 5
#    \   |  \   o   o
#   10\  |2  \8 |6 /10
#      o o    o | /
#        2 ---o 4
#           9

class TestMaximumFlow3(unittest.TestCase):

    def setUp(self):
        self.N = 6           # number of nodes
        self.G = Graph(n=self.N, directed=True)
        self.nodes = range(self.N)
        self.edges = [
            Edge(0, 1, 10), Edge(0, 2, 10), Edge(1, 2, 2), Edge(1, 3, 4), 
            Edge(1, 4, 8), Edge(2, 4, 9), Edge(4, 3, 6), Edge(4, 5, 10), 
            Edge(3, 5, 10)]
        for node in self.nodes:
            self.G.add_node(node)
        for edge in self.edges:
            self.G.add_edge(edge)
        #self.G.show()

    def test_ford_fulkerson(self):
        algorithm = FordFulkerson(self.G)
        algorithm.run(0, 5)
        expected_max_flow = 19
        expected_flow = {
            0: {0: 0, 1: 10, 2: 9, 3: 0, 4: 0, 5: 0},
            1: {0: -10, 1: 0, 2: 0, 3: 4, 4: 6, 5: 0},
            2: {0: -9, 1: 0, 2: 0, 3: 0, 4: 9, 5: 0},
            3: {0: 0, 1: -4, 2: 0, 3: 0, 4: -5, 5: 9},
            4: {0: 0, 1: -6, 2: -9, 3: 5, 4: 0, 5: 10},
            5: {0: 0, 1: 0, 2: 0, 3: -9, 4: -10, 5: 0}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_sparse(self):
        algorithm = FordFulkersonSparse(self.G)
        algorithm.run(0, 5)
        expected_max_flow = 19
        expected_flow = {
            0: {1: 10, 2: 9},
            1: {0: -10, 2: 0, 3: 4, 4: 6},
            2: {0: -9, 1: 0, 4: 9},
            3: {1: -4, 4: -5, 5: 9},
            4: {1: -6, 2: -9, 3: 5, 5: 10},
            5: {3: -9, 4: -10}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_with_edges(self):
        algorithm = FordFulkersonWithEdges(self.G)
        algorithm.run(0, 5)
        expected_max_flow = 19
        expected_flow = {
            Edge(0, 1, 10): 10, Edge(0, 2, 10): 9,
            Edge(1, 0, 0): -10, Edge(1, 2, 2): 0,
            Edge(1, 3, 4): 4, Edge(1, 4, 8): 6,
            Edge(2, 0, 0): -9, Edge(2, 1, 0): 0, Edge(2, 4, 9): 9,
            Edge(3, 1, 0): -4, Edge(3, 4, 0): -5, Edge(3, 5, 10): 9,
            Edge(4, 1, 0): -6, Edge(4, 2, 0): -9,
            Edge(4, 3, 6): 5, Edge(4, 5, 10): 10,
            Edge(5, 3, 0): -9, Edge(5, 4, 0): -10}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_recursive(self):
        algorithm = FordFulkersonRecursive(self.G)
        algorithm.run(0, 5)
        expected_max_flow = 19
        expected_flow = {
            0: {0: 0, 1: 10, 2: 9, 3: 0, 4: 0, 5: 0},
            1: {0: -10, 1: 0, 2: 0, 3: 4, 4: 6, 5: 0},
            2: {0: -9, 1: 0, 2: 0, 3: 0, 4: 9, 5: 0},
            3: {0: 0, 1: -4, 2: 0, 3: 0, 4: -6, 5: 10},
            4: {0: 0, 1: -6, 2: -9, 3: 6, 4: 0, 5: 9},
            5: {0: 0, 1: 0, 2: 0, 3: -10, 4: -9, 5: 0}}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_ford_fulkerson_recursive_with_edges(self):
        algorithm = FordFulkersonRecursiveWithEdges(self.G)
        algorithm.run(0, 5)
        expected_max_flow = 19
        expected_flow = {
            Edge(0, 1, 10): 10, Edge(0, 2, 10): 9,
            Edge(1, 0, 0): -10, Edge(1, 2, 2): 0,
            Edge(1, 3, 4): 4, Edge(1, 4, 8): 6,
            Edge(2, 0, 0): -9, Edge(2, 1, 0): 0, Edge(2, 4, 9): 9,
            Edge(3, 1, 0): -4, Edge(3, 4, 0): -6, Edge(3, 5, 10): 10,
            Edge(4, 1, 0): -6, Edge(4, 2, 0): -9,
            Edge(4, 3, 6): 6, Edge(4, 5, 10): 9,
            Edge(5, 3, 0): -10, Edge(5, 4, 0): -9}
        self.assertEqual(algorithm.max_flow, expected_max_flow)
        self.assertEqual(algorithm.flow, expected_flow)

    def test_exceptions(self):
        self.assertRaises(ValueError, FordFulkerson, Graph())
        self.assertRaises(ValueError, FordFulkersonSparse, Graph())
        self.assertRaises(ValueError, FordFulkersonWithEdges, Graph())
        self.assertRaises(ValueError, FordFulkersonRecursive, Graph())
        self.assertRaises(ValueError, lambda: FordFulkerson(self.G).run(0,0))
        self.assertRaises(ValueError, lambda: FordFulkersonSparse(self.G).run(0,0))
        self.assertRaises(ValueError, lambda: FordFulkersonWithEdges(self.G).run(0,0))
        self.assertRaises(ValueError, lambda: FordFulkersonRecursive(self.G).run(0,0))
        self.assertRaises(ValueError, lambda: FordFulkersonRecursiveWithEdges(self.G).run(0,0))

if __name__ == "__main__":

    unittest.main()

# EOF
