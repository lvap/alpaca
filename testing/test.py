import os
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

# toggle test run (exporting signal stats for all processed webpages to csv)
TEST_ENABLED = False

# collects signal data for test runs
results = defaultdict(lambda: defaultdict(float))


def add_result(url: str, field: str, value: float):
    """TODO documentation"""

    if TEST_ENABLED:
        results[url][field] = value


def results_to_csv():
    """TODO documentation"""

    if TEST_ENABLED and results:
        dirpath = (Path(__file__).parent / "test_runs/").resolve()
        os.makedirs(dirpath, exist_ok=True)
        csvpath = (dirpath / ("test_results_" + datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss") + ".csv")).resolve()
        df = pd.DataFrame.from_dict(results, orient="index")
        df.to_csv(path_or_buf=csvpath, sep=";")
