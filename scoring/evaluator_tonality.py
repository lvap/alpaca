import logging
import re

import spacy

import stats_collector
from parsing.webpage_data import WebpageData

logger = logging.getLogger("alpaca")

# value limits for subscores
QUESTIONS_LIMIT_TEXT = 0.2
EXCLAMATIONS_LIMIT_TEXT = 0.05
ALL_CAPS_LIMIT_TITLE = 2
ALL_CAPS_LIMIT_TEXT = 0.05

# boundary checks
if not (0 < QUESTIONS_LIMIT_TEXT <= 1 and 0 < EXCLAMATIONS_LIMIT_TEXT <= 1 and 0 < ALL_CAPS_LIMIT_TITLE
        and 0 < ALL_CAPS_LIMIT_TEXT <= 1):
    raise ValueError("A constant for tonality evaluation is set incorrectly")


def evaluate_questions_text(data: WebpageData) -> float:
    """Evaluates webpage text question mark usage.

    Returned score is linear from 0 question marks per sentence (no question mark usage, best score => 1) to
    **QUESTIONS_LIMIT_TEXT** question marks per sentence (high usage, worst score => 0).

    :return: 1 for low usage of question marks, 0 for high usage of question marks.
    """

    question_score = data.text.count("?") / len(data.text_sentences)

    logger.debug("[Tonality] Question marks per sentence: {:.3f}".format(question_score))
    stats_collector.add_result(data.url, "questions_text_per_sentence", question_score)

    question_score = min(question_score / QUESTIONS_LIMIT_TEXT, 1)
    return 1 - question_score


def evaluate_questions_title(data: WebpageData) -> float:
    """Evaluates webpage headline question mark usage.

    :return: 1 if the headline contains no questions marks, else 0.
    """

    stats_collector.add_result(data.url, "questions_title", data.headline.count("?") if data.headline else -10)
    return 0 if "?" in data.headline else 1


def evaluate_exclamations_text(data: WebpageData) -> float:
    """Evaluates webpage text exclamation mark usage.

    Returned score is linear from 0 exclamation marks per sentence (no exclamation mark usage, best score => 1) to
    **EXCLAMATIONS_LIMIT_TEXT** exclamation marks per sentence (high usage, worst score => 0).

    :return: 1 for low usage of exclamation marks, 0 for high usage of exclamation marks.
    """

    exclamation_score = data.text.count("!") / len(data.text_sentences)

    logger.debug("[Tonality] Exclamation marks per sentence: {:.3f}".format(exclamation_score))
    stats_collector.add_result(data.url, "exclamations_text_per_sentence", exclamation_score)

    exclamation_score = min(exclamation_score / EXCLAMATIONS_LIMIT_TEXT, 1)
    return 1 - exclamation_score


def evaluate_exclamations_title(data: WebpageData) -> float:
    """Evaluates webpage headline exclamation mark usage.

    :return: 1 if the headline contains no exclamation marks, else 0.
    """

    stats_collector.add_result(data.url, "exclamations_title", data.headline.count("!") if data.headline else -10)
    return 0 if "!" in data.headline else 1


def evaluate_all_caps_text(data: WebpageData) -> float:
    """Evaluates webpage text usage of words in all capitals.

    Capitalisation score is linear from 0 occurrences (best score => 1) to **ALL_CAPS_LIMIT_TEXT** occurrences
    (worst score => 0). Words that are all capitals and occur more than once in either title or text
    are assumed to be acronyms or initialisms, and ignored. We also ignore all caps words that are recognised as
    entities.

    :return: 1 for low number of all capitals words, 0 for a high number.
    """

    headline_matches = {}
    text_matches = {}
    all_caps = re.compile(r"\b[A-Z]+\b")

    # named entity recognition to avoid classifying initialisms/acronyms as all caps words
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(data.headline + "\n" + data.text)
    entity_labels = ["PERSON", "NORP", "FAC", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW"]
    entities = set([ent.text.strip() for ent in doc.ents if ent.label_ in entity_labels])

    # collect all-cap words in headline (unless empty/entirely capitalised)
    if data.headline.upper() != data.headline:
        for word in all_caps.findall(data.headline):
            if len(word) >= 2 and not any(word in entity.split() for entity in entities):
                if word in headline_matches:
                    headline_matches[word] = False
                else:
                    headline_matches[word] = True

    # collect all-cap words in text
    for word in all_caps.findall(data.text):
        if len(word) >= 2 and not any(word in entity.split() for entity in entities):
            if word in headline_matches or word in text_matches:
                headline_matches[word] = False
                text_matches[word] = False
            else:
                text_matches[word] = True

    # compute ratio all caps per word
    all_caps_count = 0
    all_caps_words = []
    for match, match_value in text_matches.items():
        if match_value:
            all_caps_words.append(match)
            all_caps_count += 1
    all_caps_ratio = all_caps_count / len(data.text_words)

    logger.debug("[Tonality] {} all caps words in text ({:.3f} per word): {}".format(len(all_caps_words),
                                                                                     all_caps_ratio, all_caps_words))
    stats_collector.add_result(data.url, "all_caps_text", all_caps_ratio)

    score = 1 - (all_caps_ratio / ALL_CAPS_LIMIT_TEXT)
    return max(score, 0)


def evaluate_all_caps_title(data: WebpageData) -> float:
    """Evaluates webpage headline usage of words in all capitals.

    Capitalisation score is linear from 0 occurrences (best score => 1) to **ALL_CAPS_LIMIT_TITLE**
    occurrences (worst score => 0). Words that are all capitals and occur more than once in either title or text
    are assumed to be acronyms or initialisms, and ignored. We also ignore all caps words that are recognised as
    entities.

    :return: 1 for low number of all capitals words, 0 for a high number.
    """

    if data.headline.upper() == data.headline:
        # entire headline is capitalised (or empty)
        stats_collector.add_result(data.url, "all_caps_title", -10)
        return 1

    headline_matches = {}
    text_matches = {}
    all_caps = re.compile(r"\b[A-Z]+\b")

    # named entity recognition to avoid classifying initialisms/acronyms as all caps words
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(data.headline + "\n" + data.text)
    entity_labels = ["PERSON", "NORP", "FAC", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW"]
    entities = set([ent.text.strip() for ent in doc.ents if ent.label_ in entity_labels])

    # collect all-cap words in headline
    for word in all_caps.findall(data.headline):
        if len(word) >= 2 and not any(word in entity.split() for entity in entities):
            if word in headline_matches:
                headline_matches[word] = False
            else:
                headline_matches[word] = True

    # collect all-cap words in text
    for word in all_caps.findall(data.text):
        if len(word) >= 2 and not any(word in entity.split() for entity in entities):
            if word in headline_matches or word in text_matches:
                headline_matches[word] = False
                text_matches[word] = False
            else:
                text_matches[word] = True

    # count all caps words
    all_caps_words = []
    for match, match_value in headline_matches.items():
        if match_value:
            all_caps_words.append(match)
    all_caps_count = len(all_caps_words)

    logger.debug("[Tonality] {} all caps words in title: {}".format(all_caps_count, all_caps_words))
    stats_collector.add_result(data.url, "all_caps_title", all_caps_count)

    return 1 - (all_caps_count / ALL_CAPS_LIMIT_TITLE)
