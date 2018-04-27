"""Experiment for exact solutions"""


# Imports
from experiments import (
    headers,
    logger,
    HUFFNER_DATA_DIR,
    HUFFNER_DATA_EXT,
    SNAP_DATA_DIR,
    SNAP_DATA_EXT,
    EXACT_TIMEOUT,
    GROUND_TRUTH_DATA_FILE
)
from experiments.datasets import preprocessed as DATASETS
from experiments.exact import (
    AI,
    IC,
    ILP,
    ILP1T,
    EXACT_RESULTS_DATA_PATH
)
from src.ilp.solver import read_edgelist, solve as solve_ilp
from src.akiba_iwata.solver import solve as solve_ai
from src.huffner.solver import solve as solve_ic
from functools import partial
from itertools import product
import csv
import pandas
import subprocess
import sys


def _run_ilp(dataset, threads=4):
    """Run the designmated ILP solver on a dataset."""

    # Compute solution
    solution = solve_ilp(
        read_edgelist(str(SNAP_DATA_DIR / (dataset + SNAP_DATA_EXT))),
        formulation='VC',
        solver='CPLEX',
        threads=threads,
        timelimit=EXACT_TIMEOUT,
        convert_to_oct=True
    )

    # Return solution
    return solution.time, solution.opt, solution.certificate


def _run_ai(dataset):
    """Run Akiba-Iwata on a dataset"""

    # Run
    return solve_ai(
        str(SNAP_DATA_DIR / (dataset + SNAP_DATA_EXT)),
        timeout=EXACT_TIMEOUT,
        convert_to_oct=True
    )


def _run_ic(dataset):
    """Run iterative compression on a dataset."""

    # Run
    return solve_ic(
        str(HUFFNER_DATA_DIR / (dataset + HUFFNER_DATA_EXT)),
        timeout=EXACT_TIMEOUT,
        preprocessing=2,
        htime=min(0.3 * EXACT_TIMEOUT, 1)
    )


def _generate_ground_truth():
    """Generate the ground truth file from exact results."""

    # Read exact results
    exact = pandas.read_csv(str(EXACT_RESULTS_DATA_PATH))

    # Subset to Akiba-Iwata
    exact = exact[exact[headers.SOLVER] == AI]

    # Pick only Dataset, Size, and Certificate
    exact = exact[[headers.DATASET, headers.SIZE, headers.CERTIFICATE]]

    # Write to csv
    exact.to_csv(str(GROUND_TRUTH_DATA_FILE), index=False)


def main():
    """Run experiment."""

    # Create dictionary of solvers
    solvers_dict = {
        AI: _run_ai,
        ILP: _run_ilp,
        ILP1T: partial(_run_ilp, threads=1),
        IC: _run_ic
    }

    # Get solvers
    argv = sys.argv[1:]
    if len(argv) == 1 and argv[0] in solvers_dict:
        name = argv[0]
        solvers = [(name, solvers_dict[name])]
    else:
        solvers = list(solvers_dict.items())

    # Generate experiments
    experiments = product(DATASETS, solvers)

    # Open output file for writing
    with open(str(EXACT_RESULTS_DATA_PATH), 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            headers.DATASET, headers.SOLVER, headers.TIME,
            headers.SIZE, headers.CERTIFICATE
        ])

        # Run experiments
        for dataset, (name, solver) in experiments:

            # Log
            logger.info('Running {} on {}'.format(name, dataset))

            # Solve and write output
            try:
                solution = solver(dataset)
                if solution[0] >= EXACT_TIMEOUT:
                    continue
            except subprocess.TimeoutExpired:
                continue

            writer.writerow([
                dataset,
                name,
                *solution
            ])
            output.flush()

    # Now generate the ground truth table if akiba_iwata was run
    if (AI, _run_ai) in solvers:
        _generate_ground_truth()


# Invoke main
if __name__ == '__main__':
    main()
