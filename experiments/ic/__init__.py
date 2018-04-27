"""Iterative Compression Module."""

from experiments import RESULTS_DIR, TABLES_DIR
from pathlib import Path


# Paths
IC_DIR = Path(__file__).parent
SELF_COMPARISON_DATA_PATH = RESULTS_DIR / 'ic_preprocessing_level.csv'
IC_TABLE_FORMAT_STR = 'timeout_{}.tex'
IC_TABLES_DIR = TABLES_DIR / 'ic'
IC_TABLES_DIR.mkdir(exist_ok=True)
BASELINE_FILE = str(RESULTS_DIR / 'ic_baseline_experiment_results.csv')


# Constants
PREPROCESSING_LEVELS = [0, 1, 2]
