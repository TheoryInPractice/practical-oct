"""Generate plots associated with the iterative compression experiment."""


# Imports
from experiments import (
    headers,
    logger,
    PRINT_CONTEXT,
    PREPROCESSING_TIMEOUTS
)
from experiments.ic import (
    SELF_COMPARISON_DATA_PATH,
    IC_TABLE_FORMAT_STR,
    IC_TABLES_DIR
)
import pandas


# Constants
HEADERS = [
    headers.DATASET,
    headers.PREPROCESSING,
    headers.SIZE
]
GROUPBY = [
    headers.DATASET,
    headers.PREPROCESSING
]


def main():
    """Load and plot."""

    # Load data
    if not SELF_COMPARISON_DATA_PATH.exists():
        logger.error(
            'Self comparison data not found at: {}'
            .format(SELF_COMPARISON_DATA_PATH)
        )
        return
    data = pandas.read_csv(str(SELF_COMPARISON_DATA_PATH))

    # Generate table for each timeout
    for timeout in PREPROCESSING_TIMEOUTS:

        # Subset to data by timeout and grab desired columns
        subset = data[data[headers.TIMEOUT] == timeout][HEADERS]

        # Group and compute statistics
        describe = subset.groupby(GROUPBY).describe().round(decimals=1)

        # Format columns
        describe = describe.drop(columns=[(headers.SIZE, 'count')])
        int_headers = [(headers.SIZE, h) for h in [
            'min', '25%', '50%', '75%', 'max'
        ]]
        describe[int_headers] = describe[int_headers].astype('int')

        # Generate latex
        describe.to_latex(
            str(IC_TABLES_DIR / IC_TABLE_FORMAT_STR.format(timeout))
        )

        # Print
        with PRINT_CONTEXT:
            logger.info('Timeout == {}'.format(timeout))
            logger.info(str(describe) + '\n')


if __name__ == '__main__':
    main()
