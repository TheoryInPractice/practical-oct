"""Huffner based OCT solver."""


# Imports
from pathlib import Path
import argparse
import subprocess
import time


def solve(filename, timeout=None, preprocessing=0, seed=0, htime=0.25):
    """Solve OCT using Huffner.

    Parameters
    ----------
    filename : string
        Path to graph input file.
    timeout : float
        Timeout in seconds.
    preprocessing : int
        Preprocessing level to use.
    seed : int
        Seed to be used for shuffling.
    htime : float
        Number of seconds to run heuristics for. Defaults to 0.25.
    """

    # Get path to Huffner binary
    huffner = str(Path(__file__).parent.parent / 'huffner-src/occ')

    # Get start time
    start = time.time()

    # Create Huffner subprocess
    print('Calling {} -p {} -s {} -t {} -f {}'.format(huffner, str(preprocessing), str(seed), str(int(htime * 1000)), filename))
    proc = subprocess.Popen(
        [
            huffner,
            '-p', str(preprocessing),
            '-s', str(seed),
            '-t', str(int(htime * 1000)),
            '-f', filename
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    # Wait for results. If timeout is hit, terminate the process
    # and then get results.
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
        total_time = round(time.time() - start, 1)
    except subprocess.TimeoutExpired:
        proc.terminate()
        stdout, stderr = proc.communicate()
        total_time = timeout

    # Error if process failed
    if proc.returncode:
        raise Exception(stderr)

    # Decode stdout
    stdout = bytes.decode(stdout, 'utf-8').strip().split('\n')
    certificate = stdout[1:]

    # Return results
    return total_time, len(certificate), certificate


def main():
    """Main function. Parse args and run."""

    # Get an argument parser
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to a Huffner formatted graph file.')
    parser.add_argument(
        '--timeout',
        help='Optional timeout in seconds.',
        type=float
    )
    parser.add_argument(
        '--preprocessing',
        help='Preprocessing level (0, 1, 2).',
        type=int,
        default=0
    )
    parser.add_argument(
        '--seed',
        help='Seed for random generators.',
        type=int,
        default=0
    )
    parser.add_argument(
        '--htime',
        help='Milliseconds to run preprocessing for.',
        type=float,
        default=0.25
    )
    argv = parser.parse_args()

    # Run solver
    print('{},{},"{}"'.format(*solve(
        argv.file,
        timeout=argv.timeout,
        preprocessing=argv.preprocessing,
        seed=argv.seed,
        htime=argv.htime
    )))


# Invoke main
if __name__ == '__main__':
    main()
