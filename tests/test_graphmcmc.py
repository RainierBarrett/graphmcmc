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


class TestGraphmcmc(unittest.TestCase):

    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_printout(self):#just something to get me started
        assert graphmcmc.output() == 1

    
    def test_read_file(self):
        '''This tests that we can read an input file into a list of nodes'''
        test_infile = 'test_infile.txt'#an included test infile with some touples.
        graphmcmc.read_file(test_infile)
        self.assertTrue(graphmcmc.nodes)#make sure the list of nodes isn't empty
        

    def test_command_line_interface(self):
        runner = CliRunner()
        result = runner.invoke(cli.main)
        assert result.exit_code == 0
        assert 'graphmcmc.cli.main' in result.output
        help_result = runner.invoke(cli.main, ['--help'])
        assert help_result.exit_code == 0
        assert '--help  Show this message and exit.' in help_result.output
