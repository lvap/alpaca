import os
import re
from collections import defaultdict
from datetime import datetime
from pathlib import Path

import pandas as pd

from parsing.webpage_parser import valid_address, get_real_url

# collects signal statistics from evaluation runs
results = defaultdict(lambda: defaultdict(float))

# toggle collection of webpage statistics, should preferably only be changed through set_stats_collection()
_STATS_ENABLED = False


def set_stats_collection(enable_or_disable: bool):
    """Set whether the program should collect signal statistics for the processed webpages."""

    global _STATS_ENABLED
    _STATS_ENABLED = enable_or_disable


def add_result(url: str, field: str, value: float):
    """Add data value regarding a webpage to the module. Collected data can later be exported as csv file.

    :param url: Url of the webpage the data belongs to.
    :param field: Name/class of the data point to be added (later column header in table).
    :param value: Value of the data point to be added.
    """

    if _STATS_ENABLED:
        results[url][field] = value


def results_to_csv():
    """Exports webpage statistics currently held by the module to a csv file."""

    if _STATS_ENABLED and results:
        dirpath = (Path(__file__).parent / "stats_results/").resolve()
        os.makedirs(dirpath, exist_ok=True)
        csvpath = (dirpath / ("stats_results_" + datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss") + ".csv")).resolve()
        results_df = pd.DataFrame.from_dict(results, orient="index")
        results_df.index.rename("url", inplace=True)
        results_df.to_csv(path_or_buf=csvpath, sep=";")


def clear_results():
    """Resets the webpage stats results dictionary."""

    global results
    results = defaultdict(lambda: defaultdict(float))


def check_duplicate_urls():
    """Checks whether the datasets for performance analysis contain duplicate URLs. Assumes http(s) URLs."""

    directory = (Path(__file__).parent / "datasets").resolve()
    urls = set()
    check_dupl = lambda links, link: print("Duplicate URL: " + link) if link in links else None

    for dataset in directory.glob("*"):
        with open(dataset, "r") as datasetIO:
            for line in datasetIO.readlines()[1:]:  # first line is column headers
                url = line.split(";")[0]

                if valid_address(url):
                    url2 = get_real_url(url)  # check urls for archived + original page
                    if url2 and url != url2:
                        url2 = url2[re.search(r"https?://", url2).end():]
                        check_dupl(urls, url2)
                        urls.add(url2)
                    url = url[re.search(r"https?://", url).end():]
                    check_dupl(urls, url)
                    urls.add(url)
                elif valid_address("http://" + url):
                    check_dupl(urls, url)
                    urls.add(url)
                else:
                    print("Invalid URL: " + url)

        print("Finished dataset " + str(dataset))
