"""Generate the preprocessing ground truth table."""

from itertools import product

# Imports
from experiments import headers
import pandas as pd
import numpy as np
from pathlib import Path
import re

PREPROCESSED_DATA_DIR = Path('.') / 'data' / 'preprocessed'
EDGELIST_DATA_DIR = PREPROCESSED_DATA_DIR / 'edgelist'
EDGELIST_DATA_EXT = '.edgelist'
TABLES_DIR = Path('.') / 'tables'
AI = 'akiba_iwata'
ILP = 'ilp'


def normalize_dataset_name(name):
    m = re.match(r'([a-zA-Z]+)_?([0-9]+)(?:_([0-9]+))?', name)
    return '{}-{}-{}'.format(
        m.group(1).replace('bqp', 'b'),
        m.group(2),
        m.group(3) or ''
    ).strip('-')


def _get_metadata(dataset):
    """"Read vertex and edge metadata from an edgelist dataset."""
    with open(dataset, 'r') as datafile:
        return datafile.readline().strip().split(' ')


def _compute_density(row, preprocessed):
    """Computes the density for a given row."""
    if preprocessed:
        if row['final_vertices'] == 0:
            return float('NaN')
        return (float(row['final_edges']) /
                float(row['final_vertices']))
    else:
        return (float(row['original_edges']) /
                float(row['original_vertices']))


def _vertex_normalize(row, col_name):
    """Computes the value at row[col_name] normalized by vertices."""
    return (float(row[col_name]) /
            float(row[headers.LT_NUM_VERTICES])) * 100


def _edge_normalize(row, col_name):
    """Computes the value at row[col_name] normalized by edges."""
    if row[headers.LT_NUM_EDGES] == 0:
        return 'NaN'
    return (float(row[col_name]) /
            float(row[headers.LT_NUM_EDGES])) * 100


def _range_str(col):
    """Given a Series, return a string summarizing the range."""
    smallest, largest = min(col), max(col)
    if smallest == largest:
        if np.issubdtype(col.dtype, np.float):
            return '{:.1f}'.format(smallest)
        else:
            return '{}'.format(smallest)
    else:
        if np.issubdtype(col.dtype, np.float):
            return '{:.1f}--{:.1f}'.format(min(col), max(col))
        else:
            return '{}--{}'.format(min(col), max(col))


def _mean_str(col):
    """Returns the mean of a Series formatted as a str"""
    return _str(int(np.mean(col)))


def _str(value):
    """Returns the value formatted as a string"""
    if value == 0:
        return '-'
    else:
        return r'{}\%'.format(value)


def _save_latex_table(dataframe, table_name):
    """Prints a dataframe to a reasonably-formatted latex table"""
    # Compute column_format
    columns = ''.join(['l'] + ['r'] * (len(dataframe.columns.values) - 1))

    # Print the entire table
    dataframe.to_latex(
        str(TABLES_DIR / table_name),
        index=False,
        escape=False,
        column_format=columns
    )


def construct_df(filename):
    """Constructs the primary DataFrame"""

    preprocessed_data =\
        pd.read_csv(filename, dtype={'Dataset': np.str,
                                     'original_vertices': np.int64,
                                     'original_edges': np.int64,
                                     'vertices_removed': np.int64,
                                     'edges_removed': np.int64,
                                     'oct': np.int64,
                                     'bipartite': np.int64,
                                     'final_vertices': np.int64,
                                     'final_edges': np.int64})

    # "Rename" (=copy) my new columns to old names
    preprocessed_data[headers.LT_NUM_VERTICES] =\
        preprocessed_data['original_vertices']
    preprocessed_data[headers.LT_NUM_EDGES] =\
        preprocessed_data['original_edges']

    # with pd.option_context('display.max_rows', None):
    #     print(preprocessed_data)

    return preprocessed_data


def construct_summary_df(data):
    """Using the preprocessed data, compute the statistics DataFrame"""
    print("Started summary")

    # Begin by adding all columns we care about
    # Add density column
    data[headers.DENSITY] = data.apply(
        lambda row: _compute_density(row, preprocessed=False), axis=1)

    data[headers.PREPROCESSED_DENSITY] = data.apply(
        lambda row: _compute_density(row, preprocessed=True), axis=1)

    # Compute the normalized data as new columns
    data[headers.LT_VERTICES_REMOVED_NORM] = \
        data.apply(
        lambda row: _vertex_normalize(row, 'vertices_removed'),
        axis=1)

    data[headers.LT_EDGES_REMOVED_NORM] = \
        data.apply(
        lambda row: _edge_normalize(row, 'edges_removed'),
        axis=1)

    data[headers.LT_VERTICES_OCT_NORM] = \
        data.apply(
        lambda row: _vertex_normalize(row, 'oct'),
        axis=1)

    data[headers.LT_VERTICES_BIPARTITE_NORM] = \
        data.apply(
        lambda row: _vertex_normalize(row, 'bipartite'),
        axis=1)

    # Proceed to create a summary of all graphs within a dataset
    # summary_data will summarize over each dataset (headers.DATASET_HEADERS)
    summary_data = pd.DataFrame(columns=[r'\textbf{Dataset}',
                                         r'$|V|$',
                                         r'$|E|/|V|$',
                                         r'$|\widehat{V_r}|$',
                                         r'$|\widehat{E_r}|$',
                                         r'$|\widehat{V_o}|$',
                                         r'$|\widehat{V_b}|$',
                                         r'\textbf{Solved}',
                                         r"$|V' \cup V_b|$",
                                         r"$|E'|/|V' \cup V_b|$"])

    datasets = ['aa', 'j', 'b-50', 'b-100', 'gka']
    generators = ['-er', '-to', '-cl', '-ba']
    for counter, (dataset_header, synthetic_header) in\
            enumerate(product(datasets, generators)):
        print('Looking for data', dataset_header, synthetic_header)
        # Select the rows in this dataset that weren't solved completely
        select_data = data[
            (data[headers.DATASET].str.contains(dataset_header)) &
            (data[headers.DATASET].str.contains(synthetic_header)) &
            (data['final_vertices'] != 0)]

        # Also select the rows that were solved completely, it will be reported
        # as a statistic.
        solved = len(data[
            (data[headers.DATASET].str.contains(dataset_header)) &
            (data[headers.DATASET].str.contains(synthetic_header)) &
            (data['final_vertices'] == 0)])

        # print(select_data)
        row = [r'\texttt{' + dataset_header + str.upper(synthetic_header) +
               r'}']
        # Add the vertex range
        row.append(_range_str(select_data['original_vertices']))
        # Add the density range
        row.append(_range_str(select_data[headers.DENSITY]))
        # Add the average vertices removed
        row.append(_mean_str(select_data['vertices_removed']))
        # Add the average edges removed
        row.append(_mean_str(select_data['edges_removed']))
        # Add the average OCT vertices
        row.append(_mean_str(select_data['oct']))
        # Add the average bipartite vertices
        row.append(_mean_str(select_data['bipartite']))
        # Add the percent of datasets solved
        row.append(_str(int(solved * 100 / (len(select_data) + solved))))
        # Add the preprocessed vertex range
        row.append(_range_str(select_data['final_vertices']))
        # Add the preprocessed density range
        row.append(_range_str(select_data[headers.PREPROCESSED_DENSITY]))

        # Add the new row to the summary data
        summary_data.loc[counter] = row
    return summary_data


if __name__ == '__main__':
    """
    Generate preprocessed data tables.
    """

    results_to_plot = 'results/synthetic_preprocessing_results.csv'

    # Compute the full table of preprocessed data
    preprocessed_data = construct_df(results_to_plot)
    # with pd.option_context('display.max_rows', None):
    #     print(preprocessed_data)
    _save_latex_table(preprocessed_data,
                      'generated_preprocessed_synthetic_full.tex')

    # Compute the summary table
    summary_data = construct_summary_df(preprocessed_data)
    # with pd.option_context('display.max_rows', None):
    #     print(summary_data)
    # Save as a latex table
    _save_latex_table(summary_data,
                      'generated_preprocessed_synthetic_summary.tex')
