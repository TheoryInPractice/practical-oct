import subprocess

HUFFNER = ["aa31",  "j19",  "j24",  "j11", "aa10", "aa36",  "j18",  "j17",
           "aa11", "aa54", "aa34", "aa52", "aa22", "aa48", "aa50", "aa19",
           "aa45", "aa29", "aa40", "aa39", "aa17", "aa38", "aa28", "aa42",
           "aa41"]

BEASLEY_GKA = ["bqpgka_{}".format(i) for i in range(1, 46)]
BEASLEY_50 = ["bqp50_{}".format(i) for i in range(1, 11)]
BEASLEY_100 = ["bqp100_{}".format(i) for i in range(1, 11)]
BEASLEY_250 = ["bqp250_{}".format(i) for i in range(1, 11)]


def formatted_header():
    print("{:12s}  {:>8s}  {:>8s}  {:>8s}".format("Dataset",
          "OCT", "Not_OCT", "Rest"))


def formatted_print(stats):
    print("{:12s}  {:>8s}  {:>8s}  {:>8s}".format(*map(str, stats)))


def summarized_reduction(data):
    results = {}
    for dataset in data:
        output = subprocess.run(
            args=['java', '-cp', 'bin', 'Main',
                  '../../../data/preprocessed/snap/{}.snap'.format(dataset),
                  '-r', '3'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True)
        output = output.stdout.decode("utf-8").split("\n")
        oct_set = output[0].split()[1:]
        bipartite_set = output[1].split()[1:]
        rest = output[2].split()[1:]
        # print(oct_set, bipartite_set, rest)
        print("Data: {} OCT: {} Bipartite: {} Rest: {}".format(dataset, len(oct_set), len(bipartite_set), len(rest)))
        # results[dataset] = [int(x.split()[1]) for x in output]

    # print results
    # formatted_header()
    # for dataset in data:
        # formatted_print([dataset] + results[dataset])


if __name__ == "__main__":
    summarized_reduction(HUFFNER)
