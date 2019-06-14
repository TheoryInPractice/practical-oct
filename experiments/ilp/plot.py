import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import warnings
warnings.filterwarnings("ignore")


def _load_raw_data(filename):
    dataframe = pd.read_csv(filename, header=0)
    return dataframe


def _refine_data(dataframe):
    # Rename solvers
    solver_name_map = {'ilp_oct_1t': 'OCT-1T',
                       'ilp_vc_1t': 'VC-1T',
                       'ilp_oct_4t': 'OCT-4T',
                       'ilp_vc_4t': 'VC-4T'}
    dataframe['Solver'] = dataframe['Solver'].map(solver_name_map)

    # Compute dataset order so they're in the run time order of VC 1t
    # First get order of dataset names when sorting by VC 1t run time
    baseline_df = dataframe.loc[
        dataframe['Solver'] == 'VC-1T']
    baseline_df.sort_values(by=['Time'], inplace=True)
    dataset_order = list(baseline_df['Dataset'])

    # If a dataset is missing for a solver, add a row with a -1 size and the
    # timeout time
    for dataset in dataset_order:
        for solver in ['VC-1T', 'VC-4T', 'OCT-1T', 'OCT-4T']:
            if not ((dataframe['Solver'] == solver) &
                    (dataframe['Dataset'] == dataset)).any():
                new_row = {'Dataset': dataset,
                           'Solver': solver,
                           'Time': -1,
                           'Size': -1,
                           'Certificate': ""}
                dataframe = dataframe.append(new_row, ignore_index=True)

    # Change the run time so that it's relative to VC 1t
    def compute_relative_run_time(row):
        baseline = dataframe.loc[
            (dataframe['Dataset'] == row['Dataset']) &
            (dataframe['Solver'] == 'VC-1T')]
        baseline_time = float(baseline['Time'])
        row_time = float(row['Time'])

        # Handle some exception cases
        if row_time == -1:
            result = 100000
        elif baseline_time == 0:
            if row_time == 0:
                result = 1
            else:
                result = 100000
        else:
            result = row_time / baseline_time
        return result

    dataframe['Relative Run Time'] = dataframe.apply(compute_relative_run_time,
                                                     axis=1)

    # Add 0.001 to zero run times so points display properly.
    def buffer_zero_run_time(row):
        if row['Time'] == 0:
            return 0.001
        else:
            return row['Time']
    dataframe['Time'] = dataframe.apply(buffer_zero_run_time, axis=1)

    # Add runtime categories
    def regime_map(row):
        cache = row['Relative Run Time']
        if cache == 1:
            return 'Identical'
        elif cache == 100000:
            return 'Timed Out'
        elif cache > 1:
            return 'Slower'
        else:
            return 'Faster'
    dataframe['Regime'] = dataframe.apply(regime_map, axis=1)

    # Order the rows by the dataset order
    dataframe['Dataset'] = pd.Categorical(dataframe['Dataset'], dataset_order)
    dataframe.sort_values(by='Dataset', inplace=True)

    # Add a dataset number
    dataset_ids = {}
    for counter, dataset in enumerate(dataset_order):
        dataset_ids[dataset] = counter + 1
    dataframe['Dataset ID'] = dataframe['Dataset'].map(dataset_ids)

    return dataframe


def _plot_oct(dataframe, output_filename):
    sns.set_style("darkgrid")

    # Use latex text
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    # Define color palette
    colors = ["dusty purple", "windows blue", "amber", "faded green"]
    palette = sns.xkcd_palette(colors)

    # Make plot
    solver_order = ['OCT-1T', 'OCT-4T']

    g = sns.FacetGrid(data=dataframe,
                      col="Solver",
                      col_order=solver_order,
                      col_wrap=2,
                      hue='Regime',
                      hue_order=['Timed Out', 'Identical', 'Slower'],
                      height=2.3,
                      aspect=1.7,
                      palette=palette)
    g = (g.map(sns.scatterplot, "Dataset ID", "Relative Run Time")
         .add_legend())

    g.set(yscale='log')
    plt.ylim(0.5, 200000)

    # Update titles
    titles = ['OCT-1T', 'OCT-4T']
    for axis in g.fig.axes:
        axis.set_title(titles.pop(0))

    # Facet titles
    g.set_ylabels(r'\textbf{Run Time Ratio}')
    g.set_xlabels(r'\textbf{Dataset ID (Sorted by VC-1T)}')

    # Save plot
    g.savefig(output_filename)


def _plot_vc(dataframe, output_filename):
    sns.set_style("darkgrid")

    # Use latex text
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    # Define color palette
    colors = ["windows blue", "amber", "faded green"]
    palette = sns.xkcd_palette(colors)

    # Make plot
    solver_order = ['VC-4T']

    g = sns.FacetGrid(data=dataframe,
                      col="Solver",
                      col_order=solver_order,
                      hue='Regime',
                      hue_order=['Identical', 'Slower', 'Faster'],
                      height=2.3,
                      aspect=1.7,
                      palette=palette)
    g = (g.map(sns.scatterplot, "Dataset ID", "Relative Run Time")
         .add_legend())

    g.set(yscale='log')
    plt.ylim(0.01, 10)

    # Update titles
    titles = ['VC-4T']
    for axis in g.fig.axes:
        axis.set_title(titles.pop(0))

    # Facet titles
    g.set_ylabels(r'\textbf{Run Time Ratio}')
    g.set_xlabels(r'\textbf{Dataset ID (Sorted by VC-1T)}')

    # Save plot
    g.savefig(output_filename)


def _plot_vc_runtime(dataframe, output_filename):
    sns.set_style("darkgrid")

    # Use latex text
    plt.rc('text', usetex=True)
    plt.rc('font', family='serif')

    # Define color palette
    colors = ["windows blue"]
    palette = sns.xkcd_palette(colors)

    # Make plot
    solver_order = ['VC-1T']

    g = sns.FacetGrid(data=dataframe,
                      col="Solver",
                      col_order=solver_order,
                      height=2.3,
                      aspect=1.7,
                      palette=palette)
    g = (g.map(sns.scatterplot, "Dataset ID", "Time").add_legend())

    g.set(yscale='log')
    plt.ylim(0.0005, 10000)

    # Update titles
    titles = ['VC-1T']
    for axis in g.fig.axes:
        axis.set_title(titles.pop(0))

    # Facet titles
    g.set_ylabels(r'\textbf{Run Time (sec)}')
    g.set_xlabels(r'\textbf{Dataset ID (Sorted by VC-1T)}')

    # Save plot
    g.savefig(output_filename)


if __name__ == '__main__':
    df = _load_raw_data('results/cplex_results.csv')
    print("Loaded results/cplex_results.csv")

    df = _refine_data(df)
    print("Refined dataframe")

    _plot_oct(df, 'figures/cplex_plot_oct.pdf')
    print("Generated figures/cplex_plot_oct.pdf")

    _plot_vc(df, 'figures/cplex_plot_vc.pdf')
    print("Generated figures/cplex_plot_vc.pdf")

    _plot_vc_runtime(df, 'figures/cplex_plot_vc_runtime.pdf')
    print("Generated figures/cplex_plot_vc_runtime.pdf")
