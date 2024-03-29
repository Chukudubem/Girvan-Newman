from pyspark import SparkContext
from collections import OrderedDict
import sys
import itertools

inputfile = sys.argv[1]
outputfile = sys.argv[2]
sc = SparkContext(appName = "Girvan Newman")

data = sc.textFile(inputfile)
data = data.map(lambda x: (eval(x)[0],eval(x)[1]))

g = data.collect()
node_test = sorted(list(set([i for i in g for i in i])))
parallelized_nodes = sc.parallelize(node_test, 7)

def generate_adj_matrix(iterator):
    iterator = list(iterator)
    yield (iterator[0], iterator[1])
    yield (iterator[1], iterator[0])


    
adj_matrix = data.map(generate_adj_matrix).flatMap(lambda x:x).groupByKey().map(lambda x: (x[0], set(x[1]))).collect()
dict_adj_matrix = dict(adj_matrix)



def bfs_new(node, dict_adj_matrix):
    visited_order_set, visit_order, seen, to_visit, to_visit_set = set(), list(), dict(), [node], set()
    to_visit_set.add(node)
    while(to_visit):
        vertex = to_visit.pop(0)
        to_visit_set.remove(vertex)
        if vertex == node:
            seen[node] = [[], 0]
            visit_order.append(node)
            visited_order_set.add(node)
        else:
            visit_order.append(vertex)
            visited_order_set.add(vertex)
        vertex_distance_from_root = seen[vertex][1]
        ### add predecessors in seen
        ### filtering out edges which have been already visited
        to_be_appended = dict_adj_matrix[vertex] - visited_order_set
        ### to_be_appended - to_visit_set
        ### to eliminte nodes which are already queued to be visited
        for n in to_be_appended - to_visit_set:
            to_visit_set.add(n)
            to_visit.append(n)
        for item in to_be_appended:
            if not seen.get(item):
                seen[item] = [[vertex], seen[vertex][1]+1]
            else:
                if seen[item][1] == vertex_distance_from_root + 1:
                    seen[item][0].append(vertex)
    temp_nodes = {}
    temp_edges = {}
    for inner_node in reversed(visit_order):
        inner_node_value = temp_nodes.get(inner_node)
        temp_nodes[inner_node] = inner_node_value+1 if inner_node_value else 1
        ends = seen[inner_node][0]
        current_inner_node_value = temp_nodes[inner_node]
        number_of_influenced_nodes = len(ends)
        if number_of_influenced_nodes:
            influencing_value = float(current_inner_node_value) / number_of_influenced_nodes
        for end in ends:
            end_node_value = temp_nodes.get(end)
            sorted_edge_list = sorted([inner_node, end])
            edge_name = "{} {}".format(sorted_edge_list[0], sorted_edge_list[1])
            temp_edges[edge_name] = influencing_value
            temp_nodes[end] = end_node_value+influencing_value if end_node_value else influencing_value
    return temp_edges




def girvan_newman(iterator):
    node = iterator
    global dict_adj_matrix
    return bfs_new(node, dict_adj_matrix).items()



output = parallelized_nodes.flatMap(girvan_newman).groupByKey().mapValues(lambda x: sum(x)/2).map(lambda x: (tuple([i for i in x[0].split()]),x[1])).sortByKey().collect()

with open(outputfile, 'w') as f:
    for i in output:
        f.write("({},{}),{}\n".format(i[0][0],i[0][1], i[1]))

        