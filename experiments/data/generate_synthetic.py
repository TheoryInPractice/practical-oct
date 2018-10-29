"""
A collection of methods for generating synthetic data to mimic attributes of
real-world data.
"""

import argparse
from itertools import chain, combinations, product
import math
import networkx as nx
from pathlib import Path
import random
import scipy.special

from src.preprocessing.graphs import (
    read_edgelist,
    write_edgelist,
    write_huffner,
    write_snap,
    reset_labels,
    names_in_dir
)


def _populate_oct_upper_bound_lookup():
    """
    Generate a dictionary mapping a (quantum) graph name to its min OCT value.
    """
    file_path = (Path('.') / 'experiments' / 'data' /
                 'quantum_precomputed_oct.csv')
    oct_upper_bound = {}
    with open(str(file_path), 'r') as infile:
        # Discard header
        infile.readline()
        # Populate loookup table
        for line in infile.readlines():
            line = line.split(',')
            dataset = line[0]
            size = int(line[3])
            oct_upper_bound[dataset] = size
    return oct_upper_bound


def _generate_er(qubo, seed):
    """
    Given a QUBO, generate an Erdos-Renyi graph matching the number of
    vertices and edges (in expectation)
    """
    # Compute parameters needed for model
    n = qubo.order()
    p = qubo.size() / scipy.special.binom(n, 2)
    # Generate graph
    graph = nx.erdos_renyi_graph(n=n, p=p, seed=seed)
    # Name the graph
    graph.graph['name'] = '{}-{}-{}'.format(qubo.graph['name'], 'er', seed)
    # Sanitize the graph and return
    graph = reset_labels(graph)
    return graph


def _generate_to(qubo, seed, oct_upper_bound, bias=0.5):
    """
    Given a QUBO, an upper bound on oct, and a bias of bipartite vertices,
    generate an Erdos-Renyi graph such that oct_upper_bound number of vertices
    form an OCT set and the remaining vertices are partitioned into partites
    (left partite set with probability of "bias"). Edges between the partite
    sets are then removed.
    """
    # Compute parameters needed for ER
    n = qubo.order()
    p = qubo.size() / scipy.special.binom(n, 2)
    # Generate graph
    graph = nx.erdos_renyi_graph(n=n, p=p, seed=seed)
    random.seed(seed)
    # Compute partite sets on the remaining vertices
    nodes = list(graph.nodes())[oct_upper_bound:]
    partite1 = set()
    partite2 = set()
    for node in nodes:
        if random.random() < bias:
            partite1.add(node)
        else:
            partite2.add(node)
    # Remove edges within a partite set
    for edge in chain(combinations(partite1, 2), combinations(partite2, 2)):
        if graph.has_edge(*edge):
            graph.remove_edge(*edge)
    # Name the graph
    graph.graph['name'] = '{}-{}-{}'.format(qubo.graph['name'], 'to', seed)
    # Sanitize the graph and return
    graph = reset_labels(graph)
    return graph


def _generate_cl(qubo, seed):
    """Generate a Chung-Lu graph that matches a graph's degree distriubtion"""
    # Compute the parameters needed for CL
    degree_distribution = sorted([qubo.degree(node) for node in qubo.nodes()])
    # Generate graph
    graph = nx.expected_degree_graph(w=degree_distribution,
                                     selfloops=False,
                                     seed=seed)
    # Name the graph
    graph.graph['name'] = '{}-{}-{}'.format(qubo.graph['name'], 'cl', seed)
    # Sanitize the graph and return
    graph = reset_labels(graph)
    return graph


def _generate_ba(qubo, seed):
    """Generate Barabasi-Albert graph such that each new edge has 'edge
        density' neighbors"""
    # Compute the parameters needed for BA
    n = qubo.order()
    m = math.ceil(qubo.size() / n)
    # Generate graph
    graph = nx.barabasi_albert_graph(n=n, m=m, seed=seed)
    # Name the graph
    graph.graph['name'] = '{}-{}-{}'.format(qubo.graph['name'], 'ba', seed)
    # Sanitize the graph and return
    graph = reset_labels(graph)
    return graph


if __name__ == '__main__':
    # Read existing graphs from the sanitized folder
    sanitized_dir = Path('.') / 'data' / 'sanitized'
    input_dir = sanitized_dir / 'edgelist'

    # Obtain the number of seeds
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('-seeds', type=int, nargs='+',
                        help='The graph generator seeds')
    args = parser.parse_args()

    # Obtain the names of the quantum graphs already sanitized
    datasets = names_in_dir(input_dir, '.edgelist')
    # Keep only the non-synthetic data
    datasets = sorted(list(filter(lambda x: '-' not in x, datasets)))

    # Read in the pre-computed optimal OCT sizes
    oct_upper_bound = _populate_oct_upper_bound_lookup()

    # For every dataset and seed, generate a synthetic graph with each model
    for dataset, seed in product(datasets, args.seeds):
        print('For {} and seed {}'.format(dataset, seed))
        # Generate the sanitized ER random graph
        print('- Generating Erdos-Renyi')
        graph = read_edgelist(input_dir, dataset)
        er_graph = _generate_er(graph, seed)
        reset_labels(er_graph)
        # Write the graph
        write_edgelist(er_graph, sanitized_dir / 'edgelist')
        write_huffner(er_graph, sanitized_dir / 'huffner')
        write_snap(er_graph, sanitized_dir / 'snap')

        # Generate the sanitized CL random graph
        print('- Generating Chung-Lu')
        graph = read_edgelist(input_dir, dataset)
        cl_graph = _generate_cl(graph, seed)
        reset_labels(cl_graph)
        # Write the graph
        write_edgelist(cl_graph, sanitized_dir / 'edgelist')
        write_huffner(cl_graph, sanitized_dir / 'huffner')
        write_snap(cl_graph, sanitized_dir / 'snap')

        # Generate the sanitized BA random graph
        print('- Generating Barabasi-Albert')
        graph = read_edgelist(input_dir, dataset)
        ba_graph = _generate_ba(graph, seed)
        reset_labels(ba_graph)
        # Write the graph
        write_edgelist(ba_graph, sanitized_dir / 'edgelist')
        write_huffner(ba_graph, sanitized_dir / 'huffner')
        write_snap(ba_graph, sanitized_dir / 'snap')

        # Generate the sanitized TO random graph
        print('- Generating Tunable OCT')
        graph = read_edgelist(input_dir, dataset)
        upper_bound = oct_upper_bound[graph.graph['name']]
        to_graph = _generate_to(graph, seed, upper_bound)
        reset_labels(to_graph)
        # Write the graph
        write_edgelist(to_graph, sanitized_dir / 'edgelist')
        write_huffner(to_graph, sanitized_dir / 'huffner')
        write_snap(to_graph, sanitized_dir / 'snap')
