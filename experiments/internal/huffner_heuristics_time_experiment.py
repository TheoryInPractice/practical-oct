"""Huffner experiment for heuristics comparison.

This script tests the effect varying the proportion of
time Huffner spends running heuristics vs iterative
compression.
"""


# Imports
from experiments import (
    headers,
    logger,
    HUFFNER_DATA_DIR,
    HUFFNER_DATA_EXT,
    PREPROCESSING_TIMEOUTS,
    RESULTS_DIR
)
from experiments.datasets import preprocessed
from src.huffner.solver import solve
from itertools import product
import csv


# Constants
DATAFILE = RESULTS_DIR / 'huffner_heuristics_comparison_results.csv'
HTIME_PERCENTS = [0.1, 0.2, 0.3, 0.4, 0.5]
PREPROCESSING = 2


def main():
    """Run experiment."""

    # Open output file for writing
    with open(str(DATAFILE), 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            headers.DATASET, headers.SOLVER, headers.TIMEOUT,
            headers.HTIME, headers.TIME, headers.SIZE,
            headers.CERTIFICATE
        ])

        # Iterate over all combinations of timeouts and percents
        experiments = product(PREPROCESSING_TIMEOUTS, HTIME_PERCENTS)
        for timeout, percent in experiments:

            # Compute htime
            htime = round(timeout * percent, 4)

            # Iterate over all datasets
            for dataset in preprocessed:

                # Log
                logger.info(
                    'Computing OCT for {} with timeout={}, htime={}'
                    .format(dataset, timeout, htime)
                )

                # Run solver
                solution = solve(
                    str(HUFFNER_DATA_DIR / (dataset + HUFFNER_DATA_EXT)),
                    timeout=timeout,
                    preprocessing=PREPROCESSING,
                    htime=htime
                )

                # Write data
                writer.writerow([
                    dataset,
                    'huffner',
                    timeout,
                    htime,
                    *solution
                ])
                output.flush()


# Invoke main
if __name__ == '__main__':
    main()
