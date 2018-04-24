"""Sanity check that two preprocessed datasets are probably isomorphic."""


# Inputs
from experiments import logger, EDGELIST_DATA_EXT
from pathlib import Path
from src.preprocessing import graphs
import sys


# Constants
EDGELIST_GLOB = '*{}'.format(EDGELIST_DATA_EXT)


def _glob_edgelists(path):
    """Return the set of all .edglist files at a path."""

    return set(map(lambda p: p.name, path.glob(EDGELIST_GLOB)))


def main():
    """Validate."""

    # Validate directories
    argv = sys.argv[1:]
    if len(argv) != 2:
        raise Exception(
            'Usage: python -m experiments.sanity_check_preprocessing '
            '<preprocessed data dir> <preprocessed data dir>'
        )
    dir1 = Path(argv[0]) / 'edgelist'
    dir2 = Path(argv[1]) / 'edgelist'

    logger.info('Loading edgelists from `{}`'.format(dir1))
    logger.info('Loading edgelists from `{}`'.format(dir2))

    # Get common edgelist files
    edgelists = _glob_edgelists(dir1) & _glob_edgelists(dir2)
    logger.info('Found {} shared edgelist files'.format(len(edgelists)))

    # Check each
    for edgelist in edgelists:

        logger.info('Validating `{}`'.format(edgelist))

        # Construct graphs from edgelists
        g1 = graphs.read_edgelist(dir1, edgelist)
        g2 = graphs.read_edgelist(dir2, edgelist)

        # Check for isomorphism
        if not graphs.could_be_isomorphic(g1, g2):
            logger.info('`{}` is not isomorphic'.format(edgelist))


# Invoke main
if __name__ == '__main__':
    main()
