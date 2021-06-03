from datetime import datetime
from pathlib import Path

import pandas as pd

# collects signal data for performance tests
results = {}


def add_result(url: str, field: str, value: float):
    """TODO documentation"""

    results[url][field] = value


def results_to_csv():
    """TODO documentation"""

    if results:
        csvpath = (Path(__file__).parent /
                   ("testing/test_results_" + datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss") + ".csv")).resolve()
        df = pd.DataFrame.from_dict(results, orient="index")  # TODO check output formatting
        df.to_csv(path_or_buf=csvpath, sep=";")
