import re

from parsing.webpage_data import WebpageData
from logger import log

# toggle some file-specific logging messages
LOGGING_ENABLED = False

# TODO proper limits on punctuation usage/all caps?
# sub-score for title punctuation goes from this number to 0 linearly (ie this amount or more gives a score of 0)
MAX_EXCLAMATION_MARKS_TITLE = 1
MAX_QUESTION_MARKS_TITLE = 2
# acceptable levels of punctuation per sentence to still get maximum score
EXCLAMATION_MARK_LIMIT_TEXT = 0.0
QUESTION_MARK_LIMIT_TEXT = 0.05

# acceptable number of all-capitalised words to still get maximum score (title: absolute, text: per sentence)
ALL_CAPS_LIMIT_TITLE = 1
ALL_CAPS_LIMIT_TEXT = 0.05


def evaluate_punctuation(data: WebpageData) -> float:
    """Evaluates credibility of the webpage by analysing punctuation of its headline and text.
    Currently evaluates usage of question and exclamation marks and computes score using global variables above.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 for very high credibility (low usage of question/exclamation marks), 0 for very low credibility (high
        usage of question/exclamation marks).
    """

    headline_score = 1.0
    headline_score -= (1.0 / MAX_EXCLAMATION_MARKS_TITLE) * data.headline.count("!")
    headline_score -= (1.0 / MAX_QUESTION_MARKS_TITLE) * data.headline.count("?")
    headline_score = max(headline_score, 0.0)

    exclamation_marks = 0
    question_marks = 0
    sentences = 0
    for punctuation in re.findall("[!?.]", data.text):
        # TODO possibly penalise multiple question/exclamation marks after another
        sentences += 1
        if punctuation == "!":
            exclamation_marks += 1
        elif punctuation == "?":
            question_marks += 1

    question_score = ((question_marks - QUESTION_MARK_LIMIT_TEXT * sentences)
                      / (sentences - QUESTION_MARK_LIMIT_TEXT * sentences))
    exclamation_score = ((exclamation_marks - EXCLAMATION_MARK_LIMIT_TEXT * sentences)
                         / (sentences - EXCLAMATION_MARK_LIMIT_TEXT * sentences))

    log("*** [Tonality] Text punctuation metrics: Question marks {} | Exclamation marks {}".
        format(round(question_score, 3), round(exclamation_score, 3)), LOGGING_ENABLED)

    text_score = max(question_score, exclamation_score)
    text_score = max(min(text_score, 1.0), 0.0)
    text_score = 1.0 - text_score

    return (headline_score + 2.0 * text_score) / 3.0


def evaluate_capitalisation(data: WebpageData) -> float:
    """Evaluates credibility of the webpage by analysing usage of all capitalised words in its headline and text.
    Penalises capitalised words in accordance to the global variables above.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 for very high credibility (low number of capitalise words), 0 for very low credibility (high number of
        capitalised words).
    """

    # TODO implement better check to avoid matching acronyms/initialisms
    headline_matches = {}
    text_matches = {}
    for word in re.findall(r"\b[A-Z]+\b", data.headline):
        if len(word) >= 2:
            if word in headline_matches:
                headline_matches[word] = False
            else:
                headline_matches[word] = True
    for word in re.findall(r"\b[A-Z]+\b", data.text):
        if len(word) >= 2:
            if word in headline_matches or word in text_matches:
                headline_matches[word] = False
                text_matches[word] = False
            else:
                text_matches[word] = True

    headline_score = 1.0
    bonus = ALL_CAPS_LIMIT_TITLE
    all_cap_words_title = []
    for match, match_value in headline_matches.items():
        if match_value:
            all_cap_words_title.append(match)
            if bonus > 0:
                bonus -= 1
            else:
                headline_score = 0.0

    text_score = 0.0
    all_cap_words_text = []
    for match, match_value in text_matches.items():
        if match_value:
            all_cap_words_text.append(match)
            text_score += 1.0

    log("*** [Tonality] All capitalised words: Title {} | Text {}".format(all_cap_words_title, all_cap_words_text),
        LOGGING_ENABLED)

    word_count = len(data.text.split()) - len(re.findall(r"\s.\s", data.text))
    text_score = (text_score - ALL_CAPS_LIMIT_TEXT * word_count) / (word_count - ALL_CAPS_LIMIT_TEXT * word_count)
    log("*** [Tonality] Text all caps metric: {}".format(text_score), LOGGING_ENABLED)
    text_score = max(min(text_score, 1.0), 0.0)
    text_score = 1.0 - text_score

    return (headline_score + 2.0 * text_score) / 3.0
