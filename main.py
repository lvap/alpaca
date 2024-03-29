import atexit
import logging
import os
from datetime import datetime
from pathlib import Path

import stats_collector
from parsing.webpage_parser import valid_address
from scoring.credibility_evaluation import evaluate_webpage

# additional signal statistics for processed webpages, exported as csv file
COLLECT_STATS = False

# logging output settings per stream (None = disabled)
LOG_LEVEL_CONSOLE = logging.WARNING
LOG_LEVEL_FILE = logging.DEBUG

# initialise logging
logger = logging.getLogger("alpaca")
logger.setLevel(logging.DEBUG)
logger.propagate = False
if LOG_LEVEL_CONSOLE:
    handler = logging.StreamHandler()
    handler.setLevel(LOG_LEVEL_CONSOLE)
    logger.addHandler(handler)
if LOG_LEVEL_FILE:
    dirpath = (Path(__file__).parent / ".log/").resolve()
    os.makedirs(dirpath, exist_ok=True)
    filepath = (dirpath / (datetime.now().strftime("%Y-%m-%d_%Hh%Mm%Ss.%f") + ".log")).resolve()
    filehandler = logging.FileHandler(filepath, encoding="utf-8")
    filehandler.setFormatter(logging.Formatter("%(asctime)s %(levelname)-8s %(message)s"))
    filehandler.setLevel(LOG_LEVEL_FILE)
    logger.addHandler(filehandler)


def alpaca_init():
    """If a valid webpage URL is submitted, retrieves and prints the webpage's credibility score.

    Initialises the program and waits for & handles console input. Terminates on input *exit* or *quit*. To export
    collected webpage signal statistics, terminate the program in this way after enabling **COLLECT_STATS**.
    """

    logger.info("[Main] ALPACA init")
    atexit.register(logger.info, "[Main] ALPACA end")

    if COLLECT_STATS:
        stats_collector.set_stats_collection(True)
        atexit.register(stats_collector.results_to_csv)

    while True:
        user_input = input("\nEnter webpage address: ")

        if user_input.lower() in ["exit", "quit"]:
            break

        if valid_address(user_input):
            score = evaluate_webpage(user_input)
            if 0 <= score <= 1:
                print("Webpage credibility score: {:.5f} for {}".format(score, user_input))
            else:
                print("Credibility score could not be calculated")
        else:
            print("Invalid address")


def evaluate_datasets():
    """Evaluates credibility of and collects signal statistics for all URLs in the performance analysis datasets.

    The datasets are expected as semicolon-separated list of URLs and credibility/fake news classification ratings,
    with the first line in each file being the column headers.
    """

    logger.info("[Main] Evaluating datasets")
    stats_collector.set_stats_collection(True)
    directory = (Path(__file__).parent / "analysis/datasets").resolve()

    for dataset in directory.glob("*"):
        logger.info("[Main] Evaluating dataset " + str(dataset))
        with open(dataset, "r") as datasetIO:
            for line in datasetIO.readlines()[1:]:  # first line is column headers
                url = line.split(";")[0]
                rating = float(line.split(";")[1])
                if not valid_address(url):
                    url = "http://" + url

                stats_collector.add_result(url, "rating", rating)
                score = evaluate_webpage(url)
                print("Webpage score: {:.5f} for {}".format(score, url))

        stats_collector.results_to_csv()
        stats_collector.clear_results()
        print("Finished dataset " + str(dataset))
        print()


if __name__ == "__main__":
    alpaca_init()
