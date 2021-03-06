"""Experiment for exact solutions"""


# Imports
from src.preprocessing.graphs import names_in_dir
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
from pathlib import Path
import argparse


def _run_ilp(dataset, threads, formulation, timeout):
    """Run the designmated ILP solver on a dataset."""

    # Compute solution
    solution = solve_ilp(
        read_edgelist(str(SNAP_DATA_DIR / (dataset + SNAP_DATA_EXT))),
        formulation=formulation,
        solver='CPLEX',
        threads=threads,
        timelimit=timeout,
        convert_to_oct=True
    )

    # Return solution
    return solution.time, solution.opt, solution.certificate


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


def main(current_server_id, total_servers, seed_filter):
    """Run experiment."""

    # Find the datasets we want
    input_dir = Path('.') / 'data' / 'preprocessed' / 'edgelist'
    datasets = names_in_dir(input_dir, '.edgelist')
    datasets = [dataset.replace('.edgelist', '') for dataset in datasets]
    datasets = sorted(datasets)
    # Quantum data has no dashes, synthetics use dashes to separate parameters
    datasets = list(filter(seed_filter, datasets))
    dataset_partition = datasets[current_server_id-1::total_servers]

    # print('Expected data:', dataset_partition)
    # Collect solvers
    solvers_dict = {
        'ilp_vc_1t':
            partial(_run_ilp, threads=1, formulation='VC', timeout=3600),
        'ilp_vc_4t':
            partial(_run_ilp, threads=4, formulation='VC', timeout=3600),
        'ilp_oct_1t':
            partial(_run_ilp, threads=1, formulation='OCT', timeout=3600),
        'ilp_oct_4t':
            partial(_run_ilp, threads=4, formulation='OCT', timeout=3600),
    }
    solvers = sorted(list(solvers_dict.items()))

    # Generate experiments
    experiments = product(dataset_partition, solvers)

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


# Invoke main
if __name__ == '__main__':
    # Obtain the server number needed to split the data
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-server',
        type=int,
        required=True,
        help='Current server number between 1 and total number of servers')
    parser.add_argument(
        '-of',
        type=int,
        required=True,
        help='Total number of servers')
    args = parser.parse_args()
    main(args.server, args.of, lambda x: '-' not in x)
