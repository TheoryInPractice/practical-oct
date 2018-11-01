"""Utility for downloading and formatting data.

This utility does not perform preprocessing. See `experiments/preprocessing/`
and `src/preprocessing/` for all implementation regarding preprocesisng
routines.
"""


# Imports
from pathlib import Path
from urllib.request import urlretrieve
import re
import shutil
import subprocess


# Data sources
HUFFNER_SRC = 'https://github.com/tdgoodrich/occ_cpp.git'
BEASLEY_SRC = 'http://people.brunel.ac.uk/~mastjjb/jeb/orlib/files'
BQP_FILES = [
    'bqp50.txt',
    'bqp100.txt',
    'bqp250.txt',
    'bqp500.txt'
]
GKA_SRC_NAME = 'bqpgka.txt'
GKA_FILE_NAME = '_gka.txt'


# Directories
DATA_DIR = Path(__file__).parent.parent / 'data'
TMP_DIR = DATA_DIR / 'tmp'
ORIGINAL_DATA_DIR = DATA_DIR / 'original'
HUFFNER_DATA_DIR = ORIGINAL_DATA_DIR / 'huffner'
BEASLEY_DATA_DIR = ORIGINAL_DATA_DIR / 'beasley'
GKA_DATA_DIR = ORIGINAL_DATA_DIR / 'gka'


def _download_huffner():
    """Download and extract huffner data."""

    # Make sure data dir exists
    HUFFNER_DATA_DIR.mkdir(exist_ok=True, parents=True)

    # Clear temporary directory
    if TMP_DIR.exists():
        shutil.rmtree(str(TMP_DIR))

    # Now clone huffner
    subprocess.run(
        [
            'git',
            'clone',
            str(HUFFNER_SRC),
            str(TMP_DIR)
        ],
        check=True
    )

    # Now move files
    for src in TMP_DIR.glob('data/*/*.graph'):

        # Compute destination path
        if src.parent.name == 'japanese':
            dest = HUFFNER_DATA_DIR / 'j{}'.format(src.name)
        else:
            dest = HUFFNER_DATA_DIR / 'aa{}'.format(src.name)

        # Move
        shutil.move(str(src), str(dest))


def _download_beasley():
    """Download beasley files."""

    # Create beasey data dir
    BEASLEY_DATA_DIR.mkdir(exist_ok=True, parents=True)

    # Download each beasley file
    for datafile in BQP_FILES:
        urlretrieve(
            '{}/{}'.format(BEASLEY_SRC, datafile),
            filename=str(BEASLEY_DATA_DIR / ('_' + datafile))
        )


def _download_gka():
    """Download gka files."""

    # Create gka data dir
    GKA_DATA_DIR.mkdir(exist_ok=True, parents=True)

    # Download gka file
    urlretrieve(
        '{}/{}'.format(BEASLEY_SRC, GKA_SRC_NAME),
        filename=str(GKA_DATA_DIR / '_gka.txt')
    )


def _decompress(path):
    """Decompress a dataset."""

    # Open data file and output file
    with open(str(path), 'r') as infile:

        # Get number of graphs
        num_data = int(infile.readline())

        # Parse each
        for data in range(1, num_data + 1):

            # Format output path
            outpath = path.parent / '{}_{}.txt'.format(
                re.match(r'_?([a-zA-Z0-9]+).txt', path.name).group(1),
                data
            )

            # Write
            with open(str(outpath), 'w') as outfile:
                stats = infile.readline()
                outfile.write(stats)
                num_v, num_e = map(int, stats.split())
                for _ in range(num_e):
                    outfile.write(infile.readline())


def _decompress_all():
    """Decompress all datafiles."""

    # Decompress all BQP files
    for datafile in BQP_FILES:
        _decompress(BEASLEY_DATA_DIR / ('_' + datafile))

    # Decompress gka
    _decompress(GKA_DATA_DIR / GKA_FILE_NAME)


def _remove_empty_huffner():
    """Removes Huffner graphs known to be empty"""
    (Path('.') / 'data' / 'original' / 'huffner' / 'aa12.graph').unlink()
    (Path('.') / 'data' / 'original' / 'huffner' / 'j12.graph').unlink()
    (Path('.') / 'data' / 'original' / 'huffner' / 'j27.graph').unlink()


def main():
    """Download and place data into the data dir."""

    # If the data dir does not exist, create it now
    DATA_DIR.mkdir(exist_ok=True, parents=True)

    # Download data
    _download_huffner()
    _download_beasley()
    _download_gka()
    _decompress_all()

    # Remove bad files
    _remove_empty_huffner()

    # Delete temp directory
    if TMP_DIR.exists():
        shutil.rmtree(str(TMP_DIR))


if __name__ == '__main__':
    main()
