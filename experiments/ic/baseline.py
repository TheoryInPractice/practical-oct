"""Compute huffner baseline data."""


# Imports
from experiments import (
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


def main():
    """Run experiment."""

    # Open output file for writing
    with open(BASELINE_FILE, 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Dataset', 'Time', 'Size', 'Certificate'
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
                *solution
            ])
            output.flush()


# Invoke main
if __name__ == '__main__':
    main()
