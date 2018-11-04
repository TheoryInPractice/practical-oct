"""Experiment for exact solutions"""


# Imports
from src.preprocessing.graphs import names_in_dir
from experiments import (
    headers,
    logger,
    PREPROCESSING_TIMEOUTS_MILLISECONDS,
    HUFFNER_DATA_DIR,
    HUFFNER_DATA_EXT,
    SNAP_DATA_DIR,
    SNAP_DATA_EXT,
    EXACT_TIMEOUT,
    GROUND_TRUTH_DATA_FILE,
    PROJECT_ROOT,
    PREPROCESSING_TIMEOUTS
)
from experiments.exact import (
    AI,
    IC,
    ILP,
    ILP1T,
    EXACT_RESULTS_DATA_PATH
)
from experiments.heuristic import (
    CPLEX_RESULTS_DATA_FILE,
    HEURISTICS_RESULTS_DATA_FILE,
    HEURISTICS_CSV_HEADERS,
    HUFFNER_P1,
    HUFFNER_P2,
    HUFFNER_RESULTS_DATA_FILE,
    HUFFNER_CSV_HEADERS
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
import re
import os

# Constants
HEURISTIC_SOLVER = PROJECT_ROOT / 'src/heuristics/heuristic_solver'
PREPROCESSING_ENSEMBLE = 1
PREPROCESSING_DENSITY = 2


def _execute_cplex(preprocessed):
    """Run experiments"""

    # Compute datasets
    datasets = list(map(
        lambda d: str(SNAP_DATA_DIR / (d + SNAP_DATA_EXT)),
        preprocessed
    ))

    # Log
    logger.info('Starting CPLEX Experiment')

    # Generate experiments
    experiments = product(PREPROCESSING_TIMEOUTS, datasets)

    # Open output file
    with open(str(CPLEX_RESULTS_DATA_FILE), 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow(HEURISTICS_CSV_HEADERS)

        # Run experiments
        for experiment in experiments:

            try:

                # Log
                logger.info(
                    'Starting experiment timeout={} dataset={}'
                    .format(*experiment)
                )

                # Run cplex
                solution = solve(
                    read_edgelist(experiment[1]),
                    formulation='VC',
                    solver='CPLEX',
                    threads=4,
                    timelimit=experiment[0],
                    convert_to_oct=True
                )

                # Write
                writer.writerow([
                    os.path.basename(experiment[1]),
                    experiment[0],
                    solution.opt,
                    solution.time,
                    solution.certificate
                ])
                output.flush()

            except Exception as e:

                logger.error(e)


def _execute_heuristic_ensemble(datasets):
    """Run experiments"""

    # Log
    logger.info('Starting Heuristics Experiment')

    # Generate experiments
    experiments = product(PREPROCESSING_TIMEOUTS_MILLISECONDS, datasets)

    # Open output file
    with open(str(HEURISTICS_RESULTS_DATA_FILE), 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow(HEURISTICS_CSV_HEADERS)

        # Run experiments
        for experiment in experiments:

            # Log
            logger.info(
                'Starting experiment timeout={} dataset={}'.format(*experiment)
            )

            # Run subprocess
            cmd = [str(HEURISTIC_SOLVER), *experiment]
            proc = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )

            # Parse results
            output_string = bytes.decode(proc.stdout, 'utf-8').strip()
            match = re.match(
                r'(\d+),(\d+),"(\[((\d+)(,(\d+))*)?\])"',
                output_string
            )
            size = int(match.group(1))
            time = int(match.group(2))
            certificate = match.group(3)

            # Write
            writer.writerow([
                os.path.basename(experiment[1]),
                experiment[0],
                size,
                time,
                certificate
            ])
            output.flush()


def _execute_iterative_compression(datasets):
    """Run experiment."""

    # Open output file for writing
    with open(str(HUFFNER_RESULTS_DATA_FILE), 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow(HUFFNER_CSV_HEADERS)

        # Run all combinations of dataset and timeouts
        experiments = product(datasets, PREPROCESSING_TIMEOUTS)
        for dataset, timeout in experiments:

            # Log
            logger.info(
                'Computing OCT for {} with timeout={}'
                .format(dataset, timeout)
            )

            # Determine preprocessing level and solver name
            if timeout <= 0.1:
                preprocessing = PREPROCESSING_ENSEMBLE
                solver = HUFFNER_P1
            else:
                preprocessing = PREPROCESSING_DENSITY
                solver = HUFFNER_P2

            # Solve
            solution = solve_ic(
                str(HUFFNER_DATA_DIR / (dataset + HUFFNER_DATA_EXT)),
                timeout=timeout,
                preprocessing=preprocessing,
                htime=min(0.3 * timeout, 1)
            )

            # Write output
            writer.writerow([
                dataset,
                solver,
                timeout,
                *solution
            ])
            output.flush()


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

    # Sloppy way of splitting seeds across servers
    if args.server == 1 and args.of == 3:
        def seed_filter(x): return (x.endswith('-0') or
                                    x.endswith('-1') or
                                    x.endswith('-2') or
                                    x.endswith('-3') or
                                    x.endswith('-4'))
    elif args.server == 2 and args.of == 3:
        def seed_filter(x): return (x.endswith('-5') or
                                    x.endswith('-6') or
                                    x.endswith('-7') or
                                    x.endswith('-8') or
                                    x.endswith('-9'))
    elif args.server == 3 and args.of == 3:
        def seed_filter(x): return (x.endswith('-10') or
                                    x.endswith('-11') or
                                    x.endswith('-12') or
                                    x.endswith('-13') or
                                    x.endswith('-14'))
    else:
        raise ValueError("Unsupported server and total count configuration")

    # Find the datasets we want
    input_dir = Path('.') / 'data' / 'preprocessed' / 'edgelist'
    datasets = names_in_dir(input_dir, '.edgelist')
    datasets = [dataset.replace('.edgelist', '') for dataset in datasets]
    datasets = sorted(datasets)
    # Quantum data has no dashes, synthetics use dashes to separate parameters
    datasets = list(filter(seed_filter, datasets))

    # Execute experiments
    _execute_cplex(datasets)
    _execute_heuristic_ensemble(datasets)
    _execute_iterative_compression(datasets)
