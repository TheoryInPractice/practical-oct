"""Experiment runner.

This frustrated cluster loop experiment runs heuristic solvers against the FCL
dataset. Heuristics are run at different timeout levels.
"""


# Imports
from itertools import product
from typing import Set, Tuple
import csv
import re
import subprocess

from experiments import logger, PROJECT_ROOT, FCL_DATA_DIR, RESULTS_DIR
from src.huffner.solver import solve as solve_ic
from src.ilp.solver import read_edgelist, solve as solve_ilp


# Paths
HEURISTIC_SOLVER = str(PROJECT_ROOT / 'src/heuristics/heuristic_solver')
RESULTS_FILE = str(RESULTS_DIR / 'fcls_heuristic_experiment.csv')


# Constants
HE = 'HE'
ILP = 'ILP'
IC = 'IC'
HEURISTIC_TIMEOUTS_S = (0.01, 0.1, 1.0, 10.0,)
OUTPUT_HEADER = [
    'Dataset',
    'Solver',
    'Timeout',
    'Time',
    'Size',
    'Certificate',
]


def _run_he(name: str, timeout: int) -> Tuple[int, float, str]:
    """Run heuristic ensemble on all datasets.

    The ensemble will be run once for each timeout.

    Parameters
    ----------
    name : str
        Dataset name.
    timeout : int
        Timeout in seconds.

    Returns
    -------
    Tuple[int, float, str]
        Solution size, time, and certificate.
    """
    # Execute
    # The heuristic ensemble expects timeout in milliseconds.
    proc = subprocess.run(
        [
            HEURISTIC_SOLVER,
            str(int(1000 * timeout)),
            str(FCL_DATA_DIR / 'edgelist/{}.edgelist'.format(name))
        ],
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
    time = int(match.group(2)) / 1000
    certificate = match.group(3)

    # Return
    return size, time, certificate


def _run_ilp(name: str, timeout: int) -> Tuple[int, float, str]:
    """Run ILP on all datasets.

    Parameters
    ----------
    name : str
        Dataset name.
    timeout : int
        Timeout in seconds.

    Returns
    -------
    Tuple[int, float, str]
        Solution size, time, and certificate.
    """
    # Execute
    # Solved using CPLEX with timeout for a partial solution
    solution = solve_ilp(
        read_edgelist(str(FCL_DATA_DIR / 'snap/{}.snap'.format(name))),
        formulation='VC',
        solver='CPLEX',
        threads=1,
        timelimit=timeout,
        convert_to_oct=True
    )

    # Return
    return solution.opt, solution.time, solution.certificate


def _run_ic(name: str, timeout: int) -> Tuple[int, float, str]:
    """Run iterative compression on all datasets.

    Parameters
    ----------
    name : str
        Dataset name.
    timeout : int
        Timeout in seconds.

    Returns
    -------
    Tuple[int, float, str]
        Solution size, time, and certificate.
    """
    # Determine preprocessing level
    if timeout <= 0.1:
        preprocessing = 1
    else:
        preprocessing = 2

    # Execute
    time, size, certificate = solve_ic(
        str(FCL_DATA_DIR / 'huffner/{}.huffner'.format(name)),
        timeout=timeout,
        preprocessing=preprocessing,
        htime=min(0.3 * timeout, 1)
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
    solvers = [(HE, _run_he), (ILP, _run_ilp), (IC, _run_ic)]

    # Open results file context
    with open(RESULTS_FILE, 'w') as results_file_fd:

        # Create CSV writer and write heuristic header row
        csv_writer = csv.writer(results_file_fd)
        csv_writer.writerow(OUTPUT_HEADER)

        # Execute for each pair of dataset and timeout
        for name, timeout in product(_datasets(), HEURISTIC_TIMEOUTS_S):

            logger.info('Solving {} with timeout {}ms'.format(name, timeout))

            # Execute for each solver
            for sn, solver in solvers:

                logger.info('Running solver {}'.format(sn))

                # Try to execute heuristics
                try:

                    size, time, certificate = solver(name, timeout)

                    # Write results
                    csv_writer.writerow([
                        name,
                        sn,
                        timeout,
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
                        timeout,
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
