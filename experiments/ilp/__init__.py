"""ILP Experiment Module."""


from experiments import RESULTS_DIR


ILP_RESULTS_FILE_PATH = RESULTS_DIR / 'ilp_experiment_results.csv'


SOLVERS = [('CPLEX', 1), ('CPLEX', 4), ('GLPK', 1)]  # (solver, threads)
EXPERIMENT_MEMORY_LIMITS = [4, 16384]                # 4MB, 16GB
