import logging

import language_tool_python as ltp
import spacy

import stats_collector
from parsing.tokenize import word_tokenize
from parsing.webpage_data import WebpageData

# modify grammar/spelling error score gradient given this upper limit
ERROR_LIMIT = 0.03
# TODO scale from 0.005 (=>best score) to 0.03 (=>worst)

# boundary check
if not 0 < ERROR_LIMIT <= 1:
    raise ValueError("ERROR_LIMIT must be greater than 0 and lower than or equal to 1.")

# languageTool server
lang_tool = ltp.LanguageTool("en-US")

logger = logging.getLogger("alpaca")


def evaluate_errors(data: WebpageData) -> float:
    """Evaluates a webpage's language correctness.

    Determines how many spelling or grammar errors were encountered on the page and scales this value
    by overall word count. Specifically, the returned score is linear from 0 unique errors per word (no errors,
    best score => 1) to *ERRORS_LIMIT* unique errors per word (large amount of errors, worst score => 0).

    :return: Value between 0 (large amount of errors) and 1 (no errors).
    """

    matches = lang_tool.check(data.headline)
    if matches and matches[-1].ruleId == "PUNCTUATION_PARAGRAPH_END":
        # ignore error for missing punctuation at title ending
        matches.pop()
    matches += lang_tool.check(data.text)

    # named entity recognition to avoid classifying names as spelling errors
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(data.headline + "\n" + data.text)
    entities = ["PERSON", "NORP", "FAC", "FACILITY", "ORG", "GPE", "LOC", "PRODUCT", "EVENT", "WORK_OF_ART", "LAW"]
    names = set([ent.text.strip() for ent in doc.ents if ent.label_ in entities])
    logger.debug("[Errors] {} recognised named entities: {}".format(len(names), names))

    # filter out irrelevant matches and penalise errors only once
    matches_to_ignore = 0
    unknown_words = []
    for match in matches:
        if (match.ruleId in ["EN_QUOTES", "DASH_RULE", "EXTREME_ADJECTIVES", "MONTH_OF_XXXX",
                             "ENGLISH_WORD_REPEAT_BEGINNING_RULE"]
                or match.category == "REDUNDANCY" or "is British English" in match.message
                or match.matchedText in unknown_words or ("Possible spelling mistake" in match.message
                                                          and any(match.matchedText in nm.split() for nm in names))):
            matches_to_ignore += 1
        else:
            unknown_words.append(match.matchedText)
            logger.debug("[Errors] Text error:\n{}".format(match))

    error_score = len(matches) - matches_to_ignore
    word_count = len(word_tokenize(data.headline)) + len(data.text_words)
    subscore = 1 - (error_score / (word_count * ERROR_LIMIT))

    logger.debug("[Errors] {} grammar or spelling errors in {} words ({} errors ignored), {:.3f} errors per word"
                 .format(len(matches) - matches_to_ignore, word_count, matches_to_ignore, error_score / word_count))
    stats_collector.add_result(data.url, "errors_grammar_spelling", error_score / word_count)

    return max(subscore, 0)
