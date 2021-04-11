import re

from parsing.webpage_data import WebpageData
from logger import log

# toggle some file-specific logging messages
LOGGING_ENABLED = True

# give lowest sub-score if ratio of question/exclamation marks to sentences reaches this number
QUESTION_MARKS_LIMIT = 0.1
EXCLAMATION_MARKS_LIMIT = 0.05
# give lowest score if number of all-capitalised words reaches this threshold
ALL_CAPS_MAX_TITLE = 2
ALL_CAPS_MAX_TEXT = 10


def evaluate_punctuation(data: WebpageData) -> float:
    """Evaluates credibility of the webpage by analysing punctuation of its headline and text.
    Currently evaluates usage of question and exclamation marks and computes score using global variables above.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 for very high credibility (low usage of question/exclamation marks), 0 for very low credibility (high
        usage of question/exclamation marks).
    """

    # TODO possibly penalise multiple question/exclamation marks in title
    question_marks_title = 0.0 if data.headline.__contains__("?") else 1.0
    exclamation_marks_title = 0.0 if data.headline.__contains__("!") else 1.0
    log("[Tonality] Title punctuation scores: Question marks {} | Exclamation marks {}".
        format(round(question_marks_title, 3), round(exclamation_marks_title, 3)), LOGGING_ENABLED)

    question_marks = 0
    exclamation_marks = 0
    sentences = 0
    for punctuation in re.findall("[!?.]", data.text):
        # TODO possibly penalise multiple question/exclamation marks after another in text
        sentences += 1
        if punctuation == "?":
            question_marks += 1
        elif punctuation == "!":
            exclamation_marks += 1

    question_score = question_marks / sentences
    exclamation_score = exclamation_marks / sentences
    log("[Tonality] Text punctuation per sentence: Question marks {} | Exclamation marks {}".
        format(round(question_score, 3), round(exclamation_score, 3)), LOGGING_ENABLED)

    question_score = 1 - min(question_score * (1 / QUESTION_MARKS_LIMIT), 1)
    exclamation_score = 1 - min(exclamation_score * (1 / EXCLAMATION_MARKS_LIMIT), 1)
    log("[Tonality] Text punctuation scores: Question marks {} | Exclamation marks {}".
        format(round(question_score, 3), round(exclamation_score, 3)), LOGGING_ENABLED)

    return (min(question_marks_title, exclamation_marks_title) + min(question_score, exclamation_score)) / 2


def evaluate_capitalisation(data: WebpageData) -> float:
    """Evaluates credibility of the webpage by analysing usage of all capitalised words in its headline and text.
    Penalises capitalised words in accordance to the global variables above.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 for very high credibility (low number of capitalise words), 0 for very low credibility (high number of
        capitalised words).
    """

    # TODO implement better check to avoid matching acronyms/initialisms, or score text based on length?
    headline_matches = {}
    text_matches = {}
    headline_capitalised = False  # check whether entire headline is capitalised

    if data.headline.upper() is not data.headline:
        for word in re.findall(r"\b[A-Z]+\b", data.headline):
            if len(word) >= 2:
                if word in headline_matches:
                    headline_matches[word] = False
                else:
                    headline_matches[word] = True
    else:
        headline_capitalised = True

    for word in re.findall(r"\b[A-Z]+\b", data.text):
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
