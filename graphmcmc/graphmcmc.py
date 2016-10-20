# -*- coding: utf-8 -*-
import networkx as nx
import graphviz as gv
import math

nodes = []
Nmin = 0
Nmax = 0
Ni = 0

def read_file(infile):
    global nodes
    global Nmin
    global Nmax
    if(len(nodes) != 0):#in case it gets called more than once for some reason
        nodes = []
    with open(infile) as f:
        for i in f:
            nodes.append((tuple(map(float,i.split(',')))))
    Nmin = (len(nodes) - 1) #the minimum number of edges is n-1
    Nmax = len(nodes) * (len(nodes) -1)/ 2 #the most edges we can have is n(n-1)/2

graph = nx.Graph()

def distance(p1, p2):#takes tuples p1 and p2
    return(math.sqrt((p1[0]-p2[0])**2 + (p1[1] - p2[1])**2))

def make_graph():
    global graph
    global Nmin#need to modify the actual graph
    global nodes
    print("nodes is {}".format(nodes))
    print("nmin is {}".format(Nmin))
    for i in range(Nmin):#for now, I'm just putting the tuples in a line
        graph.add_edge(i, i+1, weight=distance(nodes[i], nodes[i+1]))

def new_edge(idx1, idx2):
    global graph
    graph.add_edge(idx1, idx2, weight=distance(nodes[idx1], nodes[idx2]))

def cut_edge(idx1, idx2):
    global graph
    if(idx1 in graph.neighbors(idx2) and ( len(graph.neighbors(idx1)) > 1 and len(graph.neighbors(idx2)) > 1)):#make sure we only try to remove if it's there
        graph.remove_edge(idx1,idx2)

