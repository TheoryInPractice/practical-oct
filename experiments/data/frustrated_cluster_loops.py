"""Data generator for frustrated cluster loops.

https://docs.ocean.dwavesys.com/projects/dimod/en/latest/reference/bqm/generated/dimod.generators.fcl.frustrated_loop.html#dimod.generators.fcl.frustrated_loop
"""


# Imports
from itertools import product
from typing import Iterable
import argparse
import random

from dimod.generators.fcl import frustrated_loop
from matplotlib import pyplot as plt
import networkx as nx
import seaborn as sns

from experiments import FCL_DATA_DIR, logger
from src.preprocessing import graphs


# Constants
DEFAULT_CLIQUE_SIZES = (64, 96, 128)
DEFAULT_NUM_CYCLES = (1/3, 2/3, 3/3)
DEFAULT_NUM_FCLS = 10
SEED = 882351143
MIN_SEED = 0
MAX_SEED = 2**32 - 1


def generate_fcls(clique_sizes: Iterable[int] = DEFAULT_CLIQUE_SIZES,
                  num_cycles: Iterable[float] = DEFAULT_CLIQUE_SIZES,
                  num_fcls: int = DEFAULT_NUM_FCLS):
    """Generate frustrated cluster loops.

    Parameters
    ----------
    clique_sizes : Iterable[int, ...]
        Iterable of clique sizes to use in generating FCLs. A base clique of
        each size will be used to generate a set of
    num_cycles : Iterable[float, ...]
        Iterable of number of cycles to use in generating FCLs. Expressed as a
        percentage of ``n``, where ``n`` is the clique size.
    num_fcls : int
        Number of FCLs to generate for each combination of clique size and
        number of cycles.
    """
    # Get current random state and set seed
    state = random.getstate()
    random.seed(SEED)

    # All fcls
    fcls = []

    # Generate fcls
    for clique, cycles in product(clique_sizes, num_cycles):

        logger.info('Generating FCL for ({}, {:.2f})'.format(clique, cycles))

        for i in range(num_fcls):

            logger.info('---> Iteration {}'.format(i))

            # Generate binary quadratic model
            bqm = frustrated_loop(
                graph=clique,
                num_cycles=int(clique * cycles),
                seed=random.randint(MIN_SEED, MAX_SEED)
            )

            # Generate a graph from the non-zero edges
            fcl = nx.Graph()
            fcl.add_nodes_from(bqm.linear.keys())
            fcl.add_weighted_edges_from(
                (*e, w) for e, w in bqm.quadratic.items() if w
            )
            fcls.append(fcl)

            # Form filename
            fcl.graph['name'] = 'fcl_{}_{:.2f}_{}'.format(clique, cycles, i)

            # Write edgelist
            graphs.write_edgelist(fcl, FCL_DATA_DIR)

    # Plot stats
    x, y = zip(*map(lambda g: (len(g.nodes()), len(g.edges())), fcls))
    sns.scatterplot(
        x=x,
        y=y,
    )
    plt.savefig(str(FCL_DATA_DIR / 'plot.png'), dpi=300)
    plt.close()

    # Reset random state
    random.setstate(state)


def main():
    """Parse arguments and run frustrated loop generator."""
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--clique-sizes',
        nargs=3,
        type=int,
        default=DEFAULT_CLIQUE_SIZES,
        help='Size of input cliques. Must be (small, medium, large). '
             'Default = {}'.format(DEFAULT_CLIQUE_SIZES),
    )
    parser.add_argument(
        '--num-cycles',
        nargs=3,
        type=float,
        default=DEFAULT_NUM_CYCLES,
        help='Number of cycles in the FCL, expressed as a percentage of n. '
             'Default = ({:.2f}, {:.2f},  {:.2f})'.format(*DEFAULT_NUM_CYCLES),
    )
    parser.add_argument(
        '--num-fcls',
        type=int,
        default=DEFAULT_NUM_FCLS,
        help='Number of FCLs',
    )
    argv = parser.parse_args()

    # Generate FCLs
    generate_fcls(clique_sizes=argv.clique_sizes, num_cycles=argv.num_cycles)


# Invoke main
if __name__ == '__main__':
    main()
