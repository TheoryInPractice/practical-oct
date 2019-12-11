"""Data generator for frustrated cluster loops.

https://docs.ocean.dwavesys.com/projects/dimod/en/latest/reference/bqm/generated/dimod.generators.fcl.frustrated_loop.html#dimod.generators.fcl.frustrated_loop
"""


# Imports
from itertools import product
from typing import Iterable, Optional
import argparse
import random

from dimod.generators.fcl import frustrated_loop
from matplotlib import pyplot as plt
import networkx as nx
import seaborn as sns

from experiments import FCL_DATA_DIR, logger
from src.preprocessing import graphs


# Paths
PLOT = str(FCL_DATA_DIR / 'plot.png')


# Constants
DEFAULT_CLIQUE_SIZES = (64, 80, 96, 112, 128,)
DEFAULT_NUM_CYCLES = (0.05, 0.10, 0.15, 0.20, 0.25, 0.3)
DEFAULT_NUM_FCLS = 5
DEFAULT_SEED = 882351143
MIN_SEED = 0
MAX_SEED = 2**32 - 1
DPI = 300


def generate_fcls(clique_sizes: Iterable[int] = DEFAULT_CLIQUE_SIZES,
                  num_cycles: Iterable[float] = DEFAULT_CLIQUE_SIZES,
                  num_fcls: int = DEFAULT_NUM_FCLS,
                  seed: Optional[int] = DEFAULT_SEED):
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
    seed : Optional[int]
        Seed for randomness in generating FCLs. Setting this guarantees a
        deterministic outcome.
    """
    # Create output directories
    edgelist_dir = FCL_DATA_DIR / 'edgelist'
    edgelist_dir.mkdir(exist_ok=True, parents=True)
    huffner_dir = FCL_DATA_DIR / 'huffner'
    huffner_dir.mkdir(exist_ok=True, parents=True)
    snap_dir = FCL_DATA_DIR / 'snap'
    snap_dir.mkdir(exist_ok=True, parents=True)

    # Get current random state and set seed
    if seed is not None:
        state = random.getstate()
        random.seed(seed)
    else:
        state = None

    # All fcls and plotting data
    fcls = []
    data = []

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
            fcl.add_weighted_edges_from(
                (*e, w) for e, w in bqm.quadratic.items() if w
            )

            # Set graph name (will be used as filename)
            fcl.graph['name'] = 'fcl_{}_{:.2f}_{}'.format(clique, cycles, i)

            # Normalize node labels to integers in the range 0..n.
            fcl = graphs.reset_labels(fcl)

            # Store
            fcls.append(fcl)
            graphs.write_edgelist(fcl, edgelist_dir)
            graphs.write_huffner(fcl, huffner_dir)
            graphs.write_snap(fcl, snap_dir)
            data.append((
                len(fcl.nodes()),
                len(fcl.edges()),
                (clique, cycles,),
            ))

    # Plot stats
    x, y, hue = zip(*data)
    sns.scatterplot(x=x, y=y, hue=hue)
    plt.title('Frustrated Cluster Loops')
    plt.xlabel('Nodes')
    plt.ylabel('Edges')
    legend = plt.legend(
        title='(clique_size, num_cycles)',
        loc='upper left',
        bbox_to_anchor=(1.0, 1.0,),
    )
    plt.savefig(
        PLOT,
        dpi=DPI,
        # bbox_extra_artists=(legend,),
        bbox_inches='tight',
    )
    plt.close()

    # Reset random state
    if state is not None:
        random.setstate(state)


def main():
    """Parse arguments and run frustrated loop generator."""
    # Parse arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        '--clique-sizes',
        nargs='+',
        type=int,
        default=DEFAULT_CLIQUE_SIZES,
        help='Size of input cliques. Must be (small, medium, large). '
             'Default = {}'.format(DEFAULT_CLIQUE_SIZES),
    )
    from decimal import Decimal
    parser.add_argument(
        '--num-cycles',
        nargs='+',
        type=float,
        default=DEFAULT_NUM_CYCLES,
        help='Number of cycles in the FCL, expressed as a percentage of n. '
             'Default = {}'.format(DEFAULT_NUM_CYCLES),
    )
    parser.add_argument(
        '--num-fcls',
        type=int,
        default=DEFAULT_NUM_FCLS,
        help='Number of FCLs',
    )
    parser.add_argument(
        '--seed',
        type=int,
        default=DEFAULT_SEED,
        help='Seed for randomness in generating FCLs.'
    )
    argv = parser.parse_args()

    # Generate FCLs
    generate_fcls(
        clique_sizes=argv.clique_sizes,
        num_cycles=argv.num_cycles,
        num_fcls=argv.num_fcls,
        seed=argv.seed,
    )


# Invoke main
if __name__ == '__main__':
    main()
