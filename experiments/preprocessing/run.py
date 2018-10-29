"""
Runs reduction rules to generate data/preprocessed/ from data/converted/
"""

import networkx as nx
from pathlib import Path
import subprocess
import time

from experiments import PREPROCESSED_DATA_DIR
from src.preprocessing.graphs import (
    read_beasley,
    read_huffner,
    write_edgelist,
    write_huffner,
    write_snap,
    open_path,
    reset_labels,
    names_in_dir,
    convert_oct_set,
    load_pre_oct_set,
    load_og_name_lookup
)
from src.preprocessing.oct import oct_reductions
from src.preprocessing.vc import vc_reductions


def write_oct_set(graph, oct_set, output_dir):
    """
    Write the oct vertices that were preprocessed out of the original graph.
    """
    name = '{}.oct'.format(graph.graph['name'])
    with open_path(output_dir / name, 'w') as outfile:
        for vertex in oct_set:
            outfile.write('{}\n'.format(vertex))


def write_name_lookup(graph, output_dir):
    """
    Write a lookup table of preprocessed vertices to original names.
    Each line is [new_name] [original_name].
    """
    name = '{}.lookup'.format(graph.graph['name'])

    og_name_lookup = nx.get_node_attributes(graph, 'og_name')
    # print("Nodes:", graph.nodes(data=True))
    # print("Lookup:", og_name_lookup)
    with open_path(output_dir / name, 'w') as outfile:
        for vertex in graph.nodes():
            outfile.write('{} {}\n'.format(vertex, og_name_lookup[vertex]))


def write_summary(graph, output_dir, csv_filename):
    """
    Append a summary line to a csv file.
    """
    with open_path(output_dir / csv_filename, 'a') as outfile:
        outfile.write('{},{},{},{},{}\n'.format(graph.graph['name'],
                                                graph.graph['vertices_removed'],
                                                graph.graph['edges_removed'],
                                                graph.graph['oct'],
                                                graph.graph['bipartite']))


def reduce_graph(graph, oct_reductions, vc_reductions):
    # Run each type of reduction at least once
    changed = oct_reductions()
    changed = vc_reductions()

    # Reduce until no changes
    while changed:
        changed = oct_reductions()
        if changed:
            changed = vc_reductions()

    return graph


def convert_huffner():
    # Define some directories-of-interest paths
    original_dir = Path('.') / 'data' / 'original'
    preprocessed_dir = Path('.') / 'data' / 'preprocessed'

    # Huffner files we don't preprocess
    blacklist = ['aa12', 'j12', 'j27']

    # Identify the Huffner data
    data_names = sorted(filter(
        lambda n: n not in blacklist,
        names_in_dir(original_dir / 'huffner', '.graph')
    ))
    print('Identified {} Huffner files'.format(len(data_names)))

    # Convert datasets
    for dataset in data_names:
        print('Processing', dataset)
        start_time = time.time()

        # Process the graph
        graph = read_huffner(original_dir / 'huffner', dataset)
        oct_set = set()
        graph_reduced = True
        while graph_reduced:
            # Require a change for graph_reduced to be triggered again
            graph_reduced = False

            # Compute OCT reductions
            print("- Computing OCT reduction")
            graph = reset_labels(graph)
            changed, graph, oct_set = oct_reductions(graph, oct_set)

            if changed:
                print("-- OCT reduced graph")
                graph_reduced = True

            # Compute
            print("- Computing VC reduction")
            graph = reset_labels(graph)
            write_snap(graph, preprocessed_dir / 'snap')
            changed, graph, oct_set = vc_reductions(graph, oct_set)
            if changed:
                print("-- VC reduced graph")
                graph_reduced = True

        total_time = time.time() - start_time
        print('Preprocessing `{}` took {} seconds'.format(
            dataset, round(total_time, 1)
        ))
        # Write the results
        graph = reset_labels(graph)
        write_summary(graph, preprocessed_dir / 'summary', 'huffner.csv')
        write_oct_set(graph, oct_set, preprocessed_dir / 'oct')
        write_name_lookup(graph, preprocessed_dir / 'lookup')
        write_edgelist(graph, preprocessed_dir / 'edgelist')
        write_huffner(graph, preprocessed_dir / 'huffner')
        write_snap(graph, preprocessed_dir / 'snap')
    print('Preprocessed Huffner data')


def convert_beasley():
    # Define some directories-of-interest paths
    original_dir = Path('.') / 'data' / 'original'
    preprocessed_dir = Path('.') / 'data' / 'preprocessed'

    # Identify the Huffner data
    data_names = sorted(names_in_dir(original_dir / 'beasley', '.txt'))
    print('Identified {} Beasley files'.format(len(data_names)))

    # Convert datasets
    for dataset in data_names:
        print('Processing', dataset)
        start_time = time.time()

        # Process the graph
        graph = read_beasley(original_dir / 'beasley', dataset)
        oct_set = set()
        graph_reduced = True
        while graph_reduced:
            # Require a change for graph_reduced to be triggered again
            graph_reduced = False

            # Compute OCT reductions
            print("- Computing OCT reduction")
            graph = reset_labels(graph)
            changed, graph, oct_set = oct_reductions(graph, oct_set)

            if changed:
                print("-- OCT reduced graph")
                graph_reduced = True

            # Compute
            print("- Computing VC reduction")
            graph = reset_labels(graph)
            write_snap(graph, preprocessed_dir / 'snap')
            changed, graph, oct_set = vc_reductions(graph, oct_set)
            if changed:
                print("-- VC reduced graph")
                graph_reduced = True

        # Write the results
        total_time = time.time() - start_time
        print('Preprocessing `{}` took {} seconds'.format(
            dataset, round(total_time, 1)
        ))
        graph = reset_labels(graph)
        write_summary(graph, preprocessed_dir / 'summary', 'beasley.csv')
        write_oct_set(graph, oct_set, preprocessed_dir / 'oct')
        write_name_lookup(graph, preprocessed_dir / 'lookup')
        write_edgelist(graph, preprocessed_dir / 'edgelist')
        write_huffner(graph, preprocessed_dir / 'huffner')
        write_snap(graph, preprocessed_dir / 'snap')
    print('Preprocessed Beasley data')


def convert_select_beasley(data_names):
    # Define some directories-of-interest paths
    original_dir = Path('.') / 'data' / 'original'
    preprocessed_dir = Path('.') / 'data' / 'preprocessed'

    # Remove the old statistics CSV
    if Path(preprocessed_dir / 'summary' / 'beasley.csv').is_file():
        Path(preprocessed_dir / 'summary' / 'beasley.csv').unlink()

    # Convert datasets
    for dataset in data_names:
        print('Processing', dataset)
        start_time = time.time()

        # Process the graph
        graph = read_beasley(original_dir / 'beasley', dataset)
        oct_set = set()
        graph_reduced = True
        while graph_reduced:
            # Require a change for graph_reduced to be triggered again
            graph_reduced = False

            # Compute OCT reductions
            print("- Computing OCT reduction")
            graph = reset_labels(graph)
            changed, graph, oct_set = oct_reductions(graph, oct_set)

            if changed:
                print("-- OCT reduced graph")
                graph_reduced = True

            # Compute
            print("- Computing VC reduction")
            graph = reset_labels(graph)
            write_snap(graph, preprocessed_dir / 'snap')
            changed, graph, oct_set = vc_reductions(graph, oct_set)
            if changed:
                print("-- VC reduced graph")
                graph_reduced = True

        # Write the results
        total_time = time.time() - start_time
        print('Preprocessing `{}` took {} seconds'.format(
            dataset, round(total_time, 1)
        ))
        graph = reset_labels(graph)
        write_summary(graph, preprocessed_dir / 'summary', 'beasley.csv')
        write_oct_set(graph, oct_set, preprocessed_dir / 'oct')
        write_name_lookup(graph, preprocessed_dir / 'lookup')
        write_edgelist(graph, preprocessed_dir / 'edgelist')
        write_huffner(graph, preprocessed_dir / 'huffner')
        write_snap(graph, preprocessed_dir / 'snap')
    print('Preprocessed Beasley data')


def convert_gka():
    # Define some directories-of-interest paths
    original_dir = Path('.') / 'data' / 'original'
    preprocessed_dir = Path('.') / 'data' / 'preprocessed'

    # Identify the Huffner data
    data_names = sorted(names_in_dir(original_dir / 'gka', '.txt'))
    print('Identified {} GKA files'.format(len(data_names)))

    # Convert datasets
    for dataset in data_names:
        print('Processing', dataset)
        start_time = time.time()

        # Process the graph
        graph = read_beasley(original_dir / 'gka', dataset)
        oct_set = set()
        graph_reduced = True
        while graph_reduced:
            # Require a change for graph_reduced to be triggered again
            graph_reduced = False

            # Compute OCT reductions
            print("- Computing OCT reduction")
            graph = reset_labels(graph)
            changed, graph, oct_set = oct_reductions(graph, oct_set)

            if changed:
                print("-- OCT reduced graph")
                graph_reduced = True

            # Compute
            print("- Computing VC reduction")
            graph = reset_labels(graph)
            write_snap(graph, preprocessed_dir / 'snap')
            changed, graph, oct_set = vc_reductions(graph, oct_set)
            if changed:
                print("-- VC reduced graph")
                graph_reduced = True

        # Write the results
        total_time = time.time() - start_time
        print('Preprocessing `{}` took {} seconds'.format(
            dataset, round(total_time, 1)
        ))
        graph = reset_labels(graph)
        write_summary(graph, preprocessed_dir / 'summary', 'gka.csv')
        write_oct_set(graph, oct_set, preprocessed_dir / 'oct')
        write_name_lookup(graph, preprocessed_dir / 'lookup')
        write_edgelist(graph, preprocessed_dir / 'edgelist')
        write_huffner(graph, preprocessed_dir / 'huffner')
        write_snap(graph, preprocessed_dir / 'snap')
    print('Preprocessed GKA data')


def convert_select_gka(data_names):
    # Define some directories-of-interest paths
    original_dir = Path('.') / 'data' / 'original'
    preprocessed_dir = Path('.') / 'data' / 'preprocessed'

    # Remove the old statistics CSV
    if Path(preprocessed_dir / 'summary' / 'gka.csv').is_file():
        Path(preprocessed_dir / 'summary' / 'gka.csv').unlink()

    # Convert datasets
    for dataset in data_names:
        print('Processing', dataset)
        start_time = time.time()

        # Process the graph
        graph = read_beasley(original_dir / 'gka', dataset)
        oct_set = set()
        graph_reduced = True
        while graph_reduced:
            # Require a change for graph_reduced to be triggered again
            graph_reduced = False

            # Compute OCT reductions
            print("- Computing OCT reduction")
            graph = reset_labels(graph)
            changed, graph, oct_set = oct_reductions(graph, oct_set)

            if changed:
                print("-- OCT reduced graph")
                graph_reduced = True

            # Compute
            print("- Computing VC reduction")
            graph = reset_labels(graph)
            write_snap(graph, preprocessed_dir / 'snap')
            changed, graph, oct_set = vc_reductions(graph, oct_set)
            if changed:
                print("-- VC reduced graph")
                graph_reduced = True

        # Write the results
        total_time = time.time() - start_time
        print('Preprocessing `{}` took {} seconds'.format(
            dataset, round(total_time, 1)
        ))
        graph = reset_labels(graph)
        write_summary(graph, preprocessed_dir / 'summary', 'gka.csv')
        write_oct_set(graph, oct_set, preprocessed_dir / 'oct')
        write_name_lookup(graph, preprocessed_dir / 'lookup')
        write_edgelist(graph, preprocessed_dir / 'edgelist')
        write_huffner(graph, preprocessed_dir / 'huffner')
        write_snap(graph, preprocessed_dir / 'snap')
    print('Preprocessed GKA data')


def create_dirs():
    """
    Creates the directories needed for preprocessed data.
    """
    preprocessed_dir = Path('.') / 'data' / 'preprocessed'

    # Make directories if they do not exist
    Path(preprocessed_dir / 'summary').mkdir(parents=True, exist_ok=True)
    Path(preprocessed_dir / 'oct').mkdir(parents=True, exist_ok=True)
    Path(preprocessed_dir / 'lookup').mkdir(parents=True, exist_ok=True)
    Path(preprocessed_dir / 'edgelist').mkdir(parents=True, exist_ok=True)
    Path(preprocessed_dir / 'huffner').mkdir(parents=True, exist_ok=True)
    Path(preprocessed_dir / 'snap').mkdir(parents=True, exist_ok=True)


def call_huffner(filename):
    HUFFNER = './src/huffner-src/occ'
    DATA = 'data/preprocessed/huffner/{}'.format(filename)
    try:
        output = subprocess.check_output('{} < {} -b'.format(HUFFNER, DATA),
                              stderr=subprocess.STDOUT, shell=True)
        oct_set = output.decode('utf-8').split()
        return oct_set
    except:
        print('Something went wrong with Huffner call')


def call_akiba_iwata(filename):
    try:
        output = subprocess.run(
            args=['java', '-cp', 'src/akiba-iwata-src/bin', 'Main',
                  'data/preprocessed/snap/{}.snap'.format(
                  filename), '-r', '3', '-p'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True)

        # Pull the number of vertices from stderr
        err = output.stderr.decode('utf-8').split('\n')
        num_vertices = int(err[1].split(',')[0].split()[-1])

        # Pull the Vertex Cover from stdout
        output = output.stdout.decode("utf-8").split("\n")
        vc_set = list(map(int, output[1:-1]))

        # Construct the OCT set by looking at a vertex and its mirror
        oct_set = set()
        shift = num_vertices // 2
        for vertex in range(0, shift):
            if vertex in vc_set and vertex + shift in vc_set:
                oct_set.add(str(vertex))

        # Return the OCT set
        return oct_set
    except Exception as e:
        print(e)
        print('Something went wrong with Akiba-Iwata call')


def verify(pre_oct_set, oct_set, graph):
    """
    Returns whether the preprocessed OCT vertices (pre_oct_set) and the proposed oct_set are really an OCT set.
    """
    # Remove the OCT set
    if pre_oct_set:
        graph.remove_nodes_from(pre_oct_set)
    if oct_set:
        graph.remove_nodes_from(oct_set)

    return nx.is_bipartite(graph)


def validate_preprocesing(filename, data_type):
    """
    Once a preprocessed dataset has been written, validate that it is a valid preprocessing by (a) computing an optimal OCT set on the preprocessed graph using Huffner and (b) checking that the preprocessed OCT set plus the Huffner OCT set is actually an OCT set on the full graph.
    """

    # Define some directories of interest
    data_dir = Path('.') / 'data'
    oct_dir = data_dir / 'preprocessed' / 'oct'
    lookup_dir = data_dir / 'preprocessed' / 'lookup'
    og_dir = data_dir / 'original' / data_type

    # Pick a graph reader based on the data type
    if data_type == 'huffner':
        reader = read_huffner
        extension = 'graph'
    elif data_type == 'beasley' or data_type == 'gka':
        reader = read_beasley
        extension = 'txt'
    else:
        reader = None
        raise ValueError('data_type not supported')

    # Load the two OCT sets and graph
    og_names = load_og_name_lookup(lookup_dir, '{}.lookup'.format(filename))
    pre_oct_set = load_pre_oct_set(oct_dir, '{}.oct'.format(filename))
    # oct_set = call_huffner('{}.huffner'.format(filename))
    oct_set = call_akiba_iwata(filename)
    oct_set = convert_oct_set(oct_set, og_names)
    graph = reader(og_dir, '{}.{}'.format(filename, extension))

    # print("Pre OCT is", pre_oct_set)
    # print("OCT is", oct_set)
    # print("Original graph has {} nodes and {} edges".format(graph.order(), graph.size()))
    # print("OG nodes:", graph.nodes())

    # Check if these OCT sets are valid together
    if verify(pre_oct_set, oct_set, graph):
        print('{} is valid, minOCT = {} (pre={})'.format(filename, len(pre_oct_set) + len(oct_set), len(pre_oct_set)))
    else:
        print("pre_oct: {} oct: {}".format(str(pre_oct_set), str(oct_set)))
        raise ValueError('Invalid OCT set!')


if __name__ == '__main__':
    """
    Assumes that the experiment is called from the root directory.
    """

    # Write summary file headers
    summry_dir = PREPROCESSED_DATA_DIR / 'summary'
    summry_dir.mkdir(exist_ok=True, parents=True)
    summary_headers = [
        'name', 'vertices_removed',
        'edges_removed', 'oct', 'bipartite'
    ]
    for s in ['beasley.csv', 'gka.csv', 'huffner.csv']:
        f = summry_dir / s
        with open(str(f), 'w') as summary:
            summary.write(','.join(summary_headers))

    # Preprocess all data
    create_dirs()
    convert_huffner()
    convert_select_beasley(['{}.txt'.format(x) for x in beasley_data])
    convert_select_gka(['{}.txt'.format(x) for x in gka_data])

    for dataset in huffner_data:
        validate_preprocesing(dataset, 'huffner')
    for dataset in beasley_data:
        validate_preprocesing(dataset, 'beasley')
    for dataset in gka_data:
        validate_preprocesing(dataset, 'gka')
