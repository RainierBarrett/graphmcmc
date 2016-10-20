# -*- coding: utf-8 -*-
import networkx as nx
import graphviz as gv

def output():#this was just a way to let me understand python testing. Nice and easy.
    return(1)

nodes = []

def read_file(infile):
    with open(infile) as f:
        for i in f:
            nodes.append(tuple(map(float,i.split(','))))
