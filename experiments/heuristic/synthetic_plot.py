import pandas as pd
import math

off_by_one = {}
missing_data = set()


def _cluster_dataset(row):
    dataset = row['Dataset']
    prefix = ""
    suffix = ""
    # Assign prefix
    if 'aa' in dataset:
        prefix = 'aa'
    elif 'j' in dataset:
        prefix = 'j'
    elif 'b-50' in dataset:
        prefix = 'b-50'
    elif 'b-100' in dataset:
        prefix = 'b-100'
    elif 'gka' in dataset:
        prefix = 'gka'
    # Assign suffix
    if '-er' in dataset:
        suffix = '-er'
    elif '-cl' in dataset:
        suffix = '-cl'
    elif '-ba' in dataset:
        suffix = '-ba'
    elif '-to' in dataset:
        suffix = '-to'

    return prefix + suffix


def _write_header(outfile):
    outfile.write('\\begin{tabular}{lc c ccc c ccc c ccc c ccc}\n')
    outfile.write('\\toprule\n')
    outfile.write('\\multicolumn{3}{r}{\\textbf{Timeout:}} &\n')
    outfile.write('\\multicolumn{3}{c}{\\textbf{0.01(s)}} & \\phantom{Q} &\n')
    outfile.write('\\multicolumn{3}{c}{\\textbf{0.1(s)}} & \\phantom{Q} &\n')
    outfile.write('\\multicolumn{3}{c}{\\textbf{1(s)}} & \\phantom{Q} &\n')
    outfile.write('\\multicolumn{3}{c}{\\textbf{10(s)}}\\\\\n')
    outfile.write('\\cmidrule(lr){4-6}\n')
    outfile.write('\\cmidrule(lr){8-10}\n')
    outfile.write('\\cmidrule(lr){12-14}\n')
    outfile.write('\\cmidrule(lr){16-18}\n')
    outfile.write('\\textbf{Dataset} & \\textbf{Represented} &&\n')
    outfile.write('\\textsf{HE} & \\textsf{IC} & \\textsf{ILP} &&\n')
    outfile.write('\\textsf{HE} & \\textsf{IC} & \\textsf{ILP} &&\n')
    outfile.write('\\textsf{HE} & \\textsf{IC} & \\textsf{ILP} &&\n')
    outfile.write('\\textsf{HE} & \\textsf{IC} & \\textsf{ILP}\\\\\n')
    outfile.write('\\midrule\n')


def _highlight_min(ratios):
    # We may already have an exact solution, in which case it wins by default
    if '\\checkmark' in ratios:
        return ratios
    # Else we may assume all are ratios (floats)
    ratios = list(map(float, ratios))
    smallest = min(ratios)
    return ['\\textbf{{{:.2f}}}'.format(x) if x == smallest
            else '{:.2f}'.format(x) for x in ratios]


def _worst_ratio(df, solver, timeout, cluster):
    """
    Given a df, a solver, timeout and cluster, return the number of missing
    exact solutions and the worst approximation ratio.
    """
    ratios = df.loc[(df['Cluster'] == cluster) &
                    (df['Solver'] == solver) &
                    (df['Timeout'] == timeout)]['Approximation']
    ratios = [x for x in ratios if x != float('nan')]
    worst_ratio = max(ratios)
    if worst_ratio == 1:
        worst_ratio = r'\checkmark'
    else:
        worst_ratio = '{:.2f}'.format(worst_ratio)
    return worst_ratio


def _percent_valid(df, solver, timeout, cluster):
    ratios = df.loc[(df['Cluster'] == cluster) &
                    (df['Solver'] == solver) &
                    (df['Timeout'] == timeout)]['Approximation']
    # Count and remove the NaNs
    total = len(ratios)
    ratios = [x for x in ratios if not math.isnan(x)]
    return '{}\\%'.format(100 * len(ratios) // total)


# For the heuristic ensemble, change timeout from ms to s
def _timeout_map(row):
    if row['Solver'] == 'he':
        if row['Timeout'] == 10000:
            return 10.0
        elif row['Timeout'] == 1000:
            return 1.0
        elif row['Timeout'] == 100:
            return 0.1
        elif row['Timeout'] == 10:
            return 0.01
    else:
        return row['Timeout']


def compute_approx(heuristic_filename, exact_filename, output_filename):
    # Read in heuristic data
    heuristics_df = pd.read_csv(heuristic_filename)

    heuristics_df['Timeout'] = heuristics_df.apply(_timeout_map, axis=1)

    # Append a 'approximation' ratio column based on exact results
    exact_df = pd.read_csv(exact_filename)

    def _approximation_map(row):
        """
        Return the approximation ratio for a row
        """
        exact_solutions = set(exact_df.loc[exact_df['Dataset'] ==
                                           row['Dataset']]['Size'])
        if len(exact_solutions) == 0:
            missing_data.add(row['Dataset'])
            return float('nan')
        elif len(exact_solutions) > 1:
            off_by_one[row['Dataset']] = exact_solutions
            return row['Size'] / min(exact_solutions)
            # raise ValueError('More than one exact solution found')
        else:
            opt = list(exact_solutions)[0]
            return row['Size'] / opt

    # Add the approx col
    heuristics_df['Approximation'] = heuristics_df.apply(_approximation_map,
                                                         axis=1)
    # Add the dataset cluster col
    heuristics_df['Cluster'] = heuristics_df.apply(_cluster_dataset, axis=1)

    clusters = ['aa-er', 'aa-to', 'aa-cl', 'aa-ba',
                'j-er', 'j-to', 'j-cl', 'j-ba',
                'b-50-er', 'b-50-to', 'b-50-cl', 'b-50-ba',
                'b-100-er', 'b-100-to', 'b-100-cl', 'b-100-ba',
                'gka-er', 'gka-to', 'gka-cl', 'gka-ba']

    with open(output_filename, 'w') as outfile:
        _write_header(outfile)
        for cluster in clusters:
            formatted_cluster = cluster.replace('aa', 'WH-aa')\
                                       .replace('j', 'WH-j')
            represented = _percent_valid(heuristics_df, 'ic', 0.01, cluster)
            outfile.write('\\texttt{{{}}} & {}'.format(formatted_cluster,
                                                       represented))
            for timeout in [0.01, 0.1, 1, 10]:
                he = _worst_ratio(heuristics_df, 'he', timeout, cluster)
                ic = _worst_ratio(heuristics_df, 'ic', timeout, cluster)
                ilp = _worst_ratio(heuristics_df, 'ilp_1t', timeout, cluster)
                formatted_ratios = _highlight_min([he, ic, ilp])
                outfile.write('&& {} & {} & {}'.format(*formatted_ratios))
            outfile.write('\\\\\n')
        outfile.write('\\bottomrule\n\\end{tabular}')


if __name__ == "__main__":
    print('Computing synthetic heuristic table')
    # Compute table and save as .tex
    compute_approx('results/synthetic_heuristic_results.csv',
                   'results/synthetic_exact_results.csv',
                   'tables/synthetic_heuristic_results.tex')
    # Save some meta data
    with open('results/off_by_one.txt', 'w') as outfile:
        for key in sorted(off_by_one.keys()):
            outfile.write('{} : {}\n'.format(str(key), str(off_by_one[key])))
    with open('results/missing_exact.txt', 'w') as outfile:
        for item in sorted(list(missing_data)):
            outfile.write(str(item) + '\n')
