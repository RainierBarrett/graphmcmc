#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_graphmcmc
----------------------------------

Tests for `graphmcmc` module.
"""

from __future__ import division
import sys
import unittest
from contextlib import contextmanager
from click.testing import CliRunner

from graphmcmc import graphmcmc
from graphmcmc import cli
import networkx as nx
import graphviz as gv
import math


class TestGraphmcmc(unittest.TestCase):
    test_infile = 'test_infile.txt'#an included test infile with some tuples.
    def setUp(self):#I'm not sure if the testing library needs these or not, so they're here
        pass

    def tearDown(self):
        pass

    def test_read_file(self):
        '''This tests that we can read an input file into a list of nodes'''
        #this is a copy of the test input file, list-tuple-ified
        tuples = [(0.000,0.000),
                  (1.000,0.000),
                  (0.000,1.000),
                  (1.000,1.000),
                  (1.500,0.000),
                  (0.750,1.250)]

        graphmcmc.read_file(self.test_infile)
        self.assertTrue(graphmcmc.nodes)#make sure the list of nodes isn't empty
        for i in range(len(tuples)):
            assert isinstance(graphmcmc.nodes[i], tuple)#make sure it's a list of tuples
            for j in range(2):
                assert isinstance(graphmcmc.nodes[i][j], float)#make sure they're tuples of floats
        assert len(graphmcmc.nodes) == 6#make sure it's the right size
        for i in  range(len(tuples)):
            assert tuples[i] == graphmcmc.nodes[i]
        print('\n', tuples, ' == ', graphmcmc.nodes)
        
    def test_distance(self):
        '''This tests the distance function is working properly for a variety of inputs'''
        assert graphmcmc.distance((0,0), (1,1)) == math.sqrt(2)
        assert graphmcmc.distance((0,0), (1,0)) == 1
        assert graphmcmc.distance((-1,-1), (0,-1)) == 1
        assert graphmcmc.distance((0.5,-1.5), (-1.25,3.5)) == math.sqrt(25+(1.75)**2)


    def test_make_graph(self):
        '''This tests that we are able to make a connected graph out of our input nodes, and that the weights are correct.'''
        graphmcmc.read_file(self.test_infile)
        graphmcmc.make_graph()
        assert isinstance(graphmcmc.graph, nx.Graph)
        assert nx.is_connected(graphmcmc.graph)
        #check all the weights worked (though I technically already tested this in test_distance)
        assert graphmcmc.graph[0][1]['weight'] == 1
        assert graphmcmc.graph[1][2]['weight'] == math.sqrt(2)
        assert graphmcmc.graph[2][3]['weight'] == 1
        assert graphmcmc.graph[3][4]['weight'] == math.sqrt(1.25)
        assert graphmcmc.graph[4][5]['weight'] == math.sqrt(0.75**2 + 1.25**2)

    def test_new_edge(self):
        '''This tests to ensure that the new_edge function handles inserting an edge properly.'''
        #I don't need to check that it ignores multiple edges between the same vertices,
        #since that's a built-in behavior of the nx.Graph object. :)
        graphmcmc.read_file(self.test_infile)
        graphmcmc.make_graph()
        graphmcmc.new_edge(graphmcmc.graph, 2, 0)
        self.assertTrue(graphmcmc.graph[0][2])
        assert graphmcmc.graph[0][2]['weight'] == 1
        
    def test_cut_edge(self):
        '''This tests to ensure that removing an edge works properly for both good and bad cuts.'''
        graphmcmc.read_file(self.test_infile)
        graphmcmc.make_graph()
        graphmcmc.new_edge(graphmcmc.graph, 2, 0)
        assert graphmcmc.graph.number_of_edges() == 6
        graphmcmc.cut_edge(graphmcmc.graph, 0, 2)
        assert graphmcmc.graph.number_of_edges() == 5
        graphmcmc.cut_edge(graphmcmc.graph, 0, 2)
        assert graphmcmc.graph.number_of_edges() == 5
        graphmcmc.cut_edge(graphmcmc.graph, 0, 1)
        assert nx.is_connected(graphmcmc.graph)

    def test_add_or_cut(self):
        '''This tests whether our add_or_cut() function properly directs us to add an edge or make a cut. It should add an edge with probability 1 when the graph has the minimum number of edges, and with probability 0 when it has maximal number of edges.'''
        testfile = 'next_test.txt'#this is an input file with only three points
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()#this will make the minimally-connected graph
        for i in range(100):
            assert graphmcmc.add_or_cut(testing = True) == 1#we expect to always add to this minimal graph
        graphmcmc.graph.add_edge(0,2)#now the graph has maximal connections
        for i in range(100):
            assert graphmcmc.add_or_cut(testing = True) == 0

    def test_get_bridges(self):
        '''This tests the get_bridges function to ensure that it returns all the bridges of a few simple graphs.'''
        testgraph = nx.Graph()#just use pure graphs for testing
        testgraph.add_edge(0,1)
        testgraph.add_edge(0,2)
        testgraph.add_edge(0,3)
        testgraph.add_edge(0,4)
        bridges = graphmcmc.get_bridges(testgraph)
        #print("apparently bridges is {}".format(bridges))
        for edge in testgraph.edges():
            assert edge in bridges
        testgraph.clear()
        testgraph.add_edge(0,1)
        testgraph.add_edge(0,2)
        testgraph.add_edge(0,3)
        testgraph.add_edge(1,2)
        bridges = graphmcmc.get_bridges(testgraph)
        assert len(bridges) == 1
        assert (0,3) in bridges

        
    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'graphmcmc.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output


        
    def test_propose_new_add(self):
        '''This tests the propose_new function's add-an-edge capability on a small graph which allows only a particular mutation for the next step.'''
        testfile = 'next_test.txt'#this is an input file with only three points
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        #print("prop_graph now has edges {}".format(graphmcmc.prop_graph.edges()))
        graphmcmc.propose_new()
        #print("and now it has {}".format(graphmcmc.prop_graph.edges()))
        #only one proposal should be possible (new edge: 0-2)
        assert len(graphmcmc.prop_graph.edges()) == 3
        assert 0 in graphmcmc.prop_graph.neighbors(2)

    def test_propose_new_cut(self):
        '''This tests the propose_new functions' cut-an-edge capability on a small graph with limited configurations.'''
        testfile = 'next_test.txt'#this is an input file with only three points
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.new_edge(graphmcmc.graph, 0, 2)#make it a loop
        graphmcmc.new_edge(graphmcmc.prop_graph, 0, 2)#this too
        #now that there's a loop, there's three viable cuts (and no unviable ones)
        graphmcmc.propose_new()
        assert len(graphmcmc.prop_graph.edges()) == 2

    def test_get_q_forward(self):
        '''This tests that we get the correct probability of transitioning forward (to a proposal) from the current graph under our proposal distribution. See documentation for details.'''
        testfile = 'next_test.txt'#this is an input file with only three points
        for i in range(100):
            graphmcmc.read_file(testfile)
            graphmcmc.make_graph()
            graphmcmc.propose_new()#this changes only the proposal graph in a predictable way
            prob_forward = graphmcmc.get_q(graphmcmc.graph, graphmcmc.prop_graph)
            assert prob_forward == 1#this should be our only choice.

        testfile2 = 'q_forward_test.txt'#a second check
        for i in range(100):
            graphmcmc.read_file(testfile2)
            graphmcmc.make_graph()
            graphmcmc.propose_new()
            prob_forward = graphmcmc.get_q(graphmcmc.graph, graphmcmc.prop_graph)
            assert prob_forward == float(1.0)/float(3.0)

        testfile = 'next_test.txt'#this is an input file with only three points
        graphmcmc.read_file(testfile)
        for i in range(100):
            graphmcmc.make_graph()
            graphmcmc.new_edge(graphmcmc.graph, 0, 2)#now it's maximally-connected
            graphmcmc.new_edge(graphmcmc.prop_graph, 0, 2)
            graphmcmc.propose_new()#this changes only the proposal graph in a predictable way
            prob_forward = graphmcmc.get_q(graphmcmc.graph, graphmcmc.prop_graph)
            assert prob_forward == 1#this should be our only choice.

        testfile2 = 'q_forward_test.txt'#a second check
        for i in range(100):
            graphmcmc.read_file(testfile2)
            graphmcmc.make_graph()
            graphmcmc.new_edge(graphmcmc.graph, 0, 2)#now it's maximally-connected
            graphmcmc.new_edge(graphmcmc.prop_graph, 0, 2)
            graphmcmc.propose_new()
            prob_forward = graphmcmc.get_q(graphmcmc.graph, graphmcmc.prop_graph)
            assert (prob_forward - float(1.0)/float(3.0)) < 1 * 10 **-7

    def test_get_q_backward(self):
        '''This tests that we get the correct reverse transition probability (from a proposal to the current state) under our proposal distribution. See documentation for details.'''
        testfile = 'next_test.txt'#this is an input file with only three points
        for i in range(100):
            graphmcmc.read_file(testfile)
            graphmcmc.make_graph()
            graphmcmc.propose_new()#this changes only the proposal graph in a predictable way
            prob_forward = graphmcmc.get_q(graphmcmc.prop_graph, graphmcmc.graph)
            assert prob_forward == 1#this should be our only choice.

        testfile2 = 'q_forward_test.txt'#a second check
        for i in range(100):
            graphmcmc.read_file(testfile2)
            graphmcmc.make_graph()
            graphmcmc.propose_new()
            prob_forward = graphmcmc.get_q(graphmcmc.prop_graph, graphmcmc.graph)
            assert (prob_forward - float(1.0)/float(3.0)) < 1 * 10 **-7

        testfile = 'next_test.txt'#this is an input file with only three points
        graphmcmc.read_file(testfile)
        for i in range(100):
            graphmcmc.make_graph()
            graphmcmc.new_edge(graphmcmc.graph, 0, 2)#now it's maximally-connected
            graphmcmc.new_edge(graphmcmc.prop_graph, 0, 2)
            graphmcmc.propose_new()#this changes only the proposal graph in a predictable way
            prob_forward = graphmcmc.get_q(graphmcmc.prop_graph, graphmcmc.graph)
            assert prob_forward == 1#this should be our only choice.

        testfile2 = 'q_forward_test.txt'#a second check
        for i in range(100):
            graphmcmc.read_file(testfile2)
            graphmcmc.make_graph()
            graphmcmc.new_edge(graphmcmc.graph, 0, 2)#now it's maximally-connected
            graphmcmc.new_edge(graphmcmc.prop_graph, 0, 2)
            graphmcmc.propose_new()
            prob_forward = graphmcmc.get_q(graphmcmc.prop_graph, graphmcmc.graph)
            assert (prob_forward - float(1.0)/float(3.0)) < 1 * 10 **-7

    def test_graph_counter(self):
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.record_state()
        assert len(graphmcmc.states) == 1
        #pretend we stayed at this state for testing
        graphmcmc.record_state()
        assert len(graphmcmc.states) == 1
        assert graphmcmc.states[frozenset(nx.get_edge_attributes(graphmcmc.graph, 'weight'))] == 2
        graphmcmc.new_edge(graphmcmc.graph, 0,2)
        graphmcmc.record_state()
        assert len(graphmcmc.states) == 2
        assert graphmcmc.states[frozenset(nx.get_edge_attributes(graphmcmc.graph, 'weight'))] == 1

    def test_track_zero_degree(self):
        '''This makes sure that we're keeping track of the degree of the 0-node at each step.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert graphmcmc.zero_degree_sum == 1
        #put in test to check behavior with step() function

    def test_track_number_edges(self):
        '''This makes sure that we're keeping track of the total number of edges in the graph at each step.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert graphmcmc.edge_sum == 2
        #put in test to check behavior with step() function

    def test_get_longest_shortest(self):
        '''This tests the function to get the longest shortest path in the graph. (The longest path that is a shortest path from 0 to some index.)'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert (graphmcmc.get_longest_shortest() - 2) < 0.0001#float testing, y'all

    def test_get_theta(self):
        '''This checks that the calculated value for theta is accurate for a small control graph.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert (graphmcmc.get_theta(graphmcmc.graph) - (2.0 * graphmcmc.r + 3.0) < 0.0001)

        #here's another check on a graph I did out myself
        test_graph = nx.Graph()
        test_graph.add_edge(0,1, weight=1)
        test_graph.add_edge(1,3, weight=2)
        test_graph.add_edge(1,2, weight=0.5)
        test_graph.add_edge(3,2, weight=0.5)
        test_graph.add_edge(3,5, weight=3)
        assert (graphmcmc.get_theta(test_graph) - (graphmcmc.r * 7.0 + 9.5) < 0.0001)
