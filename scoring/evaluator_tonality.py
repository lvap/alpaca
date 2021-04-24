import re

from parsing.webpage_data import WebpageData
from logger import log

# toggle some file-specific logging messages
LOGGING_ENABLED = False

# punctuation score is linear in the ratio of punctuation to sentences from 0 (best score) to this limit (worst)
QUESTION_MARKS_LIMIT = 0.1
EXCLAMATION_MARKS_LIMIT = 0.05
# capitalisation score is linear from 0 occurrences (best score) to this threshold (worst)
ALL_CAPS_MAX_TITLE = 2
ALL_CAPS_MAX_TEXT = 10


def evaluate_question_marks(data: WebpageData) -> float:
    """Evaluates webpage credibility focusing on question mark usage.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 for very high credibility (low usage of question marks), 0 for very low credibility (high
        usage of question marks).
    """

    # TODO possibly penalise multiple question marks in title, or directly after another in text
    question_score_title = 0 if "?" in data.headline else 1

    question_marks = 0
    sentences = 0
    for punctuation in re.findall("[!?.]", data.text):
        sentences += 1
        if punctuation == "?":
            question_marks += 1

    question_score_text = question_marks / sentences
    log("[Tonality] Question marks per sentence: {}".format(round(question_score_text, 3)), LOGGING_ENABLED)

    question_score_text = 1 - min(question_score_text * (1 / QUESTION_MARKS_LIMIT), 1)
    return (question_score_title + 2 * question_score_text) / 3


def evaluate_exclamation_marks(data: WebpageData) -> float:
    """Evaluates webpage credibility by analysing punctuation used in its headline and text.
    Examines usage of exclamation marks and computes score using global variables above.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 for very high credibility (low usage of exclamation marks), 0 for very low credibility (high
        usage of exclamation marks).
    """

    # TODO possibly penalise multiple exclamation marks in title, or directly after another in text
    exclamation_score_title = 0 if "!" in data.headline else 1

    exclamation_marks = 0
    sentences = 0
    for punctuation in re.findall("[!?.]", data.text):
        sentences += 1
        if punctuation == "!":
            exclamation_marks += 1

    exclamation_score_text = exclamation_marks / sentences
    log("[Tonality] Exclamation marks per sentence: {}".format(round(exclamation_score_text, 3)), LOGGING_ENABLED)

    exclamation_score_text = 1 - min(exclamation_score_text * (1 / EXCLAMATION_MARKS_LIMIT), 1)
    return (exclamation_score_title + 2 * exclamation_score_text) / 3


def evaluate_capitalisation(data: WebpageData) -> float:
    """Evaluates webpage by analysing usage of all capitalised words in its headline and text.
    Penalises capitalised words in accordance to the global variables above.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 for very high credibility (low number of capitalise words), 0 for very low credibility (high number of
        capitalised words).
    """

    # TODO implement better check to avoid matching acronyms/initialisms (alternatively score text based on length)?
    headline_matches = {}
    text_matches = {}
    headline_capitalised = False  # check whether entire headline is capitalised
    all_caps = re.compile(r"\b[A-Z]+\b")

    if data.headline.upper() is not data.headline:
        for word in all_caps.findall(data.headline):
            if len(word) >= 2:
                if word in headline_matches:
                    headline_matches[word] = False
                else:
                    headline_matches[word] = True
    else:
        headline_capitalised = True

    for word in all_caps.findall(data.text):
        if len(word) >= 2:
            if word in headline_matches or word in text_matches:
                headline_matches[word] = False
                text_matches[word] = False
            else:
                text_matches[word] = True

    headline_score = 0
    all_cap_words_title = []
    if not headline_capitalised:
        for match, match_value in headline_matches.items():
            if match_value:
                all_cap_words_title.append(match)
                headline_score += 1
        headline_score = 1 - (headline_score / ALL_CAPS_MAX_TITLE)
        headline_score = max(headline_score, 0)

    text_score = 0
    all_cap_words_text = []
    for match, match_value in text_matches.items():
        if match_value:
            all_cap_words_text.append(match)
            text_score += 1
    text_score = 1 - (text_score / ALL_CAPS_MAX_TEXT)
    text_score = max(text_score, 0)

    log("[Tonality] All capitalised words: Title {} | Text {}".format(all_cap_words_title, all_cap_words_text),
        LOGGING_ENABLED)

    return (headline_score + text_score) / 2 if not headline_capitalised else text_score
