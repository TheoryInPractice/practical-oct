"""Compute huffner baseline data."""


# Imports
from experiments import (
    headers,
    logger,
    EXACT_TIMEOUT,
    HUFFNER_DATA_DIR,
    HUFFNER_DATA_EXT
)
from experiments.ic import BASELINE_FILE
from experiments.datasets import huffner_experiment_datasets
from src.huffner.solver import solve
import csv
import subprocess


# Constants
HUFFNER_BASELINE_SOLVER = 'huffner_baseline'


def main():
    """Run experiment."""

    # Open output file for writing
    with open(BASELINE_FILE, 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            headers.DATASET, headers.SOLVER,
            headers.TIME, headers.SIZE, headers.CERTIFICATE
        ])

        # Run experiments
        for dataset in huffner_experiment_datasets:

            # Log
            logger.info('Computing OCT for {}'.format(dataset))

            # Solve and write output
            try:
                solution = solve(
                    str(HUFFNER_DATA_DIR / (dataset + HUFFNER_DATA_EXT)),
                    timeout=EXACT_TIMEOUT
                )
                if solution[0] >= EXACT_TIMEOUT:
                    continue
            except subprocess.TimeoutExpired:
                continue

            writer.writerow([
                dataset,
                HUFFNER_BASELINE_SOLVER,
                *solution
            ])
            output.flush()


# Invoke main
if __name__ == '__main__':
    main()
