"""Run ILP experiments.

Experiment results are reported in the generated CSV file
`ilp_experiment_results.csv`. Result headers are, in order
- Solver
- Threads
- Formulation
- Memory
- Dataset
- Vertices
- Edges
- Time
- Opt
- Certificate

All VertexCover formulation solutions are converted back
to an OCT solution for comparision to the OCT formulation.

Plots are plotted in `ilp_figures.pdf`. The output table
is in `ilp_table.tex`.
"""


# Imports
from experiments import (
    headers,
    logger,
    EXACT_TIMEOUT,
    SNAP_DATA_DIR,
    SNAP_DATA_EXT,
    EDGELIST_DATA_DIR,
    EDGELIST_DATA_EXT
)
from experiments.datasets import ilp_experiment_datasets
from experiments.ilp import (
    SOLVERS,
    EXPERIMENT_MEMORY_LIMITS,
    ILP_RESULTS_FILE_PATH
)
from itertools import product, chain
from src.ilp.solver import solve, read_edgelist
import csv
import os


def _dataset_to_formulations(data):
    """Construct (formulation, file) pairs from dataset.

    Parameters
    ----------
    data : string
        Name of dataset

    Returns
    -------
    tuple
        Return tuple of (formulation, file) pairs
    """

    # Return tuple of formulations
    return (
        ('OCT', str(EDGELIST_DATA_DIR / (data + EDGELIST_DATA_EXT))),
        ('VC', str(SNAP_DATA_DIR / (data + SNAP_DATA_EXT)))
    )


def _run_experiments():
    """Run experiments."""

    # Generate full (formulation, file) data list
    DATA = list(chain.from_iterable(map(
        lambda f: _dataset_to_formulations(f),
        ilp_experiment_datasets
    )))

    # Generate iterator for experiments
    experiments = product(
        SOLVERS,
        EXPERIMENT_MEMORY_LIMITS,
        DATA
    )

    # Log
    logger.info('Starting ILP Experiments')
    logger.info('- {} solvers'.format(len(SOLVERS)))
    logger.info('- {} memory limits'.format(len(EXPERIMENT_MEMORY_LIMITS)))
    logger.info('- {} data sets'.format(len(DATA) / 2))

    # Open output file
    with open(str(ILP_RESULTS_FILE_PATH), 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            headers.SOLVER,
            headers.THREADS,
            headers.MEMORY,
            headers.FORMULATION,
            headers.DATASET,
            headers.VERTICES,
            headers.EDGES,
            headers.TIME,
            headers.OPT,
            headers.CERTIFICATE
        ])

        # Iterate over experiments
        for experiment in experiments:

            # Run Experiments
            try:

                # Log
                logger.info((
                    'Running experiment solver={}, threads={}, '
                    'memlimit={}, dataset={}'
                ).format(
                    experiment[0][0], experiment[0][1],
                    experiment[1], experiment[2][1]
                ))

                # Compute solution
                solution = solve(
                    read_edgelist(experiment[2][1]),
                    solver=experiment[0][0],
                    threads=experiment[0][1],
                    formulation=experiment[2][0],
                    timelimit=EXACT_TIMEOUT,
                    memlimit=experiment[1],
                    convert_to_oct=True
                )

                # Write
                writer.writerow([
                    experiment[0][0],
                    experiment[0][1],
                    experiment[1],
                    experiment[2][0],
                    os.path.splitext(os.path.basename(experiment[2][1]))[0],
                    solution.n,
                    solution.m,
                    solution.time,
                    solution.opt,
                    solution.certificate
                ])
                output.flush()

            # Handle failure
            except Exception as e:
                logger.error(e)


def main():
    """Manage ILP experiments."""

    # Run
    _run_experiments()


# Call main
if __name__ == '__main__':
    main()
