"""Experiment for heuristic solutions"""
# Imports
import argparse
import csv
from itertools import product
import logging
from pathlib import Path
import re
import subprocess

# Imports from this project
from src.huffner.solver import solve as solve_ic
from src.ilp.solver import read_edgelist, solve as solve_ilp
from src.preprocessing.graphs import names_in_dir

# Init logger
logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger('tuning_oct')
logger.setLevel(logging.INFO)


def _execute_cplex(configurations, outfile, csv_writer):
    """
    Execute CPLEX on a list of (data, timeout) configurations, writing output
    to csv_writer.
    """
    logger.info('Starting CPLEX Heurisitc Experiment')

    # Execute all configurations
    for (dataset, timeout) in configurations:
        try:
            logger.info(
                'Executing CPLEX on {} with timeout {}s'
                .format(dataset, timeout)
            )

            # Execute CPLEX on one configuration
            solution = solve_ilp(
                read_edgelist(dataset),
                formulation='VC',
                solver='CPLEX',
                threads=1,
                timelimit=timeout,
                convert_to_oct=True
            )

            # Write
            csv_writer.writerow([
                dataset.split('/')[-1].replace('.snap', ''),
                'ilp_1',
                timeout,
                solution.time,
                solution.opt,
                solution.certificate
            ])
            outfile.flush()

        except Exception as e:
            logger.error(e)


def _execute_heuristic_ensemble(configurations, outfile, csv_writer):
    """
    Execute the heuristic ensemble on a list of (data, timeout) configurations,
    writing output to csv_writer.
    """
    logger.info('Starting Heuristics Ensemble Heuristic Experiment')

    # Execute all configurations
    for (dataset, timeout) in configurations:
        logger.info(
            'Executing HE on {} with timeout {}ms'.format(dataset, timeout)
        )

        # Execute configuration
        solver = str(Path('.') / 'src' / 'heuristics' / 'heuristic_solver')
        proc = subprocess.run(
            [solver, timeout, dataset],
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

        # Write results
        csv_writer.writerow([
            dataset.split('/')[-1].replace('.edgelist', ''),
            'he',
            timeout,
            time,
            size,
            certificate
        ])
        outfile.flush()


def _execute_iterative_compression(configurations, outfile, csv_writer):
    """
    Execute iterative compression on a list of (data, timeout) configurations,
    writing output to csv_writer.
    """
    logger.info('Starting Iterative Compression Heuristic Experiment')
    # Run all combinations of dataset and timeouts
    for (dataset, timeout) in configurations:
        logger.info(
            'Executing IC on {} with timeout {}s'.format(dataset, timeout)
        )

        # Determine preprocessing level and solver name
        if timeout <= 0.1:
            preprocessing = 1
        else:
            preprocessing = 2

        # Solve
        time, size, certificate = solve_ic(
            dataset,
            timeout=timeout,
            preprocessing=preprocessing,
            htime=min(0.3 * timeout, 1)
        )

        # Write output
        csv_writer.writerow([
            dataset.split('/')[-1].replace('.huffner', ''),
            'ic',
            timeout,
            time,
            size,
            certificate
        ])
        outfile.flush()


def _init_args():
    """
    Initialize the argparser used for the command-line interface.
    Returns the arguments.
    """
    # Obtain the server number needed to split the data
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-server',
        type=int,
        required=True,
        help='Current server number between 1 and total number of servers')
    parser.add_argument(
        '-of',
        type=int,
        required=True,
        help='Total number of servers')
    parser.add_argument(
        '-seeds',
        type=int,
        nargs='+',
        required=True,
        help='Dataset seeds to use')
    return parser.parse_args()


if __name__ == '__main__':
    """
    Command-line script for executing the heuristic experiment.
    Splits work across servers by partitioning seeds.
    """
    # Retrive the command-line arguments
    args = _init_args()

    # Ensure the command-line args are reasonable
    if args.server > args.of:
        raise ValueError('Unsupported server and total count configuration')
    elif args.of > len(args.seeds):
        print('Warning: Fewer seeds than total servers')

    # Find all datasets
    input_dir = Path('.') / 'data' / 'preprocessed' / 'edgelist'
    datasets = names_in_dir(input_dir, '.edgelist')
    # Take the subset of datasets that matches our seeds
    valid_suffixes = tuple(map(lambda x: '-{}'.format(x), args.seeds))
    datasets = sorted(list(filter(lambda x: x.endswith(valid_suffixes),
                                  datasets)))
    # Split data across servers
    datasets = datasets[args.server-1::args.of]

    # Define timeouts
    timeouts_in_seconds = [0.01, 0.1, 1, 10]
    timeouts_in_milliseconds = ['10', '100', '1000', '10000']

    print(
        'Starting experiment with {} datasets and timeouts {}'
        .format(len(datasets), timeouts_in_seconds))
    print(datasets)

    # Define header used in CSV output
    csv_header = [
        'Dataset',
        'Solver',
        'Timeout',
        'Time',
        'Size',
        'Certificate'
    ]

    # Execute the iterative compression solver
    dir = Path('.') / 'data' / 'preprocessed' / 'huffner'
    extension = '.huffner'
    ic_data = [str(dir / dataset) + extension for dataset in datasets]
    configurations = product(ic_data, timeouts_in_seconds)
    outfile_path = Path('.') / 'results' / 'ic_heuristic_experiment.csv'
    with open(str(outfile_path), 'w') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(csv_header)
        _execute_iterative_compression(configurations, outfile, csv_writer)

    # Execute CPLEX
    dir = Path('.') / 'data' / 'preprocessed' / 'snap'
    extension = '.snap'
    cplex_data = [str(dir / dataset) + extension for dataset in datasets]
    configurations = product(cplex_data, timeouts_in_seconds)
    outfile_path = Path('.') / 'results' / 'ilp_heuristic_experiment.csv'
    with open(str(outfile_path), 'w') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(csv_header)
        _execute_cplex(configurations, outfile, csv_writer)

    # Execute Heuristic Ensemble
    dir = Path('.') / 'data' / 'preprocessed' / 'edgelist'
    extension = '.edgelist'
    he_data = [str(dir / dataset) + extension for dataset in datasets]
    configurations = product(he_data, timeouts_in_milliseconds)
    outfile_path = Path('.') / 'results' / 'he_heiristic_experiment.csv'
    with open(str(outfile_path), 'w') as outfile:
        csv_writer = csv.writer(outfile)
        csv_writer.writerow(csv_header)
        _execute_heuristic_ensemble(configurations, outfile, csv_writer)
