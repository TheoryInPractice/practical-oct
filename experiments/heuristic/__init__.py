"""Heuristic Experiment Module."""

from experiments import headers, RESULTS_DIR

GROUND_TRUTH_DATA_FILE = RESULTS_DIR / 'ground_truth.csv'
COMBINED_RESULTS_DATA_FILE = (
    RESULTS_DIR / 'combined_heuristics_experiment_results.csv'
)
CPLEX_RESULTS_DATA_FILE = RESULTS_DIR / 'cplex_experiment_results.csv'
HEURISTICS_RESULTS_DATA_FILE = (
    RESULTS_DIR / 'heuristics_experiment_results.csv'
)
HUFFNER_RESULTS_DATA_FILE = RESULTS_DIR / 'huffner_heuristics.csv'
HUFFNER_P1 = 'IC_1'
HUFFNER_P2 = 'IC_2'
LT_HUFFNER_P1 = r'$\textsf{IC}^+_{1}$'
LT_HUFFNER_P2 = r'$\textsf{IC}^+_{2}$'
CPLEX_SOLVER = 'ILP'
HEURISTICS_SOLVER = 'HE'
HEURISTICS_CSV_HEADERS = [
    headers.DATASET, headers.TIMEOUT, headers.SIZE,
    headers.TIME, headers.CERTIFICATE
]
HUFFNER_CSV_HEADERS = [
    headers.DATASET, headers.SOLVER, headers.TIMEOUT,
    headers.TIME, headers.SIZE, headers.CERTIFICATE
]
