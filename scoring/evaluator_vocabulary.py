import re
from pathlib import Path

from logger import log
from parsing.webpage_data import WebpageData

# modify profanity score gradient given this upper limit
MAX_PROFANITY = 3


def evaluate_profanity(data: WebpageData) -> float:
    """Evaluates webpage by checking for occurrences of profanity.

    Combines and checks webpage headline and text. Profanity score is linear from 0 occurrences (best score => 1) to
    *MAX_PROFANITY* occurrences (worst score => 0).

    :return: 1 for low profanity, 0 for high profanity.
    """

    # file assumed to contain profanity strings, one word/slur per line, lower case (check is case-insensitive)
    profanity_list_path = "../files/profanity.txt"
    filepath = (Path(__file__).parent / profanity_list_path).resolve()

    fulltext = data.headline.lower() + " " + data.text.lower()

    match_count = 0
    with open(filepath, "r") as profanity_words:
        for line in profanity_words.readlines():
            if match := re.findall(r"\b" + line.strip() + r"\b", fulltext):
                match_count += len(match)
                log("[Vocabulary] Profanity list match: {}".format(match))

    score = match_count * (1 / MAX_PROFANITY)
    return 1 - min(score, 1)
