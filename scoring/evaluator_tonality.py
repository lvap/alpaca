import logging
import re

from analysis import stats_collector
from parsing.webpage_data import WebpageData

# modify punctuation scores gradient given these upper limits
QUESTIONS_LIMIT = 0.15
EXCLAMATIONS_LIMIT = 0.05
# modify capitalisation score gradient given these upper limits
ALL_CAPS_MAX_TITLE = 2
ALL_CAPS_MAX_TEXT = 10

# boundary checks
if not 0 < QUESTIONS_LIMIT <= 1 or not 0 < EXCLAMATIONS_LIMIT <= 1 or ALL_CAPS_MAX_TITLE <= 0 or ALL_CAPS_MAX_TEXT <= 0:
    raise ValueError("A constant for tonality evaluation is set incorrectly")

logger = logging.getLogger("alpaca")


def evaluate_questions_text(data: WebpageData) -> float:
    """Evaluates webpage text question mark usage.

    Returned score is linear from 0 question marks per sentence (no question mark usage, best score => 1) to
    *QUESTION_MARKS_LIMIT* question marks per sentence (high usage, worst score => 0).

    :return: 1 for low usage of question marks, 0 for high usage of question marks.
    """

    question_score = data.text.count("?") / len(data.text_sentences)
    
    logger.debug("[Tonality] Question marks per sentence: {:.3f}".format(question_score))
    stats_collector.add_result(data.url, "questions_text_per_sentence", question_score)

    question_score = min(question_score / QUESTIONS_LIMIT, 1)
    return 1 - question_score


def evaluate_questions_title(data: WebpageData) -> float:
    """Evaluates webpage headline question mark usage.

    :return: 1 if the headline contains no questions marks, else 0.
    """

    stats_collector.add_result(data.url, "questions_title", data.headline.count("?"))
    return 0 if "?" in data.headline else 1


def evaluate_exclamations_text(data: WebpageData) -> float:
    """Evaluates webpage text exclamation mark usage.

    Returned score is linear from 0 exclamation marks per sentence (no exclamation mark usage, best score => 1) to
    *EXCLAMATION_MARKS_LIMIT* exclamation marks per sentence (high usage, worst score => 0).

    :return: 1 for low usage of exclamation marks, 0 for high usage of exclamation marks.
    """

    exclamation_score = data.text.count("!") / len(data.text_sentences)

    logger.debug("[Tonality] Exclamation marks per sentence: {:.3f}".format(exclamation_score))
    stats_collector.add_result(data.url, "exclamations_text_per_sentence", exclamation_score)

    exclamation_score = min(exclamation_score / EXCLAMATIONS_LIMIT, 1)
    return 1 - exclamation_score


def evaluate_exclamations_title(data: WebpageData) -> float:
    """Evaluates webpage headline exclamation mark usage.

    :return: 1 if the headline contains no exclamation marks, else 0.
    """

    stats_collector.add_result(data.url, "exclamations_title", data.headline.count("!"))
    return 0 if "!" in data.headline else 1


def evaluate_all_caps_text(data: WebpageData) -> float:
    """Evaluates webpage text usage of all-capitalised words.

    Capitalisation score is linear from 0 occurrences (best score => 1) to *ALL_CAPS_MAX_TEXT* occurrences 
    (worst score => 0). Words that are all-capitalised and occur more than once in either title or text
    are assumed to be acronyms or initialisms, and ignored.

    :return: 1 for low number of all-capitalised words, 0 for high number of capitalised words.
    """

    # TODO implement better check to avoid matching acronyms/initialisms (alternatively score text based on length)?

    headline_matches = {}
    text_matches = {}
    all_caps = re.compile(r"\b[A-Z]+\b")

    # collect all-cap words in headline (unless empty/entirely capitalised)
    if data.headline.upper() != data.headline:
        for word in all_caps.findall(data.headline):
            if len(word) >= 2:
                if word in headline_matches:
                    headline_matches[word] = False
                else:
                    headline_matches[word] = True

    # collect all-cap words in text
    for word in all_caps.findall(data.text):
        if len(word) >= 2:
            if word in headline_matches or word in text_matches:
                headline_matches[word] = False
                text_matches[word] = False
            else:
                text_matches[word] = True

    # compute score
    score = 0
    all_caps_words = []
    for match, match_value in text_matches.items():
        if match_value:
            all_caps_words.append(match)
            score += 1

    if all_caps_words:
        logger.info("[Tonality] All capitalised words in text: {}".format(all_caps_words))
    stats_collector.add_result(data.url, "all_caps_text", score)

    score = 1 - (score / ALL_CAPS_MAX_TEXT)
    return max(score, 0)


def evaluate_all_caps_title(data: WebpageData) -> float:
    """Evaluates webpage headline usage of all-capitalised words.

    Capitalisation score is linear from 0 occurrences (best score => 1) to *ALL_CAPS_MAX_TITLE* and *ALL_CAPS_MAX_TEXT*
    occurrences (worst score => 0). Words that are all-capitalised and occur more than once in either title or text
    are assumed to be acronyms or initialisms, and ignored.

    :return: 1 for low number of all-capitalised words, 0 for high number of capitalised words.
    """

    # TODO implement better check to avoid matching acronyms/initialisms (alternatively score text based on length)?

    if data.headline.upper() == data.headline:
        # entire headline is capitalised (or empty)
        stats_collector.add_result(data.url, "all_caps_title", -1)
        return 1

    headline_matches = {}
    text_matches = {}
    all_caps = re.compile(r"\b[A-Z]+\b")

    # collect all-cap words in headline
    for word in all_caps.findall(data.headline):
        if len(word) >= 2:
            if word in headline_matches:
                headline_matches[word] = False
            else:
                headline_matches[word] = True

    # collect all-cap words in text
    for word in all_caps.findall(data.text):
        if len(word) >= 2:
            if word in headline_matches or word in text_matches:
                headline_matches[word] = False
                text_matches[word] = False
            else:
                text_matches[word] = True

    # compute score
    score = 0
    all_caps_words = []
    for match, match_value in headline_matches.items():
        if match_value:
            all_caps_words.append(match)
            score += 1

    if all_caps_words:
        logger.info("[Tonality] All capitalised words in title: {}".format(all_caps_words))
    stats_collector.add_result(data.url, "all_caps_title", score)

    score = 1 - (score / ALL_CAPS_MAX_TITLE)
    return max(score, 0)
