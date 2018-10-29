"""
Runs reduction rules to generate data/preprocessed/ from data/sanitized/
"""

import networkx as nx
from pathlib import Path
import time
import datetime

from src.preprocessing.graphs import (
    read_edgelist,
    write_edgelist,
    write_huffner,
    write_snap,
    open_path,
    reset_labels,
    names_in_dir
)
from src.preprocessing.oct import oct_reductions
from src.preprocessing.vc import vc_reductions


def _create_preprocessing_dirs():
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


def _write_summary_header(csv_filename):
    with open_path(csv_filename, 'w') as outfile:
        outfile.write('{},{},{},{},{},{},{},{},{}\n'.format(
            'Dataset',
            'original_vertices',
            'original_edges',
            'vertices_removed',
            'edges_removed',
            'oct',
            'bipartite',
            'final_vertices',
            'final_edges'))


def _write_summary(graph, output_dir, csv_filename):
    """
    Append a summary line to a csv file.
    """
    with open_path(output_dir / csv_filename, 'a') as outfile:
        outfile.write('{},{},{},{},{},{},{},{},{}\n'.format(
            graph.graph['name'],
            graph.graph['original_vertices'],
            graph.graph['original_edges'],
            graph.graph['vertices_removed'],
            graph.graph['edges_removed'],
            graph.graph['oct'],
            graph.graph['bipartite'],
            graph.order(),
            graph.size()))


def _write_oct_set(graph, oct_set, output_dir):
    """
    Write the oct vertices that were preprocessed out of the original graph.
    """
    name = '{}.oct'.format(graph.graph['name'])
    with open_path(output_dir / name, 'w') as outfile:
        for vertex in oct_set:
            outfile.write('{}\n'.format(vertex))


def _write_name_lookup(graph, output_dir):
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


def _convert_synthetic(data_names):
    # Define some directories-of-interest paths
    input_dir = Path('.') / 'data' / 'sanitized'
    output_dir = Path('.') / 'data' / 'preprocessed'

    # Remove the old statistics CSV
    summary_dir = Path(output_dir / 'summary')
    summary_filename = summary_dir / 'synthetic.csv'
    if summary_filename.is_file():
        Path(summary_filename).unlink()
    else:
        summary_dir.mkdir(exist_ok=True, parents=True)

    _write_summary_header(summary_filename)

    # Convert datasets
    for dataset in data_names:
        timestamp = datetime.\
                    datetime.\
                    fromtimestamp(time.time()).strftime('%Y/%m/%d-%H:%M:%S:')
        print('{} Processing {}'.format(timestamp, dataset))

        # Process the graph
        graph = read_edgelist(input_dir / 'edgelist', dataset)
        graph = reset_labels(graph)
        graph.graph['original_vertices'] = graph.order()
        graph.graph['original_edges'] = graph.size()

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
            write_snap(graph, output_dir / 'snap')
            changed, graph, oct_set = vc_reductions(graph, oct_set)
            if changed:
                print("-- VC reduced graph")
                graph_reduced = True

        # Write the results
        graph = reset_labels(graph)
        _write_summary(graph, output_dir / 'summary', 'synthetic.csv')
        _write_oct_set(graph, oct_set, output_dir / 'oct')
        _write_name_lookup(graph, output_dir / 'lookup')
        write_edgelist(graph, output_dir / 'edgelist')
        write_huffner(graph, output_dir / 'huffner')
        write_snap(graph, output_dir / 'snap')
    print('Finished preprocessing synthetic data')


if __name__ == '__main__':
    """
    Runs preprocessing on all synthetic graphs.
    """

    # Compute the synthetic graph names and preprocess
    _create_preprocessing_dirs()
    input_dir = Path('.') / 'data' / 'sanitized' / 'edgelist'
    datasets = names_in_dir(input_dir, '.edgelist')
    # Quantum data has no dashes, synthetics use dashes to separate parameters
    datasets = sorted(list(filter(lambda x: '-' in x, datasets)))
    print('Preprocessing {} datasets'.format(len(datasets)))
    _convert_synthetic(datasets)
