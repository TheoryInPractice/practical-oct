"""Run heuristics experiments."""


# Imports
from experiments import (
    logger,
    PREPROCESSING_TIMEOUTS_MILLISECONDS,
    EDGELIST_DATA_DIR,
    EDGELIST_DATA_EXT,
    PROJECT_ROOT
)
from experiments.datasets import preprocessed
from experiments.heuristic import (
    HEURISTICS_RESULTS_DATA_FILE,
    HEURISTICS_CSV_HEADERS
)
from itertools import product
import csv
import os
import re
import subprocess


# Define experiment parameters
DATASETS = list(map(
    lambda d: str(EDGELIST_DATA_DIR / (d + EDGELIST_DATA_EXT)),
    preprocessed
))
HEURISTIC_SOLVER = PROJECT_ROOT / 'src/heuristics/heuristic_solver'


def main():
    """Run experiments"""

    # Log
    logger.info('Starting Heuristics Experiment')

    # Generate experiments
    experiments = product(PREPROCESSING_TIMEOUTS_MILLISECONDS, DATASETS)

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


if __name__ == '__main__':
    main()
