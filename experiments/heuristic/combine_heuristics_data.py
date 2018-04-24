"""Script for generating heuristics results latex figures."""


# Imports
from experiments import (
    headers,
    PREPROCESSING_TIMEOUTS,
    PRINT_CONTEXT
)
from experiments.heuristic import (
    GROUND_TRUTH_DATA_FILE,
    COMBINED_RESULTS_DATA_FILE,
    CPLEX_RESULTS_DATA_FILE,
    HEURISTICS_RESULTS_DATA_FILE,
    HUFFNER_RESULTS_DATA_FILE,
    CPLEX_SOLVER,
    HEURISTICS_SOLVER,
    HUFFNER_P1,
    HUFFNER_P2,
    LT_HUFFNER_P1,
    LT_HUFFNER_P2
)
from itertools import chain, product
import pandas as pd
import re


# Constants
SOLVER_ORDERING = [CPLEX_SOLVER, HEURISTICS_SOLVER]
PIVOT_ORDERING = list(chain.from_iterable([
    ('{} - Size'.format(s) for s in SOLVER_ORDERING),
    ('{} - Time'.format(s) for s in SOLVER_ORDERING)
]))


def write_latex_header(outfile, solvers):
    outfile.write("\\begin{tabular}{lrcrrrcrrrcrrrcrrrl}\n")
    outfile.write("\\toprule\n")
    outfile.write("& \multicolumn{2}{c}{\\textbf{Timeout:}} &\n")
    outfile.write("\multicolumn{3}{c}{\\textbf{0.01(s)}} & \phantom{Q} &\n")
    outfile.write("\multicolumn{3}{c}{\\textbf{0.1(s)}} & \phantom{Q} &\n")
    outfile.write("\multicolumn{3}{c}{\\textbf{1(s)}} & \phantom{Q} &\n")
    outfile.write("\multicolumn{3}{c}{\\textbf{10(s)}}\\\\\n")
    outfile.write("\cmidrule(lr){4-6}\n")
    outfile.write("\cmidrule(lr){8-10}\n")
    outfile.write("\cmidrule(lr){12-14}\n")
    outfile.write("\cmidrule(lr){16-18}\n")
    outfile.write("\\textbf{Dataset} & $OPT$ & &\n")

    outfile.write("{} & {} & {} &  &\n".format(*solvers[0]))
    outfile.write("{} & {} & {} &  &\n".format(*solvers[0]))
    outfile.write("{} & {} & {} &  &\n".format(*solvers[1]))
    outfile.write("{} & {} & {}\\\\\n".format(*solvers[1]))


def write_latex_row(outfile, row):
    outfile.write("""{} & {} & &\n{} & {} & {} & &\n{} & {} & {} & &\n{} & {} & {} & &\n{} & {} & {}\\\\ \n\n""".format(*row))


def write_latex_footer(outfile):
    outfile.write("\\bottomrule\n")
    outfile.write("\end{tabular}\n")


def write_dataset_header(outfile, text):
    outfile.write("\midrule\multicolumn{10}{l}{\\textbf{" + text + "}}\\\\\n\\midrule")


def write_dataset(outfile, dataset, timeouts, solvers, df, opt_df):
    for name in dataset:
        m = re.match(r'([a-zA-Z]+)_?([0-9]+)(?:_([0-9]+))?', name)
        printed_name = '{}-{}-{}'.format(
            m.group(1), m.group(2), m.group(3) or ''
        ).strip('-')
        opt = int(opt_df.query("Dataset == '{}'".format(name))['Size'])
        row = ['\\texttt{' + printed_name + '}', opt]
        for i in [0, 1]:
            for timeout, solver in product(timeouts[i], solvers[i]):
                df_row = df.query("Dataset == '{}' and Timeout == {} and Solver == '{}'".format(name, timeout, solver))
                value = int(df_row['Size'])
                time = float(df_row['Time'])
                if value == opt and time < timeout and solver != HEURISTICS_SOLVER:
                    row.append(r'\textBF{{{}}}'.format(value))
                else:
                    row.append(value)
        write_latex_row(outfile, row)


def print_full(df):
    with pd.option_context('display.max_rows', None,
                           'display.max_columns', None):
        print(df)


def dataset_sorter(name):
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

    opt_df = pd.read_csv(GROUND_TRUTH_DATA_FILE)

    # Read cplex results
    cplex_df = pd.read_csv(CPLEX_RESULTS_DATA_FILE)
    cplex_df[headers.SOLVER] = CPLEX_SOLVER

    # Read huffner results
    huffner_df = pd.read_csv(HUFFNER_RESULTS_DATA_FILE)

    # Read heuristics results
    he_df = pd.read_csv(HEURISTICS_RESULTS_DATA_FILE)
    he_df[headers.SOLVER] = HEURISTICS_SOLVER
    he_df[headers.TIMEOUT] = he_df[headers.TIMEOUT] / 1000
    he_df[headers.TIME] = he_df[headers.TIME].apply(
        lambda v: round(v / 1000, 1)
    )

    # Combine results and normalize dataset names
    df = pd.concat([cplex_df, he_df, huffner_df])
    df[headers.DATASET] = df[headers.DATASET].apply(lambda v: v.split('.')[0])
    df = df.sort_values(by=[headers.DATASET, headers.TIMEOUT])

    # Export combined data
    df.to_csv(COMBINED_RESULTS_DATA_FILE, index=False)

    datasets = sorted(list(set(df['Dataset'])), key=dataset_sorter)
    aa_datasets = filter(lambda x: 'aa' in x, datasets)
    j_datasets = filter(lambda x: 'j' in x, datasets)
    b50_datasets = filter(lambda x: 'bqp50' in x, datasets)
    b100_datasets = filter(lambda x: 'bqp100' in x, datasets)
    gka_datasets = filter(lambda x: 'gka' in x, datasets)
    timeouts = [PREPROCESSING_TIMEOUTS[:2], PREPROCESSING_TIMEOUTS[2:]]
    solver_headers = [
        (HEURISTICS_SOLVER, LT_HUFFNER_P1, CPLEX_SOLVER),
        (HEURISTICS_SOLVER, LT_HUFFNER_P2, CPLEX_SOLVER)
    ]
    solvers = [
        (HEURISTICS_SOLVER, HUFFNER_P1, CPLEX_SOLVER),
        (HEURISTICS_SOLVER, HUFFNER_P2, CPLEX_SOLVER)
    ]

    with open('paper/tables/heuristic1.tex', 'w') as outfile:
        write_latex_header(outfile, solver_headers)
        write_dataset_header(outfile, 'Wernicke-\\huffner Afro-American Graphs')
        write_dataset(outfile, aa_datasets, timeouts, solvers, df, opt_df)
        write_dataset_header(outfile, 'Wernicke-\\huffner Japanese Graphs')
        write_dataset(outfile, j_datasets, timeouts, solvers, df, opt_df)
        write_latex_footer(outfile)

    with open('paper/tables/heuristic2.tex', 'w') as outfile:
        write_latex_header(outfile, solver_headers)
        write_dataset_header(outfile, 'Beasley 50-Vertex Graphs')
        write_dataset(outfile, b50_datasets, timeouts, solvers, df, opt_df)
        write_dataset_header(outfile, 'Beasley 100-Vertex Graphs')
        write_dataset(outfile, b100_datasets, timeouts, solvers, df, opt_df)
        write_dataset_header(outfile, 'GKA Graphs')
        write_dataset(outfile, gka_datasets, timeouts, solvers, df, opt_df)
        write_latex_footer(outfile)

    # Copy df to start computing approximation factor
    approx = df.copy()[[
        headers.DATASET, headers.SOLVER,
        headers.SIZE, headers.TIMEOUT
    ]]

    # Set index, pivot, fill empty values, then reset column levels and index
    approx = approx.set_index([headers.TIMEOUT, headers.DATASET])
    approx = approx.pivot(columns=headers.SOLVER)
    approx = approx.fillna(0)
    approx.columns = approx.columns.droplevel()
    approx = approx.reset_index()

    # Merge with ground truth opt data
    opt_df = opt_df[[headers.DATASET, headers.SIZE]].rename(columns={
        headers.SIZE: 'opt'
    })
    approx = approx.merge(opt_df, on=headers.DATASET)

    # All solvers we have in our dataset
    all_solvers = [
        HEURISTICS_SOLVER, HUFFNER_P1, HUFFNER_P2, CPLEX_SOLVER
    ]

    # Compute approximation ratios
    for solver in all_solvers:
        approx[solver] /= approx['opt']

    # Now drop the opt column
    approx = approx.drop(columns='opt')

    # Now transform the dataset into its group name
    approx[headers.DATASET] = approx[headers.DATASET].map(
        lambda d: re.match(r'(bqp50|bqp100|[a-zA-z]+)', d).group(1)
    )

    # Group by timeout and dataset
    approx = approx.groupby([headers.TIMEOUT, headers.DATASET]).max().round(
        decimals=2
    )
    approx = approx.unstack(level=0)
    approx.columns = approx.columns.swaplevel(0, 1)
    approx = approx.sort_index(axis=1, level=0)
    approx = approx.drop(columns=[
        (0.01, HUFFNER_P2),
        (0.1, HUFFNER_P2),
        (1, HUFFNER_P1),
        (10, HUFFNER_P1)
    ])

    with PRINT_CONTEXT:
        print(approx)


# Invoke main
if __name__ == '__main__':
    main()
