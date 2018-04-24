"""Run cplex experiments."""


# Imports
from experiments import (
    logger,
    SNAP_DATA_DIR,
    SNAP_DATA_EXT,
    PREPROCESSING_TIMEOUTS
)
from experiments.datasets import preprocessed
from experiments.heuristic import (
    CPLEX_RESULTS_DATA_FILE,
    HEURISTICS_CSV_HEADERS
)
from src.ilp.solver import solve, read_edgelist
from itertools import product
import csv
import os


def main():
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


if __name__ == '__main__':
    main()
