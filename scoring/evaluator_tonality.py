import re

from parsing.webpage_data import WebpageData
from logger import log

# toggle some file-specific logging messages
LOGGING_ENABLED = False

# modify punctuation scores gradient given these upper limits
QUESTION_MARKS_LIMIT = 0.15
EXCLAMATION_MARKS_LIMIT = 0.05
# modify capitalisation score gradient given these upper limits
ALL_CAPS_MAX_TITLE = 2
ALL_CAPS_MAX_TEXT = 10


def evaluate_question_marks(data: WebpageData) -> float:
    """Evaluates webpage question mark usage.

    Returned score is linear from 0 question marks per sentence (no question mark usage, best score => 1) to
    *QUESTION_MARKS_LIMIT* question marks per sentence (high usage, worst score => 0). Returns 0 if headline or
    text include double question marks ("??").

    :return: 1 for low usage of question marks, 0 for high usage of question marks.
    """

    # penalise double question marks
    if "??" in data.headline or "??" in data.text:
        log("[Tonality] Double question marks detected", LOGGING_ENABLED)
        return 0

    question_score_title = 0 if "?" in data.headline else 1

    question_marks = 0
    sentences = 0  # FIXME use tokenizer instead (eg Dr. = 1 sentence)
    for punctuation in re.findall("[!?.]", data.text):
        sentences += 1
        if punctuation == "?":
            question_marks += 1

    question_score_text = question_marks / sentences
    log("[Tonality] Question marks per sentence: {:.3f}".format(question_score_text), LOGGING_ENABLED)

    question_score_text = 1 - min(question_score_text * (1 / QUESTION_MARKS_LIMIT), 1)
    return (question_score_title + 2 * question_score_text) / 3


def evaluate_exclamation_marks(data: WebpageData) -> float:
    """Evaluates webpage exclamation mark usage.

    Returned score is linear from 0 exclamation marks per sentence (no exclamation mark usage, best score => 1) to
    *EXCLAMATION_MARKS_LIMIT* exclamation marks per sentence (high usage, worst score => 0). Returns 0 if headline or
    text include double exclamation marks ("!!").

    :return: 1 for low usage of exclamation marks, 0 for high usage of exclamation marks.
    """

    # penalise double exclamation marks
    if "!!" in data.headline or "!!" in data.text:
        log("[Tonality] Double exclamation marks detected", LOGGING_ENABLED)
        return 0

    exclamation_score_title = 0 if "!" in data.headline else 1

    exclamation_marks = 0
    sentences = 0  # FIXME use tokenizer instead (eg Dr. = 1 sentence)
    for punctuation in re.findall("[!?.]", data.text):
        sentences += 1
        if punctuation == "!":
            exclamation_marks += 1

    exclamation_score_text = exclamation_marks / sentences
    log("[Tonality] Exclamation marks per sentence: {:.3f}".format(exclamation_score_text), LOGGING_ENABLED)

    exclamation_score_text = 1 - min(exclamation_score_text * (1 / EXCLAMATION_MARKS_LIMIT), 1)
    return (exclamation_score_title + 2 * exclamation_score_text) / 3


def evaluate_capitalisation(data: WebpageData) -> float:
    """Evaluates webpage usage of all-capitalised words.

    Capitalisation score is linear from 0 occurrences (best score => 1) to *ALL_CAPS_MAX_TITLE* and *ALL_CAPS_MAX_TEXT*
    occurrences (worst score => 0). Words that are all-capitalised and occur more than once in either title or text
    are assumed to be acronyms or initialisms, and ignored.

    :return: 1 for low number of all-capitalised words, 0 for high number of capitalised words.
    """

    # TODO implement better check to avoid matching acronyms/initialisms (alternatively score text based on length)?

    headline_matches = {}
    text_matches = {}
    headline_capitalised = False
    all_caps = re.compile(r"\b[A-Z]+\b")

    # collect all-cap words in headline
    if data.headline.upper() is not data.headline:
        for word in all_caps.findall(data.headline):
            if len(word) >= 2:
                if word in headline_matches:
                    headline_matches[word] = False
                else:
                    headline_matches[word] = True
    else:
        # entire headline is capitalised
        headline_capitalised = True

    # collect all-cap words in text
    for word in all_caps.findall(data.text):
        if len(word) >= 2:
            if word in headline_matches or word in text_matches:
                headline_matches[word] = False
                text_matches[word] = False
            else:
                text_matches[word] = True

    # compute headline sub-score
    headline_score = 0
    all_cap_words_title = []
    if not headline_capitalised:
        for match, match_value in headline_matches.items():
            if match_value:
                all_cap_words_title.append(match)
                headline_score += 1
        headline_score = 1 - (headline_score / ALL_CAPS_MAX_TITLE)
        headline_score = max(headline_score, 0)

    # compute text body sub-score
    text_score = 0
    all_cap_words_text = []
    for match, match_value in text_matches.items():
        if match_value:
            all_cap_words_text.append(match)
            text_score += 1
    text_score = 1 - (text_score / ALL_CAPS_MAX_TEXT)
    text_score = max(text_score, 0)

    log("[Tonality] All capitalised words: Title {} | Text {}".format(all_cap_words_title, all_cap_words_text),
        all_cap_words_title or all_cap_words_text)

    return (headline_score + text_score) / 2 if not headline_capitalised else text_score
