import re
from pathlib import Path

from parsing.webpage_data import WebpageData
from logger import log

# toggle some file-specific logging messages
LOGGING_ENABLED = False

# profanity score is linear from 0 occurrences (best score) to this threshold (worst)
MAX_PROFANITY = 3
# relative path (from parent) to file containing strings to match for profanity evaluation
PROFANITY_LIST_PATH = "../files/profanity.txt"


def evaluate_profanity(data: WebpageData) -> float:
    """Evaluates credibility of the webpage by checking the article headline and text for profanity.
    Relies on external file containing profanity strings according to path variable above.
    Additionally assumes all profanity in said file is lower case (check is case-insensitive).

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 for low profanity, 0 for high profanity as determined by global variable above.
    """

    filepath = (Path(__file__).parent / PROFANITY_LIST_PATH).resolve()
    fulltext = data.headline.lower() + " " + data.text.lower()
    match_count = 0
    with open(filepath, "r") as profanity_words:
        for line in profanity_words.readlines():
            if match := re.findall(r"\b"+line.strip()+r"\b", fulltext):
                match_count += len(match)
                log("[Vocabulary] Profanity list match: {}".format(match))

    score = match_count * (1 / MAX_PROFANITY)
    return 1 - min(score, 1)
