"""ILP Experiment Plot Script."""

from experiments import (
    headers,
    logger,
    PLOTS_DIR,
    TABLES_DIR
)
from experiments.ilp import (
    ILP_RESULTS_FILE_PATH
)
from itertools import chain, zip_longest
from matplotlib import pyplot as plt, rc
import math
import pandas
import re
import seaborn as sns


# Configure matplotlib
rc('text', usetex=True)


# Constants
DATASET_ORDER = [
    'gka-1', 'aa-43', 'aa-45', 'gka-2',
    'aa-29', 'aa-42', 'aa-32', 'gka-3',
    'aa-41', 'gka-26', 'gka-24',  'gka-25',
    'gka-29', 'gka-27', 'gka-28'
]
LATEX_SOLVER_TEMPLATE = (
    r'$\textsf{{{}}}_\textsc{{\tiny {}}}^\textsc{{\tiny {}}}$'
)
HUE_ORDER = [
    LATEX_SOLVER_TEMPLATE.format('CPLEX', 1, 'OCT'),
    LATEX_SOLVER_TEMPLATE.format('CPLEX', 4, 'OCT'),
    LATEX_SOLVER_TEMPLATE.format('CPLEX', 1, 'VC'),
    LATEX_SOLVER_TEMPLATE.format('CPLEX', 4, 'VC')
]
HUE_KWS = {
    'color': ['limegreen', 'green', 'lightskyblue', 'blue']
}
TABLE_SOLVER_ORDER = [
    'C(4, vc)',
    'C(1, vc)',
    'G(1, vc)',
]
TABLE_HEADERS = [
    headers.DATASET, headers.VERTICES, headers.EDGES,
    headers.OPT, headers.TIME
]


def _plot_results(memory, filename):
    """Generate ILP experiment result plots."""

    # Log
    logger.info('Plotting results figure: {}'.format(filename))

    # Load dataset
    data = pandas.read_csv(ILP_RESULTS_FILE_PATH)

    # Raname datasets
    data[headers.DATASET] = data[headers.DATASET].map(
        lambda v: re.sub(
            r'([a-zA-Z]+)(_?)([0-9]+)',
            lambda m: m.group(1) + '-' + m.group(3),
            v
        )
    )

    # Create order index
    data['order'] = data.apply(
        lambda r: DATASET_ORDER.index(r.Dataset),
        axis=1
    )
    data = data.sort_values('order')

    # Create solver_group column
    data['solver_group'] = data.apply(
        lambda r: LATEX_SOLVER_TEMPLATE.format(
            r.Solver.upper(),
            r.Threads,
            r.Formulation.upper()
        ),
        axis=1
    )

    # Set common facet
    data['facet'] = 'common'

    # Subset to those with the desired memory
    data = data[data['Memory'] == memory]

    # Subset to those that didn't time out
    data = data[data['Time'] < 600]

    # Rename time
    data = data.rename(columns={'Time': 'Time (s)'})

    # Draw
    grid = sns.FacetGrid(
        data,
        col='facet',
        hue='solver_group',
        hue_order=HUE_ORDER,
        hue_kws=HUE_KWS
    ).map(
        plt.plot,
        'order',
        'Time (s)',
        marker='o'
    ).add_legend(
        title='',
        bbox_to_anchor=(1.4, 0.5, 0, 0)
    )

    # Set X axis labels and rotate
    # Reduce dataset names
    plt.xticks(
        range(len(DATASET_ORDER)),
        map(lambda d: d.replace('bqp', ''), DATASET_ORDER)
    )
    for ax in grid.axes.flatten():
        ax.set_xlabel('Dataset')
        for tick in ax.get_xticklabels():
            tick.set(rotation=90)

    # Set tight layout. This prevents labels from overlapping.
    grid.fig.tight_layout()

    # Set title
    if memory < 1024:
        unit = 'MB'
    else:
        memory = int(memory / 1024)
        unit = 'GB'
    plt.title('CPLEX Solution Times ({} {})'.format(memory, unit))

    # Save. bbox_inches=tight forces inclusion of legend
    # by bounding box for figure, so it is not cut off.
    grid.fig.savefig(
        str(PLOTS_DIR / filename),
        bbox_inches='tight'
    )
    plt.close()


def _generate_results_table(memory, filename):
    """Generate latex results table."""

    # Log
    logger.info('Generating results table: {}'.format(filename))

    # Load data file
    data = pandas.read_csv(ILP_RESULTS_FILE_PATH)

    # Filter to only the memory value we want
    data = data.loc[data['Memory'] == memory]

    # Subset to those that didn't time out
    data = data[data['Time'] < 600]

    # Create solver_group column
    data['solver_group'] = data.apply(
        lambda r: '{}({}, {})'.format(
            r.Solver[0],
            r.Threads,
            r.Formulation.lower()
        ),
        axis=1
    )

    # Drop unused columns
    data = data.drop(
        ['Solver', 'Threads', 'Formulation', 'Certificate', 'Memory'],
        axis=1
    )

    # Set index, pivot, unset index, then rename columns
    data = data.set_index(['Dataset', 'Vertices', 'Edges', 'Opt'])
    data = data.pivot(columns='solver_group')
    data = data.reset_index()
    data.columns = [c[1] or c[0] for c in data.columns.values]

    # Add any columns that don't exist
    # This happens if there is no data for some solver (*GLPK*)
    for solver in TABLE_SOLVER_ORDER:
        if solver not in data:
            data[solver] = math.nan

    # Group by dataset and aggregate
    data = data.groupby(['Dataset'], as_index=False).agg({
        'Vertices': 'max',
        'Edges': 'max',
        'Opt': 'min',
        **{
            solver: lambda l: next(chain(
                (x for x in l if not math.isnan(x)),
                [math.nan]
            ))
            for solver in TABLE_SOLVER_ORDER
        }
    })

    # Add CPLEX ground truth
    data['Time'] = data['C(4, vc)']

    def _map_to_relative_time(s):
        """Function for mapping a (Time, Solver) tuple to a relative time."""

        if s[0] == 0:
            if s[1] == 0:
                s[1] = 1
            else:
                s[1] = math.inf
        else:
            s[1] = s[1] / s[0]
        return s

    # Compute the appropriate relative time for each solver
    for cols in map(list, zip_longest([], TABLE_SOLVER_ORDER, fillvalue='Time')):
        data[cols] = data[cols].apply(_map_to_relative_time, axis=1)

    def _rel_time_to_latex(e):
        """Function for formatting a relative time in latex."""

        if math.isnan(e):
            return '-'
        elif math.isinf(e):
            return '${}\\times$'.format(e)
        return '${}\\times$'.format(round(e, 1))

    # Converet relative times to latex formatting
    data[TABLE_SOLVER_ORDER] = data[TABLE_SOLVER_ORDER].apply(
        lambda s: s.map(_rel_time_to_latex)
    )

    # Reindex for ordered columns
    data = data.reindex(
        ['Dataset', 'Vertices', 'Edges', 'Opt', 'Time', *TABLE_SOLVER_ORDER],
        axis=1
    )

    # Raname datasets
    data[headers.DATASET] = data[headers.DATASET].map(
        lambda v: re.sub(
            r'([a-zA-Z]+)(_?)([0-9]+)',
            lambda m: m.group(1) + '-' + m.group(3),
            v
        )
    )

    # Create order index, sort, and drop
    data['order'] = data.apply(
        lambda r: DATASET_ORDER.index(r.Dataset),
        axis=1
    )
    data = data.sort_values('order').drop(columns='order')

    # Rename
    data = data.rename(columns={
        'Vertices': '|V|',
        'Edges': '|E|'
    })

    # Print latex table
    data.to_latex(
        str(TABLES_DIR / filename),
        escape=False,
        index=False,
        column_format=''.join(['l'] + ['r'] * (len(data.columns.values) - 1))
    )


def main():
    """Run plots."""

    outputs = [
        (4, 'ilp_experiment_4mb.pdf', 'ilp_table_4mb.tex'),
        (16384, 'ilp_experiment.pdf', 'ilp_table.tex')
    ]
    for memory, fig, table in outputs:
        _plot_results(memory, fig)
        _generate_results_table(memory, table)


if __name__ == '__main__':
    main()
