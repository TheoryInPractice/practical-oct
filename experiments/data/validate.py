"""
Validate that each synthetic graph matches the expected number of vertices and
edges for the given seed.
"""

import argparse
from pathlib import Path
from src.preprocessing.graphs import (
    names_in_dir
)


def _generate_summary_csv(csv_dir, summary_filename):
    """Summarize the synthetic dataset info into a standardized CSV"""
    # Read existing graphs from the sanitized folder
    sanitized_dir = Path('.') / 'data' / 'sanitized'
    input_dir = sanitized_dir / 'edgelist'
    datasets = names_in_dir(input_dir, '.edgelist')
    # Keep only the synthetic data
    datasets = sorted(list(filter(lambda x: '-' in x, datasets)))

    with open(str(csv_dir / summary_filename), 'w') as outfile:
        outfile.write('dataset,vertices,edges\n')
        for dataset in datasets:
            filename = str(input_dir / dataset) + '.edgelist'
            print(filename)
            with open(filename, 'r') as infile:
                vertices, edges = map(int, infile.readline().split())
                outfile.write('{},{},{}\n'.format(dataset, vertices, edges))
    print('Wrote {}'.format(summary_filename))


def _compare_to_ground_truth(csv_dir, summary_filename, ground_truth_filename):
    with open(str(csv_dir / summary_filename), 'r') as file1:
        with open(str(csv_dir / ground_truth_filename), 'r') as file2:
            for line1, line2 in zip(file1.readlines(), file2.readlines()):
                if line1 != line2:
                    raise ValueError("Lines didn't match: '{}' and '{}''".format(
                        line1.strip(), line2.strip()))
            print('All synthetic data matches expectations!')


if __name__ == '__main__':
    # Obtain the precomputed results file
    parser = argparse.ArgumentParser(description='')
    parser.add_argument(
        '-precomputed',
        type=str,
        help='Filename for the precomputed results to validate against',
        required=True)
    args = parser.parse_args()

    # Compare current results with specified results file
    csv_dir = Path('.') / 'experiments' / 'data'
    _generate_summary_csv(csv_dir, 'synthetic_summary.csv')
    _compare_to_ground_truth(
        csv_dir, 'synthetic_summary.csv', args.precomputed)
