"""Generate plots for the FCLs experiments.

This plotting script requires that the exact and heuristic FSLs experiments
have been run.
"""


# Imports
from pandas import Series
import pandas

from experiments import headers, RESULTS_DIR
from experiments.fcls.exact_run import (
    RESULTS_FILE as EXACT_RESULTS,
    ILP,
)
from experiments.fcls.heuristic_run import RESULTS_FILE as HEURISTIC_RESULTS


# Paths
EXACT_TABLE = RESULTS_DIR / 'fcls_exact_table.tex'
HEURISTIC_TABLE = RESULTS_DIR / 'fcls_heuristic_table.tex'


# Opt is currently loaded from the ILP runs of the exact results. This
# assumes that ILP is not going to time out, which is in general a decent
# assumption on this dataset. If needed, we can run ILP with no timeout to
# get the actual opt values.
def compute_opt() -> Series:
    """Compute the optimum solution for each dataset.

    The ILP result from the exact experiment is used as the opt value.

    Returns
    -------
    Series
        ILP solution sizes indexed by dataset name.
    """
    # Load exact results.
    df = pandas.read_csv(EXACT_RESULTS)

    # Get ILP data only.
    df = df[df[headers.SOLVER] == ILP]

    # Set dataset as the index, and take keep only the size
    return df.set_index(headers.DATASET)[headers.SIZE]


def generate_exact_table():
    """Generate a latex table of exact results."""
    # Load exact data
    df = pandas.read_csv(EXACT_RESULTS)

    # Subset to columns we care about
    df = df[[headers.DATASET, headers.SOLVER, headers.TIME]]

    # Set index and unstack
    df = df.set_index([headers.DATASET, headers.SOLVER])
    df = df.unstack()
    df.columns = df.columns.droplevel(0)

    # Set opt value
    opt = compute_opt()
    df = df.join(opt)

    # Reindex for readability
    df = df.rename(index=lambda i: (
        '({:3.0f}, {:1.2f}, {:2.0f})'.format(*map(float, i.split('_')[1:]))
    ))
    df.index.name = '{} (clique_size, num_cycles, idx)'.format(df.index.name)

    # Sort lexicographically
    df = df.sort_index()

    # Write
    df.to_latex(EXACT_TABLE)


def generate_heuristic_table():
    """Generate a latex table of heuristic results."""
    # Load heuristic data
    df = pandas.read_csv(HEURISTIC_RESULTS)

    # Subset to the columns we care about
    df = df[[headers.DATASET, headers.TIMEOUT, headers.SOLVER, headers.SIZE]]

    # Set index and unstack
    df = df.set_index([headers.DATASET, headers.SOLVER, headers.TIMEOUT])
    df = df.unstack().unstack()

    # Compute opt
    opt = compute_opt()

    # Compute ratio to opt for each dataset
    df = df.apply(lambda r: r / opt[r.name], axis=1).round(2)

    # Reindex for readability
    df = df.rename(index=lambda i: (
        '({:3.0f}, {:1.2f}, {:2.0f})'.format(*map(float, i.split('_')[1:]))
    ))
    df.index.name = '{} (clique_size, num_cycles, idx)'.format(df.index.name)

    # Sort lexicographically
    df = df.sort_index()

    # Write
    df.to_latex(HEURISTIC_TABLE)


def main():
    """Parse arguments and plot."""
    # Plot
    generate_heuristic_table()
    generate_exact_table()


# Invoke main
if __name__ == '__main__':
    main()
