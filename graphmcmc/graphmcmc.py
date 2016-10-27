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
zero_degree_sum = 0#this will be used for one of the stats we're asked to calculate
edges_sum = 0#this will be used for one of the stats we're asked to calculate
long_short_sum = 0#this will be used for one of the stats we're asked to calculate
r = 0.0#this is the weight of the total-path-length in our MCMC 'energy'
T = 1.0#this is the 'temperature' in our Metropolis-Hastings algorithm
top_percent = []#this will hold the "best" graphs

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
    Nmax = (len(nodes) * (len(nodes) -1))/ 2 #the most edges we can have is n(n-1)/2



def distance(p1, p2):#takes tuples p1 and p2
    '''This function takes in two 2D tuples and returns the Euclidean distance between them. Used to assign weights to graph edges.'''
    return(math.sqrt((p1[0]-p2[0])**2 + (p1[1] - p2[1])**2))

def make_graph():
    '''This function creates our initial graph and proposal graph (which are identical except when proposing state changes) from the nodes list. Right now this just creates a minimal, linear graph, since that makes an easy starting point. Calling additional times after the first will reset the graph and proposal graph to the initial state.'''
    global graph
    global prop_graph
    global Nmin#need to modify the actual graph
    global nodes
    global zero_degree_sum
    global edge_sum
    global long_short_sum
    global states
    zero_degree_sum = 0#reset these just in case, when we make a new graph
    edge_sum = 0
    long_short_sum = 0
    states.clear()
    graph.clear()#in case make_graph is called repeatedly -- this is for tests
    prop_graph.clear()#in case make_graph is called repeatedly -- this is for tests
    for i in range(Nmin):#for now, I'm just putting the tuples in a line
        graph.add_edge(i, i+1, weight=distance(nodes[i], nodes[i+1]))
        prop_graph.add_edge(i, i+1, weight=distance(nodes[i], nodes[i+1]))
    zero_degree_sum += len(graph.neighbors(0))
    edge_sum += graph.number_of_edges()
    long_short_sum += get_longest_shortest(graph)
    record_state()
    

def new_edge(graph, idx1, idx2):
    '''This function takes two indices on the graph and adds an edge between them, with the weight given by the Euclidean distance between the points corresponding to the given indices. Lucky for me, the networkx.Graph object already ignores duplicate edges on a graph, so I don't have to check for that.'''
    graph.add_edge(idx1, idx2, weight=distance(nodes[idx1], nodes[idx2]))

def cut_edge(graph, idx1, idx2):
    '''This function takes two indices on the graph and cuts the edge between them, if that edge exists and is not a bridge.'''
    if(idx1 in graph.neighbors(idx2) and ( len(graph.neighbors(idx1)) > 1 and len(graph.neighbors(idx2)) > 1)):#make sure we only try to remove if it's there
        graph.remove_edge(idx1,idx2)

def add_or_cut():
    '''This function is used to determine whether we will add an edge or cut an edge at each MCMC step. The probability of adding an edge is inversely proportional to the number of edges. When we have the minimum number of edges in a connected simple graph (N - 1), P(add) is 1, and when we have the maximum number of edges (N * (N - 1)/2), the probability is 0. The exact formula can be found in the documentation.'''
    global graph
    global Nmax
    global Nmin
    #this is 1 when current edge count is minimal, and 0 when current edge count is maximal
    prob_add = ( Nmax - graph.number_of_edges() ) / ( Nmax - Nmin )
    rand = random.random()#roll the dice
    if ( rand < prob_add ):
        return True #1 for add
    else:
        return False #0 for subtract

def get_bridges(graph):
    cycle_list = nx.cycle_basis(graph)
    bridges = []
    for edge in graph.edges():
        if(len(cycle_list) == 0):
            return(graph.edges())
        for cycle in cycle_list:
            p1, p2 = edge[0], edge[1]
            in_cycle = False
            for i in range(len(cycle)):
                if ((p1 == cycle[i] and p2 == cycle[(i+1)%len(cycle)]) or (p2 == cycle[i] and p1 == cycle[(i+1)%len(cycle)])):
                    in_cycle = True 
            if not in_cycle:
                bridges.append(edge)
    return bridges
    
def propose_new():
    '''This is the meat of the MCMC algorithm. This will take the current graph configuration and propose a modification to it by either subtracting or adding a qualifying edge (from the proposal grpah), with probability of adding inversely proportional to the amount of edges (0 if we have max number of edges, 1 if we have min number of edges). After this function is called, we accept or reject the move with probability (pi_j * q(i|j))/(pi_i * q(j|i)). NOTE: This proposal distribution will never propose that the next state be unchanged, and so the system will only remain in a given state based on the Metropolis-Hastings algorithms' rejection chance.'''
    global graph
    global prop_graph
    node_count = prop_graph.number_of_nodes()
    if add_or_cut():
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
        while(graph.number_of_edges() == prop_graph.number_of_edges()):
            pt1 = random.randint(0, node_count - 1)
            pt2 = random.randint(0, node_count - 1)
            cut_edge(prop_graph, pt1, pt2)
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
        prob_edge = (float(1.0) / ( graph1.number_of_edges() - len(bridges) )) if ( graph1.number_of_edges() - len(bridges) ) > 0 else 0
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

def get_longest_shortest(graph):
    '''This function gets the length of the longest-shortest path in the given graph. Used for statistics in assignment.'''
    #this just gives us a dict keyed by index with value minimal-path-length to it:
    shortest_paths = nx.single_source_dijkstra_path_length(graph,0,weight='weight')
    maximum = 0
    for item in shortest_paths:#just look at all the dict items
        maximum = max(0, shortest_paths[item])
    return maximum

def get_theta(graph):
    '''This function calculates the theta of a given graph based on the Boltzmann-style formula given in the assignment.'''
    global r
    shortest_paths = nx.single_source_dijkstra_path_length(graph,0,weight='weight')
    term1 = 0
    term2 = 0
    for item in shortest_paths:
        term2 += shortest_paths[item]
    edge_weights = nx.get_edge_attributes(graph, 'weight')
    for edge in edge_weights:
        term1 += edge_weights[edge]
    return (r * term1 + term2)

def get_pi_frac(graph1 = graph, graph2 = prop_graph, T = T):
    '''This function gets the pi_j/pi_i term for the Metropolis-Hastings update step.'''
    th1 = get_theta(graph1)
    th2 = get_theta(graph2)
    return(math.exp(-(th1 - th2)/T))

def update( forward ):
    '''This function will update graph and prop_graph based on whether forward is True (graph becomes identical to prop_graph) or False (prop_graph reverts to graph).'''
    global graph
    global prop_graph
    if(forward == True):
        if(graph.number_of_edges() < prop_graph.number_of_edges()):
            #we're moving forward with an addition
            edge_difference = list(set(prop_graph.edges()) - set(graph.edges()))
            #now edge_difference is a list of length 1 containing the edge graph needs
            new_edge(graph, edge_difference[0][0], edge_difference[0][1])
            #now graph matches prop_graph again, and we can continue
        elif(graph.number_of_edges() > prop_graph.number_of_edges()):
            #we're moving forward with a cut
            edge_difference = list(set(graph.edges()) - set(prop_graph.edges()))
            cut_edge(graph, edge_difference[0][0], edge_difference[0][1])
    else:
        #we need to revert prop_graph to graph
        if(graph.number_of_edges() < prop_graph.number_of_edges()):
            #prop_graph is too big, cut the offending edge
            edge_difference = list(set(prop_graph.edges()) - set(graph.edges()))
            cut_edge(prop_graph, edge_difference[0][0], edge_difference[0][1])
        else:
            #prop_graph has a cut we need to undo
            edge_difference = list(set(graph.edges()) - set(prop_graph.edges()))
            new_edge(prop_graph, edge_difference[0][0], edge_difference[0][1])

def accept_move(graph1 = graph, graph2 = prop_graph):
    '''This is the Metropolis-Hastings acceptance/rejection function.'''
    pi_frac = get_pi_frac()
    q_ij = get_q(graph1, graph2)
    q_ji = get_q(graph2, graph1)
    a_ij = min((pi_frac * q_ij/q_ji), 1) if q_ji > 0 else 1
    rand = random.random()
    if(rand < a_ij):
        return(True)
    else:
        return(False)

def step():
    '''This function is the step-maker. Called once each timestep, it calls propose_new(), determines whether the move is acceptable with accept_move(), then update()s appropriately. It also records the state we've now moved to, and adds to our running statistic totals after it finishes stepping.'''
    global graph
    global prop_graph
    global long_short_sum
    global zero_degree_sum
    global edge_sum
    propose_new()
    forward = accept_move()
    update(forward)
    record_state()
    long_short_sum += get_longest_shortest(graph)
    zero_degree_sum += len(graph.neighbors(0))
    edge_sum += graph.number_of_edges()

def get_stats(nsteps):
    global edge_sum
    global zero_degree_sum
    global long_short_sum
    stats = []
    stats.append(float(zero_degree_sum)/float(nsteps))
    stats.append(float(edge_sum)/float(nsteps))
    stats.append(float(long_short_sum)/float(nsteps))
    return(stats)
    
def run(nsteps):
    global graph
    for i in range(nsteps):
        step()
    stats = get_stats(nsteps)
    print("The expected degree of vertex 0 is: {}\nThe expected number of total edges in a graph is: {}\nThe expected length of the largest shortest path from 0 to any other vertex is: {}\n".format(stats[0],stats[1],stats[2]))
    
def get_top_percent(graph_dict):
    '''This function treats our list of states and orders them by the number of times each has occurred, then outputs the top 1% of them in that ordering.'''
    tuples = graph_dict.items()
    count = 0
    top_percent = []
    while(count < len(graph_dict)/100):
        current_max = 0
        current_best = {}
        #find the biggest count left, and track the graph it goes with.
        for item in tuples:
            if item[1] > current_max:
                current_max = item[1]
                current_best = item[0]
        count += current_max
        top_percent.append(current_best)
    return(list(top_percent))
