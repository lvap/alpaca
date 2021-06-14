import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

# toggle program performance test run (collect signal stats for all processed webpages and export to file)
TEST_ENABLED = False

# collects signal statistics from evaluation runs
results = defaultdict(lambda: defaultdict(float))


def add_result(url: str, field: str, value: float):
    """Add data value regarding a webpage to the module. Collected data can later be exported as csv file.

    :param url: Url of the webpage the data belongs to.
    :param field: Name/class of the data point to be added (later column header in table).
    :param value: Value of the data point to be added.
    """

    if TEST_ENABLED:
        results[url][field] = value


def results_to_csv():
    """Exports data currently held by the module to a csv file."""

    if TEST_ENABLED and results:
        dirpath = (Path(__file__).parent / "test_results/").resolve()
        os.makedirs(dirpath, exist_ok=True)
        csvpath = (dirpath / ("test_results_" + datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss") + ".csv")).resolve()
        df = pd.DataFrame.from_dict(results, orient="index")
        df.to_csv(path_or_buf=csvpath, sep=";")
