# -*- coding: utf-8 -*-
from __future__ import division#what is up with float division in python2? get outta here
import networkx as nx
import graphviz as gv
import math
import random

'''Maybe I just lack the Python know-how, but the best way to deal with these seemed to be to keep them global and just let the program run with them.'''
nodes = []
Nmin = 0
Nmax = 0
Ni = 0
graph = nx.Graph()
prop_graph = nx.Graph()#keep the proposal graph up-to-date with regular graph
states = {}#an empty dict, will be used to track our states.

def read_file(infile):
    '''This function reads in the list of nodes from an input file of specified name, and builds the list of nodes, as well as setting the max and min number of edges possible for the graph .'''
    global nodes
    global Nmin
    global Nmax
    if(len(nodes) != 0):#in case it gets called more than once for some reason
        del nodes[:]
    with open(infile) as f:
        for i in f:
            nodes.append((tuple(map(float,i.split(',')))))
    Nmin = (len(nodes) - 1) #the minimum number of edges is n-1
    Nmax = len(nodes) * (len(nodes) -1)/ 2 #the most edges we can have is n(n-1)/2



def distance(p1, p2):#takes tuples p1 and p2
    '''This function takes in two 2D tuples and returns the Euclidean distance between them. Used to assign weights to graph edges.'''
    return(math.sqrt((p1[0]-p2[0])**2 + (p1[1] - p2[1])**2))

def make_graph():
    '''This function creates our initial graph and proposal graph (which are identical except when proposing state changes) from the nodes list. Right now this just creates a minimal, linear graph, since that makes an easy starting point. Calling additional times after the first will reset the graph and proposal graph to the initial state.'''
    global graph
    global prop_graph
    global Nmin#need to modify the actual graph
    global nodes
    graph.clear()#in case make_graph is called repeatedly -- this is for tests
    prop_graph.clear()#in case make_graph is called repeatedly -- this is for tests
    #print("nodes is {}".format(nodes))
    #print("nmin is {}".format(Nmin))
    for i in range(Nmin):#for now, I'm just putting the tuples in a line
        graph.add_edge(i, i+1, weight=distance(nodes[i], nodes[i+1]))
        prop_graph.add_edge(i, i+1, weight=distance(nodes[i], nodes[i+1]))

def new_edge(graph, idx1, idx2):
    '''This function takes two indices on the graph and adds an edge between them, with the weight given by the Euclidean distance between the points corresponding to the given indices. Lucky for me, the networkx.Graph object already ignores duplicate edges on a graph, so I don't have to check for that.'''
    graph.add_edge(idx1, idx2, weight=distance(nodes[idx1], nodes[idx2]))

def cut_edge(graph, idx1, idx2):
    '''This function takes two indices on the graph and cuts the edge between them, if that edge exists and is not a bridge.'''
    if(idx1 in graph.neighbors(idx2) and ( len(graph.neighbors(idx1)) > 1 and len(graph.neighbors(idx2)) > 1)):#make sure we only try to remove if it's there
        graph.remove_edge(idx1,idx2)

def add_or_cut(testing = False):
    '''This function is used to determine whether we will add an edge or cut an edge at each MCMC step. The probability of adding an edge is inversely proportional to the number of edges. When we have the minimum number of edges in a connected simple graph (N - 1), P(add) is 1, and when we have the maximum number of edges (N * (N - 1)/2), the probability is 0. The exact formula can be found in the documentation.'''
    global graph
    global Nmax
    global Nmin
    #this is 1 when current edge count is minimal, and 0 when current edge count is maximal
    prob_add = ( Nmax - graph.number_of_edges() ) / ( Nmax - Nmin )
    rand = random.random()#roll the dice
    #if testing:#during tests, make sure RNG is working
    #    print("rand is {}".format(rand))
    if ( rand < prob_add ):
        return 1 #1 for add
    else:
        return 0 #0 for subtract

def get_bridges(graph):
    cycle_list = nx.cycle_basis(graph)
    bridges = []
    for edge in graph.edges():
        if(len(cycle_list) == 0):
            #print("All edges are bridges!")
            return(graph.edges())
        for cycle in cycle_list:
            p1, p2 = edge[0], edge[1]
            in_cycle = False
            for i in range(len(cycle)):
                if ((p1 == cycle[i] and p2 == cycle[(i+1)%len(cycle)]) or (p2 == cycle[i] and p1 == cycle[(i+1)%len(cycle)])):
                    #print("{} is in the cycle {}".format(edge,cycle))
                    in_cycle = True 
            if not in_cycle:
                #print("{} is a bridge!".format(edge))
                bridges.append(edge)
    return bridges
    
def propose_new():
    '''This is the meat of the MCMC algorithm. This will take the current graph configuration and propose a modification to it by either subtracting or adding a qualifying edge (from the proposal grpah), with probability of adding inversely proportional to the amount of edges (0 if we have max number of edges, 1 if we have min number of edges). After this function is called, we accept or reject the move with probability (pi_j * q(i|j))/(pi_i * q(j|i)). NOTE: This proposal distribution will never propose that the next state be unchanged, and so the system will only remain in a given state based on the '''
    global prop_graph
    node_count = prop_graph.number_of_nodes()
    if add_or_cut() == 1:
        #time to add
        pt1, pt2 = random.randint(0, node_count - 1), random.randint(0, node_count - 1)
        #make sure they don't come out the same, and that the edge doesn't already exist
        #this implementation is a bit slow right now but it works...
        while(pt1 == pt2 or (pt1 in prop_graph.neighbors(pt2))):
            pt1 = random.randint(0, node_count - 1)
            pt2 = random.randint(0, node_count - 1)
        #now we should have two random unconnected points
        new_edge(prop_graph, pt1, pt2)
    else:
        #time to cut
        bridges = get_bridges(prop_graph)#need the list of bridges to ensure we pick a good cut
        non_bridges = list(set(prop_graph.edges()) - set(bridges))
        #print("the non-bridge elements are {}".format(non_bridges))
        target_idx = random.randint(0,len(non_bridges)-1)
        cut_edge(prop_graph, non_bridges[target_idx][0], non_bridges[target_idx][1])

    return

def get_q(graph1, graph2):
    '''This calculates the q(j|i) or q(i|j) term in our MCMC acceptance ratio. See the README for more info. Call with graph first and prop_graph second for q(j|i) (forward) and vice-versa for q(i|j) (reverse).'''
    global graph
    global prop_graph
    global Nmin
    global Nmax
    prob_add = ( Nmax - graph1.number_of_edges() ) / ( Nmax - Nmin )#the probability we add an edge
    if graph2.number_of_edges() > graph1.number_of_edges():
        #we proposed an addition
        prob_edge = 1 / ( Nmax - graph1.number_of_edges() )#the probability we pick any one edge
        return ( prob_add * prob_edge )
    else:#graph2.number_of_edges() < graph1.number_of_edges
        prob_cut = float(1.0) - prob_add
        bridges = get_bridges(graph2)#need the list of bridges for prob_edge
        prob_edge = float(1.0) / ( graph1.number_of_edges() - len(bridges) )
        return ( prob_cut * prob_edge )

def record_state():
    '''This is the function used to track the states the Markov Chain has visited so far, and keep a running count of them. The counts will be used for statistics at the end.'''
    global states
    global graph
    #this effectively generates an adjacency matrix for me:
    adjacencies = nx.get_edge_attributes(graph, 'weight')
    hashable = frozenset(adjacencies)
    if(hashable not in states):
        states[hashable] = 1#initialize a new entry, with one count
    else:
        states[hashable] += 1#add one to the existing entry
