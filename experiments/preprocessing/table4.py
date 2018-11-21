def compute_opt(exact_filename, preprocessing_filename):
    datasets = set() # Dataset names

    exact_solution_lookup = {} # Maps dataset names to OPT
    with open(exact_filename, 'r') as infile:
        # Discard header
        infile.readline()
        for line in infile.readlines():
            line = line.split(',')
            if line[1] == 'ilp':
                datasets.add(line[0])
                exact_solution_lookup[line[0]] = int(line[3])

    oct_removed_lookup = {} # Maps dataset names to V_o
    with open(preprocessing_filename, 'r') as infile:
        # Discard header
        infile.readline()
        for line in infile.readlines():
            line = line.split(',')
            oct_removed_lookup[line[0]] = int(line[5])

    before_oct_lookup = {} # Maps dataset names to OCT on raw data
    for dataset in datasets:
        before_oct_lookup[dataset] = exact_solution_lookup[dataset] +\
                                     oct_removed_lookup[dataset]

    clusters = ['aa-er', 'aa-cl', 'aa-ba', 'aa-to',
                'j-er', 'j-cl', 'j-ba', 'j-to',
                'b-50-er', 'b-50-cl', 'b-50-ba', 'b-50-to',
                'b-100-er', 'b-100-cl', 'b-100-ba', 'b-100-to',
                'gka-er', 'gka-cl', 'gka-ba', 'gka-to']

    oct_before = {} # clustered by dataset
    oct_after = {}

    print(before_oct_lookup)

    for cluster in clusters:
        oct_before[cluster] = []
        oct_after[cluster] = []
    for dataset in datasets:
        if 'aa' in dataset:
            if '-er' in dataset:
                oct_before['aa-er'].append(before_oct_lookup[dataset])
                oct_after['aa-er'].append(exact_solution_lookup[dataset])
            elif '-cl' in dataset:
                oct_before['aa-cl'].append(before_oct_lookup[dataset])
                oct_after['aa-cl'].append(exact_solution_lookup[dataset])
            elif '-ba' in dataset:
                oct_before['aa-ba'].append(before_oct_lookup[dataset])
                oct_after['aa-ba'].append(exact_solution_lookup[dataset])
            elif '-to' in dataset:
                oct_before['aa-to'].append(before_oct_lookup[dataset])
                oct_after['aa-to'].append(exact_solution_lookup[dataset])
        elif 'j' in dataset:
            if '-er' in dataset:
                oct_before['j-er'].append(before_oct_lookup[dataset])
                oct_after['j-er'].append(exact_solution_lookup[dataset])
            elif '-cl' in dataset:
                oct_before['j-cl'].append(before_oct_lookup[dataset])
                oct_after['j-cl'].append(exact_solution_lookup[dataset])
            elif '-ba' in dataset:
                oct_before['j-ba'].append(before_oct_lookup[dataset])
                oct_after['j-ba'].append(exact_solution_lookup[dataset])
            elif '-to' in dataset:
                oct_before['j-to'].append(before_oct_lookup[dataset])
                oct_after['j-to'].append(exact_solution_lookup[dataset])
        elif 'b-50' in dataset:
            if '-er' in dataset:
                oct_before['b-50-er'].append(before_oct_lookup[dataset])
                oct_after['b-50-er'].append(exact_solution_lookup[dataset])
            elif '-cl' in dataset:
                oct_before['b-50-cl'].append(before_oct_lookup[dataset])
                oct_after['b-50-cl'].append(exact_solution_lookup[dataset])
            elif '-ba' in dataset:
                oct_before['b-50-ba'].append(before_oct_lookup[dataset])
                oct_after['b-50-ba'].append(exact_solution_lookup[dataset])
            elif '-to' in dataset:
                oct_before['b-50-to'].append(before_oct_lookup[dataset])
                oct_after['b-50-to'].append(exact_solution_lookup[dataset])
        elif 'b-100' in dataset:
            if '-er' in dataset:
                oct_before['b-100-er'].append(before_oct_lookup[dataset])
                oct_after['b-100-er'].append(exact_solution_lookup[dataset])
            elif '-cl' in dataset:
                oct_before['b-100-cl'].append(before_oct_lookup[dataset])
                oct_after['b-100-cl'].append(exact_solution_lookup[dataset])
            elif '-ba' in dataset:
                oct_before['b-100-ba'].append(before_oct_lookup[dataset])
                oct_after['b-100-ba'].append(exact_solution_lookup[dataset])
            elif '-to' in dataset:
                oct_before['b-100-to'].append(before_oct_lookup[dataset])
                oct_after['b-100-to'].append(exact_solution_lookup[dataset])
        elif 'gka' in dataset:
            if '-er' in dataset:
                oct_before['gka-er'].append(before_oct_lookup[dataset])
                oct_after['gka-er'].append(exact_solution_lookup[dataset])
            elif '-cl' in dataset:
                oct_before['gka-cl'].append(before_oct_lookup[dataset])
                oct_after['gka-cl'].append(exact_solution_lookup[dataset])
            elif '-ba' in dataset:
                oct_before['gka-ba'].append(before_oct_lookup[dataset])
                oct_after['gka-ba'].append(exact_solution_lookup[dataset])
            elif '-to' in dataset:
                oct_before['gka-to'].append(before_oct_lookup[dataset])
                oct_after['gka-to'].append(exact_solution_lookup[dataset])

    print(oct_after)

    for cluster in clusters:
        try:
            print('{} before'.format(cluster),
                min(oct_before[cluster]),
                max(oct_before[cluster]))
            print('{} after:'.format(cluster),
                min(oct_after[cluster]),
                max(oct_after[cluster]))
        except:
            pass


if __name__ == "__main__":
    compute_opt('results/exact_results.csv', 'results/final_preprocessing.csv')
