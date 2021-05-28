import logging
import re

import language_tool_python as ltp
import spacy

from parsing.webpage_data import WebpageData

# modify grammar/spelling error score gradient given this upper limit
from parsing.webpage_parser import has_ending_punctuation

ERROR_LIMIT = 0.2

LOGGER = logging.getLogger("alpaca")


def evaluate_grammar_spelling(data: WebpageData) -> float:
    """Evaluates a webpage's language correctness.

    Determines how many spelling or grammar errors were encountered on the page and scales this value
    by overall word count. Specifically, the returned score is linear from 0 errors per word (no errors,
    best score => 1) to *ERRORS_LIMIT* errors per word (large amount of errors, worst score => 0).

    :return: Value between 0 (large amount of errors) and 1 (no errors).
    """

    # set up named entity recognition to avoid classifying names as spelling errors
    headline_ending = " " if has_ending_punctuation(data.headline) else ". " if data.headline else ""
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(data.headline + headline_ending + data.text)
    entities = ["ORG", "PERSON", "NORP", "FACILITY", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW"]
    names = [ent.text for ent in doc.ents if ent.label_ in entities]
    LOGGER.debug("[Grammar-Spelling] Recognised named entities: {}".format(names))

    tool = ltp.LanguageTool("en-US")
    matches = tool.check(data.headline)
    matches_to_ignore = 0
    if matches and matches[len(matches) - 1].ruleId == "PUNCTUATION_PARAGRAPH_END":
        # ignore error for missing punctuation at title ending
        matches.pop()
    # headline_matches = len(matches)
    matches += tool.check(data.text)

    # filter out irrelevant matches and penalise spelling errors only once (probably not actual errors)
    unknown_words = []
    for index, match in enumerate(matches):
        if (match.ruleId in ["EN_QUOTES", "DASH_RULE", "EXTREME_ADJECTIVES"]
                or match.category == "REDUNDANCY" or "is British English" in match.message
                or any(match.matchedText in name for name in names)):
            matches_to_ignore += 1
            continue
        elif "Possible spelling mistake" in match.message:
            if match.matchedText in unknown_words:
                matches_to_ignore += 1
                continue
            else:
                unknown_words.append(match.matchedText)
        LOGGER.debug("[Grammar-Spelling] Text error:\n{}".format(match))

    error_score = len(matches) - matches_to_ignore
    word_count = data.headline.count(" ") + data.text.count(" ") + 2 if data.headline else data.text.count(" ") + 1
    # exclude strings consisting of a single non-alphanumeric character
    word_count -= len(re.findall(r"\s\W\s", data.headline)) + len(re.findall(r"\s\W\s", data.text))
    error_score = 1 - (error_score / (word_count * ERROR_LIMIT))

    LOGGER.info("[Grammar-Spelling] {} errors in {} words ({} errors ignored), {:.3f} errors per word"
                .format(len(matches) - matches_to_ignore, word_count, matches_to_ignore, error_score / word_count))

    return max(error_score, 0)
