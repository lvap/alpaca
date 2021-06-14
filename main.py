import atexit
import logging
import os
from datetime import datetime
from pathlib import Path

import pandas as pd

from performance_analysis import performance_test
from parsing.webpage_parser import valid_address
from scoring.credibility_evaluation import evaluate_webpage

# logging output settings per stream (set to None to disable)
LOG_LEVEL_CONSOLE = logging.WARNING
LOG_LEVEL_FILE = logging.DEBUG

logger = logging.getLogger("alpaca")

# initialise logging
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
    logger.info("[Main] Alpaca init")
    atexit.register(performance_test.results_to_csv)
    _handle_input()


def _handle_input():
    """Waits for and handles user input. If a valid webpage URL is submitted, retrieves and prints the webpage's
    credibility score. Terminates on input **exit** or **quit**.
    """

    while True:
        user_input = input("\nEnter webpage address: ")
        logger.debug("[Main] Processing input: " + user_input)

        if user_input.lower() in ["exit", "quit"]:
            logger.info("[Main] Alpaca end")
            break

        if valid_address(user_input):
            score = evaluate_webpage(user_input)
            if 0 <= score <= 1:
                print("Webpage score: {:.5f} for {}".format(score, user_input))
            else:
                print("Score could not be calculated")

        else:
            print("Invalid address")
            logger.debug("[Main] Invalid address")


if __name__ == "__main__":
    # alpaca_init()
    dataset = pd.read_csv("dataset.csv", index_col="document_id", sep=";")
    dataset = dataset.sample(1000)
    dataset.to_csv("sample.csv", sep=";")
