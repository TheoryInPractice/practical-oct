"""Script for generating heuristics results latex figures."""


# Imports
from experiments import (
    headers,
    TABLES_DIR,
    RESULTS_DIR,
    GROUND_TRUTH_DATA_FILE
)
from experiments.datasets import preprocessed

from itertools import zip_longest
import pathlib
import pandas
import re

EXACT_RESULTS_DATA_PATH = RESULTS_DIR / 'quantum_exact_results.csv'

IC = 'ic'
AI = 'vc'
ILP = 'ilp'
ILP1T = 'ilp_1t'


# Constants
SOLVER_ORDERING = [ILP, ILP1T, AI, IC]
OUTPUT_DIR = TABLES_DIR / 'exact_tables'
HEADERS = [
    headers.BF_DATASET,
    headers.LT_OPT,
    'A-I',
    r'$\text{IC}^+_{2}$',
    'ILP'
]


def _rename_dataset(v):
    return re.sub(
        r'([a-zA-Z]+)_?([0-9]+)(?:_([0-9]+))?',
        lambda m: m.group(1) + '-' + m.group(2) + (
            '-' + m.group(3) if m.group(3) else ''
        ),
        v
    ).replace('bqp', 'b')


def _get_metadata(dataset):
    """"Read vertex and edge metadata from an edgelist dataset."""
    with open(dataset, 'r') as datafile:
        return datafile.readline().strip().split(' ')


def dataset_sorter(r):

    name = r[headers.DATASET]

    # Choose how we want to order the datasets
    ORDERING = {"aa": 0, "j": 1, "bqp": 2, "gka": 3}

    # Head will be letters
    head = name.rstrip("0123456789_")

    # Tail could be number or number_number
    tail = name[len(head):].lstrip("_")

    # In either case, make tail a tuple of ints
    if "_" in tail:
        tail = list(map(int, tail.split("_")))
    else:
        tail = int(tail)

    # Return a tuple of ints as our comparison key
    return (ORDERING[head], tail)


def main():
    """Load and print results."""

    # Read exact results
    c = pandas.read_csv(EXACT_RESULTS_DATA_PATH)

    # Pivot table
    c = c.drop(columns=[headers.SIZE, headers.CERTIFICATE])
    c = c.set_index([headers.DATASET])
    c = c.pivot(columns=headers.SOLVER)
    c = c.reorder_levels([1, 0], axis=1)
    c.columns = [c[0] for c in c.columns.values]
    c = c[SOLVER_ORDERING]
    c = c.reset_index().fillna('-')

    # Read metadata
    gt = pandas.read_csv(str(GROUND_TRUTH_DATA_FILE))
    gt = gt[[headers.DATASET, headers.SIZE]].rename(columns={
        headers.SIZE: headers.OPT
    })

    # Merge in metadata
    c = c.merge(gt, on=headers.DATASET)

    # Get the individual subsets of records
    first_half = preprocessed[:int(len(preprocessed)/2)]
    second_half = preprocessed[int(len(preprocessed)/2):]
    left_table = c[c[headers.DATASET].isin(first_half)]
    left_records = sorted(left_table.to_dict('records'), key=dataset_sorter)
    right_table = c[c[headers.DATASET].isin(second_half)]
    right_records = sorted(right_table.to_dict('records'), key=dataset_sorter)

    # Zip them together so we can iterate
    records = list(zip_longest(left_records, right_records))

    def _format_record(r):

        # # If no record, just return empty columns
        if not r:
            return ' '.join(['&'] * (len(HEADERS) - 1))

        # Otherwise p
        return (
            r'\texttt{{{dataset}}} & {opt} & {ai} & {ic} & {ilp}'
            .format(
                dataset=_rename_dataset(r.get(headers.DATASET, '')),
                opt=r[headers.OPT],
                ai=r[AI],
                ic=r[IC],
                ilp=r[ILP]
            )
        )

    # Start list of lines in the output tex file
    format_str = ''.join(['l'] + ['r'] * (len(HEADERS) - 1))
    header_str = ' & '.join(HEADERS)
    output_lines = [
        r'\begin{{tabular}}{{{fmt}p{{0.5in}}{fmt}}}'.format(fmt=format_str),
        r'\toprule',
        r"""  \multicolumn{2}{c}{\textbf{Graph}}
            & \multicolumn{3}{c}{\textbf{Solver}}
            &
            & \multicolumn{2}{c}{\textbf{Graph}}
            & \multicolumn{3}{c}{\textbf{Solver}} \\""".replace('\n', ''),
        r'\cmidrule(lr){1-2}',
        r'\cmidrule(lr){3-5}',
        r'\cmidrule(lr){7-8}',
        r'\cmidrule(lr){9-11}',
        header_str + ' & & ' + header_str + r' \\',
        r'\midrule',
        *(
            _format_record(t1) + ' & & ' + _format_record(t2) + r' \\'
            for t1, t2 in records
        ),
        r'\bottomrule',
        r'\end{tabular}'
    ]

    # Write output
    pathlib.Path(OUTPUT_DIR).mkdir(parents=True, exist_ok=True)
    output_filename = str(OUTPUT_DIR / 'quantum_exact.tex')
    with open(output_filename, 'w') as output:
        output.writelines(map(lambda l: l + '\n', output_lines))


# Invoke main
if __name__ == '__main__':
    main()
    print("Wrote quantum_exact.tex")
