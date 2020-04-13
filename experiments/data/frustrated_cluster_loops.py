"""Data generator for frustrated cluster loops.

https://docs.ocean.dwavesys.com/projects/dimod/en/latest/reference/bqm/generated/dimod.generators.fcl.frustrated_loop.html#dimod.generators.fcl.frustrated_loop
"""


# Imports
from functools import partial
from itertools import product
from typing import Iterable, Optional
import argparse
import random

from dimod.generators.fcl import frustrated_loop
from matplotlib import pyplot as plt, rc
import networkx as nx
import seaborn as sns

from experiments import FCL_DATA_DIR, logger
from src.preprocessing import graphs


# FCL Constants
ALL = 'all'
DW_2000Q = 'dw_2000q'
DW_8000Q = 'dw_8000q'
DW_P6 = 'dw_p6'
DW_P12 = 'dw_p12'
LONG_NAMES = {
    DW_2000Q: 'D-Wave 2000Q',
    DW_8000Q: 'D-Wave 8000Q',
    DW_P6: 'D-Wave Pegasus(6)',
    DW_P12: 'D-Wave Pegasus(12)'
}
DW_2000Q_CLIQUE_SIZES = tuple(range(64, 129, 16))
DW_8000Q_CLIQUE_SIZES = tuple(range(128, 257, 16))
DW_P6_CLIQUE_SIZES = tuple(range(62, 105, 7))
DW_P12_CLIQUE_SIZES = tuple(range(134, 249, 19))
DEFAULT_NUM_CYCLES = (0.05, 0.10, 0.15, 0.20, 0.25, 0.3)
DEFAULT_NUM_FCLS = 5


# Seed values
DEFAULT_SEED = 882351143
MIN_SEED = 0
MAX_SEED = 2**32 - 1


# Matplotlib options
DPI = 300
rc('text', usetex=True)


def generate_fcls(dataset_name: str,
                  clique_sizes: Iterable[int] = DW_2000Q_CLIQUE_SIZES,
                  num_cycles: Iterable[float] = DEFAULT_NUM_CYCLES,
                  num_fcls: int = DEFAULT_NUM_FCLS,
                  seed: Optional[int] = DEFAULT_SEED):
    """Generate frustrated cluster loops.

    Parameters
    ----------
    dataset_name : str
        Human readable name for the dataset.
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
    # Log
    logger.info('Generating FCLs for dataset: {}'.format(dataset_name))

    # Compute output directories
    dataset_dir = FCL_DATA_DIR / dataset_name
    edgelist_dir = dataset_dir / 'edgelist'
    huffner_dir = dataset_dir / 'huffner'
    snap_dir = dataset_dir / 'snap'

    # Create output directories
    edgelist_dir.mkdir(exist_ok=True, parents=True)
    huffner_dir.mkdir(exist_ok=True, parents=True)
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
    # Convert num_cycles to a percentage.
    logger.info('Plotting generated FCLs.')
    x, y, hue = zip(*data)
    hue = tuple((clique_size, int(cycles * 100)) for clique_size, cycles in hue)
    sns.scatterplot(x=x, y=y, hue=hue)
    if dataset_name in LONG_NAMES:
        title_dataset_name = LONG_NAMES[dataset_name]
    else:
        title_dataset_name = dataset_name.replace('_', '\\_')
    plt.title('Frustrated Cluster Loops ({})'.format(title_dataset_name))
    plt.xlabel('Nodes')
    plt.ylabel('Edges')
    plt.legend(
        title='(Clique Size, Percent Cycles)',
        loc='center left',
        bbox_to_anchor=(1.0, 0.0, 1.0, 1.0),
        ncol=len(clique_sizes),
    )
    plt.savefig(
        '{}/plot.pdf'.format(str(dataset_dir)),
        dpi=DPI,
        bbox_inches='tight',
    )
    plt.close()

    # Reset random state
    if state is not None:
        random.setstate(state)


# Define dataset specific generators
generate_dw_2000q_fcls = partial(
    generate_fcls,
    dataset_name=DW_2000Q,
    clique_sizes=DW_2000Q_CLIQUE_SIZES,
    num_cycles=DEFAULT_NUM_CYCLES,
    num_fcls=DEFAULT_NUM_FCLS,
    seed=DEFAULT_SEED,
)
generate_dw_8000q_fcls = partial(
    generate_fcls,
    dataset_name=DW_8000Q,
    clique_sizes=DW_8000Q_CLIQUE_SIZES,
    num_cycles=DEFAULT_NUM_CYCLES,
    num_fcls=DEFAULT_NUM_FCLS,
    seed=DEFAULT_SEED,
)
generate_dw_p6_fcls = partial(
    generate_fcls,
    dataset_name=DW_P6,
    clique_sizes=DW_P6_CLIQUE_SIZES,
    num_cycles=DEFAULT_NUM_CYCLES,
    num_fcls=DEFAULT_NUM_FCLS,
    seed=DEFAULT_SEED,
)
generate_dw_p12_fcls = partial(
    generate_fcls,
    dataset_name=DW_P12,
    clique_sizes=DW_P12_CLIQUE_SIZES,
    num_cycles=DEFAULT_NUM_CYCLES,
    num_fcls=DEFAULT_NUM_FCLS,
    seed=DEFAULT_SEED,
)


def main():
    """Parse arguments and run frustrated loop generator."""
    # Create root parser with subcommands
    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(
        dest='subcommand',
        title='Subcommand',
        description='Specific subcommand to run.',
        help='Run one of these to get started.',
    )

    # Configure parser for predefined datasets
    predefined_parser = subparsers.add_parser('predefined')
    predefined_parser.add_argument(
        'dataset',
        nargs='?',
        choices=(ALL, DW_2000Q, DW_8000Q, DW_P6, DW_P12,),
        default=ALL,
        help='Predefined datasets to generate.',
    )

    # Configure parser for custom datasets
    custom_parser = subparsers.add_parser('custom')
    custom_parser.add_argument(
        '--dataset-name',
        type=str,
        default='default',
        help='Name for the dataset.',
    )
    custom_parser.add_argument(
        '--clique-sizes',
        nargs='+',
        type=int,
        default=DW_2000Q_CLIQUE_SIZES,
        help='Size of input cliques. Must be (small, medium, large). '
             'Default = {}'.format(DW_2000Q_CLIQUE_SIZES),
    )
    custom_parser.add_argument(
        '--num-cycles',
        nargs='+',
        type=float,
        default=DEFAULT_NUM_CYCLES,
        help='Number of cycles in the FCL, expressed as a percentage of n. '
             'Default = {}'.format(DEFAULT_NUM_CYCLES),
    )
    custom_parser.add_argument(
        '--num-fcls',
        type=int,
        default=DEFAULT_NUM_FCLS,
        help='Number of FCLs',
    )
    custom_parser.add_argument(
        '--seed',
        type=int,
        default=DEFAULT_SEED,
        help='Seed for randomness in generating FCLs.'
    )

    # Parse arguments
    argv = parser.parse_args()

    # Print help if subcommand is not specified
    if not argv.subcommand:
        parser.print_help()
        exit(1)

    # Generate FCLs
    if argv.subcommand == 'predefined':
        if argv.dataset in (ALL, DW_2000Q):
            generate_dw_2000q_fcls()
        if argv.dataset in (ALL, DW_8000Q):
            generate_dw_8000q_fcls()
        if argv.dataset in (ALL, DW_P6):
            generate_dw_p6_fcls()
        if argv.dataset in (ALL, DW_P12):
            generate_dw_p12_fcls()

    if argv.subcommand == 'custom':
        generate_fcls(
            dataset_name=argv.dataset_name,
            clique_sizes=argv.clique_sizes,
            num_cycles=argv.num_cycles,
            num_fcls=argv.num_fcls,
            seed=argv.seed,
        )


# Invoke main
if __name__ == '__main__':
    main()
