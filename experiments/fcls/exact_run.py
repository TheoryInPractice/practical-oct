"""Experiment runner.

This frustrated cluster loop experiment runs exact solvers against the FCL
dataset. Solvers are run with a timeout.
"""


# Imports
from typing import Set, Tuple
import csv

from experiments import (
    logger,
    FCL_DATA_DIR,
    RESULTS_DIR,
    EXACT_TIMEOUT,
    SNAP_DATA_EXT,
    HUFFNER_DATA_EXT
)
from src.akiba_iwata.solver import solve as solve_ai
from src.huffner.solver import solve as solve_ic
from src.ilp.solver import read_edgelist, solve as solve_ilp


# Paths
RESULTS_FILE = str(RESULTS_DIR / 'fcls_exact_experiment.csv')


# Constants
AI = 'AI'
IC = 'IC'
ILP = 'ILP'
OUTPUT_HEADER = [
    'Dataset',
    'Solver',
    'Time',
    'Size',
    'Certificate',
]


def _run_ai(name: str) -> Tuple[int, float, str]:
    """Run Akiba-Iwata on a dataset.

    Parameters
    ----------
    name : str
        Dataset name.

    Returns
    -------
    Tuple[int, float, str]
        Solution size, time, and certificate.
    """
    # Execute
    time, size, certificate = solve_ai(
        str(FCL_DATA_DIR / 'snap' / (name + SNAP_DATA_EXT)),
        timeout=EXACT_TIMEOUT,
        convert_to_oct=True
    )
    return size, time, certificate


def _run_ilp(name: str) -> Tuple[int, float, str]:
    """Run ILP on all datasets.

    Parameters
    ----------
    name : str
        Dataset name.

    Returns
    -------
    Tuple[int, float, str]
        Solution size, time, and certificate.
    """
    # Execute
    solution = solve_ilp(
        read_edgelist(str(FCL_DATA_DIR / 'snap' / (name + SNAP_DATA_EXT))),
        formulation='VC',
        solver='CPLEX',
        threads=4,
        timelimit=EXACT_TIMEOUT,
        convert_to_oct=True
    )

    # Return
    return solution.opt, solution.time, solution.certificate


def _run_ic(name: str) -> Tuple[int, float, str]:
    """Run iterative compression on all datasets.

    Parameters
    ----------
    name : str
        Dataset name.

    Returns
    -------
    Tuple[int, float, str]
        Solution size, time, and certificate.
    """
    # Execute
    time, size, certificate = solve_ic(
        str(FCL_DATA_DIR / 'huffner' / (name + HUFFNER_DATA_EXT)),
        timeout=EXACT_TIMEOUT,
        preprocessing=2,
        htime=min(0.3 * EXACT_TIMEOUT, 1)
    )

    # Return
    return size, time, str(certificate)


def _datasets() -> Set[str]:
    """Get FCL datasets available in all formats.

    Returns
    -------
    Set[str]
        Names of all available datasets.
    """
    edgelist = set(map(
        lambda p: p.stem,
        (FCL_DATA_DIR / 'edgelist').glob('*')
    ))
    huffner = set(map(
        lambda p: p.stem,
        (FCL_DATA_DIR / 'huffner').glob('*')
    ))
    snap = set(map(
        lambda p: p.stem,
        (FCL_DATA_DIR / 'snap').glob('*')
    ))

    return edgelist & huffner & snap


def main():
    """Parse arguments and run experiment."""
    logger.info('Starting FCL experiment.')

    # List solvers to use
    solvers = [(AI, _run_ai), (ILP, _run_ilp), (IC, _run_ic)]

    # Open results file context
    with open(RESULTS_FILE, 'w') as results_file_fd:

        # Create CSV writer and write heuristic header row
        csv_writer = csv.writer(results_file_fd)
        csv_writer.writerow(OUTPUT_HEADER)

        # Execute for each dataset
        for name in _datasets():

            logger.info('Solving {}'.format(name))

            # Execute for each solver
            for sn, solver in solvers:

                logger.info('Running solver {}'.format(sn))

                # Try to execute heuristics
                try:

                    size, time, certificate = solver(name)

                    # Write results
                    csv_writer.writerow([
                        name,
                        sn,
                        time,
                        size,
                        certificate
                    ])

                except Exception as e:

                    # Log error
                    logger.error(e)

                    # Write empty row
                    csv_writer.writerow([
                        name,
                        sn,
                        float('nan'),
                        float('nan'),
                        float('nan')
                    ])

                finally:

                    # Flush results so we at least get partial results if
                    # something catastrophic causes the script to crash.
                    results_file_fd.flush()


# Invoke main
if __name__ == '__main__':
    main()