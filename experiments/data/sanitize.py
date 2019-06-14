"""
Sanitizes the graphs in data/original/ and writes in needed formats to
data/converted/
"""
from pathlib import Path
from itertools import chain
from src.preprocessing.graphs import (
    read_beasley,
    read_huffner,
    write_edgelist,
    write_huffner,
    write_snap,
    reset_labels,
    names_in_dir,
)


def _create_sanitized_dirs(sanitized_dir):
    """
    Creates the directories needed for sanitized data.
    """
    # Make directories if they do not exist
    Path(sanitized_dir / 'edgelist').mkdir(parents=True, exist_ok=True)
    Path(sanitized_dir / 'huffner').mkdir(parents=True, exist_ok=True)
    Path(sanitized_dir / 'snap').mkdir(parents=True, exist_ok=True)


def _sanitize_huffner(original_dir, sanitized_dir):
    """
    Sanitize all graphs in the original/huffner/ directory.
    """
    # Identify the Huffner data
    data_names = sorted(names_in_dir(original_dir / 'huffner', '.graph'))
    print('Identified {} Huffner files'.format(len(data_names)))

    # Convert datasets
    for dataset in data_names:
        # Sanitize the graph and write
        print('Sanitizing', dataset)
        graph = read_huffner(original_dir / 'huffner', dataset + '.graph')
        graph = reset_labels(graph)
        write_edgelist(graph, sanitized_dir / 'edgelist')
        write_huffner(graph, sanitized_dir / 'huffner')
        write_snap(graph, sanitized_dir / 'snap')
    print('Sanitized Huffner data')


def _sanitize_select_beasley(original_dir, sanitized_dir, data_names):
    """
    Sanitize select graphs in the origina/beasley/ directory.
    """
    for dataset in data_names:
        # Sanitize the graph and write
        print('Sanitizing', dataset)
        graph = read_beasley(original_dir / 'beasley', dataset + '.txt')
        graph = reset_labels(graph)
        write_edgelist(graph, sanitized_dir / 'edgelist')
        write_huffner(graph, sanitized_dir / 'huffner')
        write_snap(graph, sanitized_dir / 'snap')
    print('Preprocessed Beasley data')


def _sanitize_select_gka(original_dir, sanitized_dir, data_names):
    for dataset in data_names:
        # Sanitize the graph and write
        print('Sanitizing', dataset)
        graph = read_beasley(original_dir / 'gka', dataset + '.txt')
        graph = reset_labels(graph)
        write_edgelist(graph, sanitized_dir / 'edgelist')
        write_huffner(graph, sanitized_dir / 'huffner')
        write_snap(graph, sanitized_dir / 'snap')
    print('Preprocessed GKA data')


if __name__ == '__main__':
    """
    Populates data/converted/ from a previously downloaded and parsed
    data/original/.
    """
    # Define some directories-of-interest paths
    original_dir = Path('.') / 'data' / 'original'
    sanitized_dir = Path('.') / 'data' / 'sanitized'

    # We begin with selecting data
    # For Huffner take all .graph files and no work needs to be done
    # For Beasley take all bqp50 and bqp100 graphs
    beasley_data = chain(['bqp50_{}'.format(i) for i in range(1, 11)],
                         ['bqp100_{}'.format(i) for i in range(1, 11)])
    # For GKA keep graphs 1 through 35
    gka_data = ['gka_{}'.format(i) for i in range(1, 36)]

    # We then sanitize and write to data/converted/
    _create_sanitized_dirs(sanitized_dir)
    _sanitize_huffner(original_dir, sanitized_dir)
    _sanitize_select_beasley(original_dir, sanitized_dir, beasley_data)
    _sanitize_select_gka(original_dir, sanitized_dir, gka_data)
