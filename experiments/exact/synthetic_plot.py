from matplotlib.patches import Patch
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt


ALPHA = .8


def _get_dataset(name):
    if 'aa' in name:
        return 'aa'
    elif 'j' in name:
        return 'j'
    elif 'b-50' in name:
        return 'b-50'
    elif 'b-100' in name:
        return 'b-100'
    elif 'gka' in name:
        return 'gka'


def _get_generator(name):
    if '-er' in name:
        return 'ER'
    elif '-cl' in name:
        return 'CL'
    elif '-ba' in name:
        return 'BA'
    elif '-to' in name:
        return 'TO'


def construct_df(exact_filename, solver1_name, solver2_name, yaxis_title):
    rows = []
    solver1 = {}
    solver2 = {}
    opt = {}
    datasets = set()

    with open(exact_filename, 'r') as infile:
        # Discard header
        infile.readline()
        for line in infile.readlines():
            line = line.split(',')
            datasets.add(line[0])
            solver = line[1]
            if solver == solver1_name:
                solver1[line[0]] = float(line[2])
                opt[line[0]] = float(line[3])
            elif solver == solver2_name:
                solver2[line[0]] = float(line[2])

    print(len(solver1), len(solver2), len(opt), len(datasets))
    for dataset in datasets:
        if dataset in solver1 and dataset in solver2 and dataset in opt:
            row = [dataset,
                   max(solver1[dataset], 0.01),
                   solver2[dataset],
                   opt[dataset],
                   _get_dataset(dataset),
                   _get_generator(dataset)]
            rows.append(row)
    df = pd.DataFrame(rows, columns=['name',
                                     solver1_name,
                                     solver2_name,
                                     "$OPT'$",
                                     'Dataset',
                                     'Generator'])

    df[yaxis_title] = df[solver1_name] / df[solver2_name]
    return df


def _plot_vc_vs_ilp1t(exact_data_filename, output_filename, palette):
    df = construct_df(exact_data_filename,
                      'vc',
                      'ilp_1t',
                      'Relative Run Time ($VC$ / $ILP$)')

    # Prepare a new plot
    sns.set(font_scale=1.7)
    plt.clf()

    # Compute the scatterplot
    dataset_order = ['aa', 'j', 'b-50', 'b-100', 'gka']
    generator_order = ['ER', 'TO', 'CL', 'BA']
    ax = sns.relplot(
        data=df,
        x="$OPT'$",
        y='Relative Run Time ($VC$ / $ILP$)',
        col='Dataset',
        col_wrap=3,
        col_order=dataset_order,
        hue='Generator',
        hue_order=generator_order,
        s=60,
        palette=palette,
        alpha=ALPHA,
        linewidth=0,
        legend=False,  # We generate the legend manually
    )

    # Add legend
    legend_colors = zip(generator_order, palette)
    ax.add_legend(
        title='Generator',
        legend_data={
            name: Patch(color=color)
            for name, color in legend_colors
        },
        label_order=generator_order,
        bbox_to_anchor=(
            0.833,  # Halfway through the third column (5/6)
            0.75,   # Halfway through the top row (3/4)
            0,
            0
        ),
    )

    # Adjust as needed
    ax.set(yscale="log", ylim=(0.01, 1000), xlim=(-3, 100))

    for axis in ax.fig.axes:
        axis.set_title(dataset_order.pop())
        axis.axhline(y=1, color='black', dashes=[3, 3])

    # Give the lonely plot some friends (move to bottom row next to last plot).
    lone_plot = ax.fig.axes[2]
    pos = lone_plot.get_position()
    lone_plot.set_position([
        pos.x0,
        ax.fig.axes[4].get_position().y0,
        pos.width,
        pos.height
    ])

    # Save to file
    ax.savefig(output_filename)


def _plot_ilp1t_vs_ilp(exact_data_filename, output_filename, palette):
    df = construct_df(exact_data_filename,
                      'ilp_1t',
                      'ilp',
                      '$ILP$ Relative Run Time (1t / 4t)')

    # Prepare a new plot
    sns.set(font_scale=1.7)
    plt.clf()

    # Compute the scatterplot
    dataset_order = ['aa', 'j', 'b-50', 'b-100', 'gka']
    generator_order = ['ER', 'TO', 'CL', 'BA']
    ax = sns.relplot(
        data=df,
        x="$OPT'$",
        y='$ILP$ Relative Run Time (1t / 4t)',
        col='Dataset',
        col_wrap=3,
        col_order=dataset_order,
        hue='Generator',
        hue_order=generator_order,
        s=60,
        palette=palette,
        alpha=ALPHA,
        linewidth=0,
        legend=False,
    )

    # Add legend
    legend_colors = zip(generator_order, palette)
    ax.add_legend(
        title='Generator',
        legend_data={
            name: Patch(color=color)
            for name, color in legend_colors
        },
        label_order=generator_order,
        bbox_to_anchor=(
            0.833,  # Halfway through the third column (5/6)
            0.75,   # Halfway through the top row (1/4)
            0,
            0
        ),
    )

    # Adjust as needed
    ax.set(yscale="log", ylim=(0.05, 20), xlim=(-3, 100))
    for axis in ax.fig.get_axes():
        axis.set_title(dataset_order.pop())
        axis.axhline(y=1, color='black', dashes=[3, 3])
        axis.axhline(y=0.1, color='red', dashes=[2, 2])
        axis.axhline(y=4, color='blue', dashes=[5, 5])

    # Give the lonely plot some friends (move to bottom row next to last plot).
    lone_plot = ax.fig.axes[2]
    pos = lone_plot.get_position()
    lone_plot.set_position([
        pos.x0,
        ax.fig.axes[4].get_position().y0,
        pos.width,
        pos.height
    ])

    # Save to file
    ax.savefig(output_filename)


if __name__ == "__main__":
    # blue, orange, green, red, purple, brown, pink, gray, yellow, teal =\
    #     sns.color_palette('bright')
    # first_palette = [teal, orange, green, red, purple]
    # second_palette = [blue, yellow, gray, pink]
    # colors = [teal, yellow, red, purple]

    colors = ["dusty purple", "windows blue", "amber", "faded green"]
    palette = sns.xkcd_palette(colors)
    _plot_vc_vs_ilp1t('results/exact_results.csv',
                      'tables/figure2.pdf',
                      palette)
    _plot_ilp1t_vs_ilp('results/exact_results.csv',
                       'tables/figure3.pdf',
                       palette)
