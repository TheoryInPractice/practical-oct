"""Generate the preprocessing ground truth table."""


# Imports
from experiments import (
    headers,
    PREPROCESSED_DATA_DIR,
    EDGELIST_DATA_DIR,
    EDGELIST_DATA_EXT,
    TABLES_DIR,
    normalize_dataset_name
)
from experiments.exact import EXACT_RESULTS_DATA_PATH, AI
from experiments.datasets import preprocessed
from functools import reduce
import pandas


# Constants
DATA_SUBSET = [
    'b-50-1', 'b-50-2',
    'b-100-1', 'b-100-2',
    'gka-1', 'gka-2',
    'gka--15', 'gka-16',
    'gka-17', 'gka-18',
    'gka-25',
    'aa-10', 'aa-11',
    'aa-16', 'aa-21',
    'aa-41', 'aa-42',
    'j-10', 'j-11',
    'j-15', 'j-16'
]


def _get_metadata(dataset):
    """"Read vertex and edge metadata from an edgelist dataset."""
    with open(dataset, 'r') as datafile:
        return datafile.readline().strip().split(' ')


def main():
    """Generate ground truth table."""

    # Get preprocessed graph verex and edge metadata
    metadata = pandas.DataFrame(
        [
            (
                dataset,
                *_get_metadata(str(
                    EDGELIST_DATA_DIR / (dataset + EDGELIST_DATA_EXT)
                ))
            )
            for dataset in preprocessed
        ],
        columns=[headers.DATASET, headers.VERTICES, headers.EDGES],
        dtype='int64'
    )
    metadata = metadata.rename(columns={
        headers.VERTICES: headers.LT_VP,
        headers.EDGES: headers.LT_PREPROCESSED_EDGES
    })

    # Get summary of edits made during preprocessing
    edits = pandas.concat([
        pandas.read_csv(str(PREPROCESSED_DATA_DIR / 'summary' / filename))
        for filename in ['beasley.csv', 'gka.csv', 'huffner.csv']
    ])
    edits = edits.rename(columns={
        headers.VERTICES_REMOVED: headers.LT_VERTICES_REMOVED,
        headers.EDGES_REMOVED: headers.LT_EDGES_REMOVED,
        headers.OCT: headers.LT_VERTICES_OCT,
        headers.BIPARTITE: headers.LT_VERTICES_BIPARTITE
    })

    # Load all exact results and subset to akiba_iwata
    # Then grab only the headers we want
    exact = pandas.read_csv(str(EXACT_RESULTS_DATA_PATH))
    exact = exact[exact[headers.SOLVER] == AI]
    exact = exact[[headers.DATASET, headers.SIZE]]
    exact = exact.rename(columns={
        headers.SIZE: headers.LT_PREPROCESSED_OPT
    })

    # Merge them all together
    ground_truth = reduce(
        lambda l, r: l.merge(r, on=headers.DATASET),
        [metadata, edits, exact]
    )

    # Compute vertices, edges, and opt in original graph
    # ground_truth[headers.LT_VP] = (
    #     ground_truth[headers.LT_VP] -
    #     ground_truth[headers.LT_VERTICES_BIPARTITE]
    # )
    ground_truth[headers.LT_NUM_VERTICES] = (
        ground_truth[headers.LT_VP] +
        ground_truth[headers.LT_VERTICES_REMOVED] +
        # ground_truth[headers.LT_VERTICES_BIPARTITE] +
        ground_truth[headers.LT_VERTICES_OCT]
    )
    ground_truth[headers.LT_NUM_EDGES] = (
        ground_truth[headers.LT_PREPROCESSED_EDGES] +
        ground_truth[headers.LT_EDGES_REMOVED]
    )
    ground_truth[headers.LT_OPT] = (
        ground_truth[headers.LT_PREPROCESSED_OPT] +
        ground_truth[headers.LT_VERTICES_OCT]
    )

    # Now reorder the columns
    ground_truth = ground_truth[[
        headers.DATASET,
        headers.LT_NUM_VERTICES, headers.LT_NUM_EDGES, headers.LT_OPT,
        headers.LT_VERTICES_REMOVED, headers.LT_EDGES_REMOVED,
        headers.LT_VERTICES_OCT, headers.LT_VERTICES_BIPARTITE,
        headers.LT_VP, headers.LT_PREPROCESSED_EDGES,
        headers.LT_PREPROCESSED_OPT
    ]]

    # Manually escape dataset names
    ground_truth[headers.DATASET] = ground_truth[headers.DATASET].map(
        normalize_dataset_name
    )

    # Rename column
    ground_truth = ground_truth.rename(columns={
        headers.DATASET: headers.BF_DATASET
    })

    # Select subset of datasets summarized in the main paper.
    subset = ground_truth[
        ground_truth[headers.BF_DATASET].isin(DATA_SUBSET)
    ].copy()

    # Texttt wrap the datasets
    ground_truth[headers.BF_DATASET] = ground_truth[headers.BF_DATASET].map(
        lambda n: r'\texttt{{{}}}'.format(n)
    )
    subset[headers.BF_DATASET] = subset[headers.BF_DATASET].map(
        lambda n: r'\texttt{{{}}}'.format(n)
    )

    # Latex
    columns = ''.join(['l'] + ['r'] * (len(ground_truth.columns.values) - 1))

    # Print the entire table
    ground_truth.to_latex(
        str(TABLES_DIR / 'preprocessed_ground_truth.tex'),
        index=False,
        escape=False,
        column_format=columns
    )

    subset.to_latex(
        str(TABLES_DIR / 'preprocessed_summary.tex'),
        index=False,
        escape=False,
        column_format=columns
    )


if __name__ == '__main__':
    main()
