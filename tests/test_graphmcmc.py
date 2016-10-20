#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
test_graphmcmc
----------------------------------

Tests for `graphmcmc` module.
"""


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
    test_infile = 'test_infile.txt'#an included test infile with some touples.
    def setUp(self):
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
        '''This tests that we are able to make a connected graph out of our input nodes, and that it is random (the connections should be different each time).'''
        graphmcmc.read_file(self.test_infile)
        graphmcmc.make_graph()
        assert isinstance(graphmcmc.graph, nx.Graph)
        assert nx.is_connected(graphmcmc.graph)

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'graphmcmc.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
