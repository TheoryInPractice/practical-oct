"""Huffner self compairison script.

This script runs Huffner with each level of preprocessing
to determine relative performance. Each variant of Huffner
is run against datasets from huffner_experiment_datasets
with 50 unique seeds.

The timeout used will be the largest timeout in [0.01, 0.1, 1, 10]
seconds less than the time Huffner with no preprocessing took
to find an exact solution. This information is pulled from
paper_results/ic_baseline_experiment_results.csv, which
was computed by huffner_baseline.py. Any dataset not present
in this dataset timed out, so its runtime was > 10 minutes.
Any dataset reported as solved in less than the smallest timeout
will be run with the smallest timeout.

All results of this experiment are saved to the data file
results/ic_preprocessing_level.csv
"""


# Imports
from experiments import (
    headers,
    logger,
    HUFFNER_DATA_DIR,
    HUFFNER_DATA_EXT,
    PREPROCESSING_TIMEOUTS
)
from experiments.datasets import huffner_experiment_datasets
from experiments.ic import (
    PREPROCESSING_LEVELS,
    BASELINE_FILE,
    SELF_COMPARISON_DATA_PATH
)
from src.huffner.solver import solve
from collections import deque
from itertools import product
import csv
import pandas


# Constants
SEEDS = 50


def _get_timeouts():
    """Helper method for returning a dictionary of timeouts."""

    # Read baseline file
    baseline = pandas.read_csv(BASELINE_FILE)

    # Map time column to the largest timeout value that
    # is less than the reported time.
    def _largest_timeout(v):
        queue = deque(
            filter(lambda t: t < v, PREPROCESSING_TIMEOUTS),
            maxlen=1
        )
        try:
            return queue.pop()
        except IndexError:
            return PREPROCESSING_TIMEOUTS[0]
    baseline[headers.TIME] = baseline[headers.TIME].map(_largest_timeout)

    # Now convert this to a (dataset: timeout) dict.
    timeouts = pandas.Series(
        baseline[headers.TIME].values,
        index=baseline[headers.DATASET]
    ).to_dict()

    # Finally, add any datasets that didn't appear in the data
    # (they timed out on baseline)
    supplemental = {
        dataset: PREPROCESSING_TIMEOUTS[-1]
        for dataset in huffner_experiment_datasets
        if dataset not in timeouts
    }

    # Return the merged set
    return {**timeouts, **supplemental}


def _htime(timeout):
    """Amount of time to run heuristics for."""
    return min(0.3 * timeout, 1)


def main():
    """Run experiments."""

    # Load dataset timeouts
    timeouts = _get_timeouts()

    # Open output file
    with open(str(SELF_COMPARISON_DATA_PATH), 'w') as output:

        # Get writer
        writer = csv.writer(output)

        # Write header
        writer.writerow([
            'Dataset', 'Solver', 'Preprocessing', 'Timeout',
            'Seed', 'Time', 'Size', 'Certificate'
        ])

        # Run for each dataset
        for dataset in huffner_experiment_datasets:

            # Compute full dataset path
            dataset_path = str(
                HUFFNER_DATA_DIR / '{}{}'.format(dataset, HUFFNER_DATA_EXT)
            )

            # Iterate over all combinations of preprocessing level and seeds
            experiments = product(PREPROCESSING_LEVELS, range(1, SEEDS + 1))
            for preprocessing, seed in experiments:

                # Look up timeout and heuristics time
                timeout = timeouts[dataset]
                htime = _htime(timeout)

                # Log progress
                logger.info(
                    'Running {} with preprocessing={}, '
                    'seed={}, timeout={}, htime={}'
                    .format(dataset, preprocessing, seed, timeout, htime)
                )

                # Run without preprocessing
                solution = solve(
                    dataset_path,
                    timeout=timeout,
                    preprocessing=preprocessing,
                    seed=seed,
                    htime=htime
                )
                writer.writerow([
                    dataset,
                    'huffner',
                    preprocessing,
                    timeout,
                    seed,
                    *solution
                ])
                output.flush()

    # With print context
    context = pandas.option_context(
        'display.max_rows', None,
        'display.max_columns', None,
        'display.max_colwidth', 70,
        'expand_frame_repr', False,
        'justify', 'right'
    )
    with context:
        results = pandas.read_csv(str(SELF_COMPARISON_DATA_PATH))
        results = results[['Dataset', 'Preprocessing', 'Size']]
        print(results.groupby(['Dataset', 'Preprocessing']).describe())


if __name__ == '__main__':
    main()
