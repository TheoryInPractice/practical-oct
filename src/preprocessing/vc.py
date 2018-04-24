"""
To be filled in with a Python script that calls the modified akiba-iwata
subfolder.

"""

import subprocess
import networkx as nx


def vc_reductions(graph, oct_set):
    output = subprocess.run(
        args=['java', '-cp', 'src/preprocessing/akiba-iwata/bin', 'Main',
              'data/preprocessed/snap/{}.snap'.format(
              graph.graph['name']), '-r', '3'],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=True)
    output = output.stdout.decode("utf-8").split("\n")
    oct_vertices = list(map(int, output[0].split()[1:]))
    bipartite_vertices = list(map(int, output[1].split()[1:]))
    # remaining_vertices = list(map(int, output[2].split()[1:]))

    # Update the bipartite vertices
    og_name_lookup = nx.get_node_attributes(graph, 'og_name')

    for vertex in oct_vertices:
        # Update the OCT set and graph
        oct_set.add(og_name_lookup[vertex])
        graph.graph['oct'] += 1
        graph.remove_node(vertex)

    for vertex in bipartite_vertices:
        graph.add_node(vertex, bipartite=True, og_name=og_name_lookup[vertex])

    graph_reduced = len(oct_vertices) != 0

    return graph_reduced, graph, oct_set
    # print("Data: {}\nOCT: {}\nBipartite: {}\nRest: {}".format(
    #     dataset, oct_set, bipartite_set, rest))
