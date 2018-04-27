"""Huffner experiment using heuristics.

This experiment generates data to compare
Huffner against CPLEX and our heuristics
ensemble at timeouts of [0.01, 0.1, 1, 10]
seconds. We use the version of Huffner
with heuristic preprocessing and density
sorting.

All data is logged to results/ic_heuristics.csv
"""


# Imports
from experiments import (
    logger,
    HUFFNER_DATA_DIR,
    HUFFNER_DATA_EXT,
    PREPROCESSING_TIMEOUTS
)
from experiments.datasets import preprocessed
from experiments.heuristic import (
    HUFFNER_P1,
    HUFFNER_P2,
    HUFFNER_RESULTS_DATA_FILE,
    HUFFNER_CSV_HEADERS
)
from src.huffner.solver import solve
from itertools import product
import csv


# Constants
PREPROCESSING_ENSEMBLE = 1
PREPROCESSING_DENSITY = 2


def main():
    """Run experiment."""

    # Open output file for writing
    with open(str(HUFFNER_RESULTS_DATA_FILE), 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow(HUFFNER_CSV_HEADERS)

        # Run all combinations of dataset and timeouts
        experiments = product(preprocessed, PREPROCESSING_TIMEOUTS)
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
            solution = solve(
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


# Invoke main
if __name__ == '__main__':
    main()
