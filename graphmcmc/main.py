from graphmcmc import *

read_file('../input.txt')
make_graph()
print("Running. This may take some time...\n")
run(10000)
best_graphs = list(get_top_percent())
print("Here are the edge lists of some example graphs from the top 1% of graphs in this chain:\n")
for item in best_graphs:
    print(list(item))
