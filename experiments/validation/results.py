"""Sanity check all experiment certificate results.

This script checks to make sure all results presented
in the paper (stored under `experiments/paper_results`)
are valid. I.E., the returned certificate on the
preprocessed graph is a valid certificate on the
original graph.
"""


# Imports
from experiments import (
    headers,
    ORIGINAL_DATA_DIR,
    PREPROCESSED_DATA_DIR,
    RESULTS_DIR,
    PRINT_CONTEXT,
    ORIGINAL_HUFFNER_DATA_EXT,
    BEASLEY_EXT
)
from experiments.datasets import (
    huffner_aa, huffner_j,
    preprocessed_gka, beasley_small
)
from experiments.exact import EXACT_RESULTS_DATA_PATH
from experiments.heuristic import COMBINED_RESULTS_DATA_FILE
from experiments.ic import SELF_COMPARISON_DATA_PATH, BASELINE_FILE
from experiments.ilp import ILP_RESULTS_FILE_PATH
from experiments.internal.huffner_heuristics_time_experiment import DATAFILE
from src.preprocessing.graphs import (
    read_beasley, read_huffner,
    convert_oct_set, load_pre_oct_set,
    load_og_name_lookup
)
from itertools import chain
import ast
import networkx as nx
import pandas


# Constants
OCT = PREPROCESSED_DATA_DIR / 'oct'
LOOKUP = PREPROCESSED_DATA_DIR / 'lookup'
RESULTS_FILENAMES = [
    COMBINED_RESULTS_DATA_FILE,
    EXACT_RESULTS_DATA_PATH,
    ILP_RESULTS_FILE_PATH,
    BASELINE_FILE,
    SELF_COMPARISON_DATA_PATH,
    DATAFILE
]
RESULTS_HEADERS = [
    headers.SOLVER, headers.DATASET, headers.RESULTS_FILE, headers.CERTIFICATE
]
HUFFNER_DATASETS = set(chain(huffner_aa, huffner_j))
BEASLEY_DATASETS = set(beasley_small)
BEASLEY_GKA = set(preprocessed_gka)


def _is_valid_certificate(c):
    """Check to see if a certificate is valid."""

    # Read the graph
    if c.Dataset in HUFFNER_DATASETS:
        graph = read_huffner(
            ORIGINAL_DATA_DIR / 'huffner',
            c.Dataset + ORIGINAL_HUFFNER_DATA_EXT
        )
    elif c.Dataset in BEASLEY_DATASETS:
        graph = read_beasley(
            ORIGINAL_DATA_DIR / 'beasley',
            c.Dataset + BEASLEY_EXT
        )
    elif c.Dataset in BEASLEY_GKA:
        graph = read_beasley(
            ORIGINAL_DATA_DIR / 'gka',
            c.Dataset + BEASLEY_EXT
        )
    else:
        raise Exception('Unknown Dataset: {}'.format(c.Dataset))

    # Load the original oct set and names
    og_names = load_og_name_lookup(LOOKUP, '{}.lookup'.format(c.Dataset))
    pre_oct_set = load_pre_oct_set(OCT, '{}.oct'.format(c.Dataset))

    # Parse the certificate
    certificate = list(map(str, ast.literal_eval(c.Certificate)))

    # Convert certificate to OCT set with original names
    oct_set = convert_oct_set(certificate, og_names)

    # Remove oct verticies
    if pre_oct_set:
        graph.remove_nodes_from(pre_oct_set)
    if oct_set:
        graph.remove_nodes_from(oct_set)

    # Verify the remainder is bipartite
    return nx.is_bipartite(graph)


def main():
    """Sanity check"""

    # Start dataframe results
    results = pandas.DataFrame()

    # Load all results files
    for results_file in RESULTS_FILENAMES:

        # Read and subset
        partial_results = pandas.read_csv(str(RESULTS_DIR / results_file))
        partial_results[headers.RESULTS_FILE] = results_file
        partial_results = partial_results[RESULTS_HEADERS]

        # Concat
        results = pandas.concat([results, partial_results], ignore_index=True)

    # Compute if the certificate is valid
    results[headers.VALID] = results.apply(
        _is_valid_certificate,
        axis=1
    )

    # Find any where it was not valid
    invalid = results[results[headers.VALID] == False].drop(
        columns=headers.VALID
    )  # noqa: E712

    # Print
    if len(invalid):

        # With print context
        with PRINT_CONTEXT:
            print(
                'Invalid certificates found for the following results:\n{}'
                .format(invalid)
            )
    else:
        print('No invalid certificates found')


if __name__ == '__main__':
    main()
