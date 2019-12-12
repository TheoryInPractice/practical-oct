"""Run Akiba-Iwata solver and print the result."""


# Imports
from typing import List
import argparse
import subprocess
import time


def _certificate_to_oct(num_vertices: int,
                        certificate: List[int]) -> List[int]:
    """Transform a VC certificate into an OCT certificate

    Parameters
    ----------
    num_vertices : int
        The number of vertices present in the VC formulation graph. This graph
        is expected to have vertex labels normalized to the range
        0..num_vertices.
    certificate : List[int]
        Vertices present in a solution to the VC formulation.

    Returns
    -------
    List[int]
        A list of vertices forming a valid certificate to the OCT formulation
        of the problem.
    """
    if not num_vertices % 2 == 0:
        raise Exception(
            'Converting a certificate from the VC formulation to the OCT '
            'formulation expects an even number of vertices.'
        )

    # The VC formulation doubles OCT vertices, so halve the number of vertices
    # to go in the opposite direction.
    num_vertices //= 2

    # Store all vertices in the certificate as a set
    vertex_set = set(certificate)

    # Construct new vertex
    return [
        n
        for n in range(num_vertices)
        if n in vertex_set and (n + num_vertices) in vertex_set
    ]


def solve(filename, timeout=None, convert_to_oct=False):
    """Run akiba-iwata on the given file.

    Parameters
    ----------
    filename : string
        File containing problem definition
    timeout : float
        Optional timeout in seconds
    convert_to_oct : bool
        Whether or not to convert to an OCT certificate

    Returns
    -------
    tuple
        (time, size, certificate)

    Raises
    ------
    subprocess.TimeoutExpired
        Raised if a timeout is specified and no solution is found
        within the timelimit. The process is killed beforehand.
    """

    # Read first line of file to get number of vertices
    with open(filename, 'r') as ifile:
        num_vertices = int(ifile.readline().split()[2])

    # Get start time
    start = time.time()

    # Create subprocess
    proc = subprocess.Popen(
        ['java', '-cp', 'src/akiba-iwata-src/bin', 'Main', '-p', filename],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )

    # Wait with timeout for the process to finish and grab output.
    try:
        stdout, stderr = proc.communicate(timeout=timeout)
    except subprocess.TimeoutExpired:
        proc.kill()
        raise

    # Get total time
    total_time = time.time() - start

    # Get output and pop the first line (which is the size)
    certificate = list(map(int, bytes.decode(stdout, 'utf-8').strip().split()))
    certificate.pop(0)

    # Convert to OCT
    if convert_to_oct:
        certificate = _certificate_to_oct(num_vertices, certificate)

    # Return
    return round(total_time, 1), len(certificate), certificate


def main():
    """Run."""

    # Get an argument parser and parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument('file', help='Path to a snap formatted graph file.')
    parser.add_argument(
        '--timeout',
        help='Optional timeout in seconds.',
        type=float
    )
    parser.add_argument(
        '--convert-to-oct',
        help='Whether or not the solution should be converted to an OCT set.',
        action='store_true'
    )
    argv = parser.parse_args()

    # Run and print
    try:
        print('{},{},"{}"'.format(*solve(
            argv.file,
            timeout=argv.timeout,
            convert_to_oct=argv.convert_to_oct
        )))
    except subprocess.TimeoutExpired:
        print('Timeout Expired. No solution found.')


# Invoke main
if __name__ == '__main__':
    main()
