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
import copy


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
        assert graphmcmc.Nmax == 15
        
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
            assert graphmcmc.add_or_cut() == 1#we expect to always add to this minimal graph
        graphmcmc.graph.add_edge(0,2)#now the graph has maximal connections
        for i in range(100):
            assert graphmcmc.add_or_cut() == 0

    def test_get_bridges(self):
        '''This tests the get_bridges function to ensure that it returns all the bridges of a few simple graphs.'''
        testgraph = nx.Graph()#just use pure graphs for testing
        testgraph.add_edge(0,1)
        testgraph.add_edge(0,2)
        testgraph.add_edge(0,3)
        testgraph.add_edge(0,4)
        bridges = graphmcmc.get_bridges(testgraph)
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
        graphmcmc.propose_new()
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
        '''This tests to make sure our record_states() function counts graph occurrences correctly.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert len(graphmcmc.states) == 1
        #pretend we stayed at this state for testing
        graphmcmc.record_state()
        assert len(graphmcmc.states) == 1
        assert graphmcmc.states[frozenset(nx.get_edge_attributes(graphmcmc.graph, 'weight'))] == 2
        graphmcmc.new_edge(graphmcmc.graph, 0,2)
        graphmcmc.record_state()
        assert len(graphmcmc.states) == 2
        assert graphmcmc.states[frozenset(nx.get_edge_attributes(graphmcmc.graph, 'weight'))] == 1

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

    def test_different_theta(self):
        '''A sanity check to make sure the theta for two different graphs differ.'''
        test_graph = nx.Graph()
        test_graph2 = nx.Graph()
        for i in range(9):
            test_graph.add_edge(i,i+1,weight=1)
            test_graph2.add_edge(i,i+1,weight=1)
        test_graph.add_edge(9,10,weight=1)
        test_graph2.add_edge(9,10,weight=0.1)
        theta1 = graphmcmc.get_theta(test_graph)
        theta2 = graphmcmc.get_theta(test_graph2)
        assert (theta1 != theta2)

    def test_get_pi_frac(self):
        '''This checks that our pi_i/pi_j function works on a pair of simple graphs.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.propose_new()
        assert (graphmcmc.get_pi_frac() - math.exp(-2 * graphmcmc.r / graphmcmc.T) < 0.0001)

    def test_update(self):
        '''This tests to make sure we can update our two graphs appropriately. When we accept a move, should update graph, and when we reject a move, should revert prop_graph. There are four cases to test: when we move forward with a cut, forward with an addition, when we revert a cut, and when we revert an addition.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.propose_new()#propose an addition.
        graphmcmc.update(False)#we should revert the proposal graph now...
        assert graphmcmc.graph.number_of_edges() == graphmcmc.prop_graph.number_of_edges()
        assert graphmcmc.graph.number_of_edges() == 2

        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.propose_new()
        graphmcmc.update(True)#pretend we accepted
        assert graphmcmc.graph.number_of_edges() == graphmcmc.prop_graph.number_of_edges()
        assert graphmcmc.graph.number_of_edges() == 3

        #can go right into testing the cutting:
        graphmcmc.propose_new()
        graphmcmc.update(False)
        assert graphmcmc.graph.number_of_edges() == graphmcmc.prop_graph.number_of_edges()
        assert graphmcmc.graph.number_of_edges() == 3

        graphmcmc.propose_new()
        graphmcmc.update(True)
        assert graphmcmc.graph.number_of_edges() == graphmcmc.prop_graph.number_of_edges()
        assert graphmcmc.graph.number_of_edges() == 2
        
    def test_accept_move(self):
        '''This checks whether our accept/reject function works appropriately.'''
        testfile = 'next_test.txt'
        #this testfile only has one possible initial move,
        #but three possible moves after the initial acceptance happens
        #so if we run 1000 steps, we should almost certainly have non-zero, non-always acceptance
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        tot = 0
        for i in range(1000):
            graphmcmc.propose_new()
            if(graphmcmc.accept_move()):
                graphmcmc.update(True)
                tot += 1
            else:
                graphmcmc.update(False)
                tot -= 1
        assert tot != 1000
        assert tot != 0

    def test_step(self):
        '''This is a sanity test to make sure step() changes the graphs the way we expect. This is arguably not a unit test per se, but an integrated test, since step() just implements several functions already called.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        orig_zero_sum = copy.deepcopy(graphmcmc.zero_degree_sum)
        orig_edge_sum = copy.deepcopy(graphmcmc.edge_sum)
        orig_long_sum = copy.deepcopy(graphmcmc.long_short_sum)
        graphmcmc.step()
        assert graphmcmc.graph.number_of_edges() == 3
        assert graphmcmc.prop_graph.number_of_edges() == 3#should have made a move
        assert graphmcmc.zero_degree_sum > orig_zero_sum
        assert graphmcmc.zero_degree_sum == 3#should have added one edge. 1 + 2 == 3
        assert graphmcmc.edge_sum > orig_edge_sum
        assert graphmcmc.edge_sum == 5#should have added one edge. 2 + 3 == 5
        assert graphmcmc.long_short_sum > orig_long_sum
        assert graphmcmc.long_short_sum == 4
        #also need to make sure the number of states in states has increased.
        assert (len(graphmcmc.states) == 2 or graphmcmc.states[frozenset(nx.get_edge_attributes(graphmcmc.graph, 'weight'))] == 2)

    def test_track_zero_degree(self):
        '''This makes sure that we're keeping track of the degree of the 0-node at each step.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert graphmcmc.zero_degree_sum == 1

    def test_track_number_edges(self):
        '''This makes sure that we're keeping track of the total number of edges in the graph at each step.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert graphmcmc.edge_sum == 2

    def test_get_longest_shortest(self):
        '''This tests the function to get the longest shortest path in the graph. (The longest path that is a shortest path from 0 to some index.)'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert (graphmcmc.get_longest_shortest(graphmcmc.graph) - 2) < 0.0001#float testing, y'all

    def test_track_longest_shortest(self):
        '''This tests to make sure now that we can get the longest-shortest-path in a graph, that we adequately keep a running sum for our updates.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        assert (graphmcmc.long_short_sum - 2) < 0.0001

    def test_run(self):
        '''This tests to make sure our program can run for a given number of steps without weird behavior. This also is mostly just a 'does it work' test.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.run(2)#run only 2 steps
        #either we went forward one and then back, or we saw two new states
        assert len(graphmcmc.states) == 2 or len(graphmcmc.states) == 3

        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.run(99)#now we'll really make sure record_states works...
        #use 99 here for testing because we already record one state during initialization
        total = 0
        for item in graphmcmc.states:
            total += graphmcmc.states[item]
        assert total == 100

    def test_stats(self):
        '''This tests that our statistics-generating function is working as intended, using a knowable one-step chain.'''
        testfile = 'next_test.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.run(1)#we'll have been to exactly 2 states
        stats = graphmcmc.get_stats(2)
        assert (stats[0] - 1.5) < 0.0001#the expected degree of vertex 0
        assert (stats[1] - 2.5) < 0.0001#the expected number of edges
        assert (stats[2] - 2.0) < 0.0001#the expected length of the longest shortest path

    def test_get_top_percent(self):
        '''This tests that we can return the top 1% most likely graphs from among all graphs visited. Again, this is not tenable to 'really' test, so this is more of a does-it-work/integrated test.'''
        testfile = 'test_infile.txt'
        graphmcmc.read_file(testfile)
        graphmcmc.make_graph()
        graphmcmc.run(1000)
        besties = graphmcmc.get_top_percent(graphmcmc.states)
        assert len(besties) > 0
