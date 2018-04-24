from pathlib import Path
import logging
import matplotlib
import pandas
import re


# Configure matplotlib
matplotlib.use('agg')


# Construct logger
logging.basicConfig(format='%(asctime)-15s %(message)s')
logger = logging.getLogger('tuning_oct')
logger.setLevel(logging.INFO)


# Experiment constants
PREPROCESSING_TIMEOUTS = [0.01, 0.1, 1, 10]
PREPROCESSING_TIMEOUTS_MILLISECONDS = ['10', '100', '1000', '10000']
EXACT_TIMEOUT = 600


# Shared print context for pandas
PRINT_CONTEXT = pandas.option_context(
    'display.max_rows', None,
    'display.max_columns', None,
    'display.max_colwidth', 70,
    'expand_frame_repr', False,
    'justify', 'right'
)


# File system paths
PROJECT_ROOT = Path(__file__).parent.parent
EXPERIMENTS_DIR = PROJECT_ROOT / 'experiments'
RESULTS_DIR = EXPERIMENTS_DIR / 'paper_results'
PLOTS_DIR = PROJECT_ROOT / 'paper/figures'
TABLES_DIR = PROJECT_ROOT / 'paper/tables'
ORIGINAL_DATA_DIR = PROJECT_ROOT / 'data/original'
PREPROCESSED_DATA_DIR = PROJECT_ROOT / 'data/preprocessed'
HUFFNER_DATA_DIR = PREPROCESSED_DATA_DIR / 'huffner'
HUFFNER_DATA_EXT = '.huffner'
ORIGINAL_HUFFNER_DATA_EXT = '.graph'
SNAP_DATA_DIR = PREPROCESSED_DATA_DIR / 'snap'
SNAP_DATA_EXT = '.snap'
EDGELIST_DATA_DIR = PREPROCESSED_DATA_DIR / 'edgelist'
EDGELIST_DATA_EXT = '.edgelist'
BEASLEY_EXT = '.txt'
PLOTS_DIR.mkdir(exist_ok=True, parents=True)
TABLES_DIR.mkdir(exist_ok=True, parents=True)
HUFFNER_DATA_DIR.mkdir(exist_ok=True, parents=True)


# Helper functions
def normalize_dataset_name(name):
    m = re.match(r'([a-zA-Z]+)_?([0-9]+)(?:_([0-9]+))?', name)
    return '{}-{}-{}'.format(
        m.group(1).replace('bqp', 'b'),
        m.group(2),
        m.group(3) or ''
    ).strip('-')
