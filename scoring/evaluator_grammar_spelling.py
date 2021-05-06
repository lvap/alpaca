import re

import language_tool_python as ltp

from logger import log
from parsing.webpage_data import WebpageData

# toggle some file-specific logging messages
LOGGING_ENABLED = False

# modify grammar/spelling error score gradient given this upper limit
ERROR_LIMIT = 0.2


def evaluate_grammar_spelling(data: WebpageData) -> float:
    """Evaluates a webpage's language correctness.

    Determines how many spelling or grammar errors were encountered on the page and scales this value
    by overall word count. Specifically, the returned score is linear from 0 errors per word (no errors,
    best score => 1) to *ERRORS_LIMIT* errors per word (large amount of errors, worst score => 0).

    :return: Value between 0 (large amount of errors) and 1 (no errors).
    """

    tool = ltp.LanguageTool("en-US")

    matches = tool.check(data.headline)
    matches_to_ignore = 0
    # ignore error for missing punctuation at title ending
    if matches and matches[len(matches) - 1].ruleId == "PUNCTUATION_PARAGRAPH_END":
        matches_to_ignore += 1
        matches.pop()
    matches += tool.check(data.text)

    # filter out irrelevant matches and penalise unknown words as possible errors only once (might be names)
    unknown_words = []
    for match in matches:
        if (match.ruleId in ["EN_QUOTES", "DASH_RULE", "EXTREME_ADJECTIVES"]
                or match.category == "REDUNDANCY"
                or "is British English" in match.message):
            matches_to_ignore += 1
        elif " " not in match.matchedText:
            if match.matchedText in unknown_words:
                matches_to_ignore += 1
            else:
                log(match, LOGGING_ENABLED)
                unknown_words.append(match.matchedText)
        else:
            log(match, LOGGING_ENABLED)

    error_score = len(matches) - matches_to_ignore
    # words = strings bounded by whitespaces + 1, excluding strings consisting of a single non-alphanumeric character
    word_count = data.headline.count(" ") + data.text.count(" ") + 2 - (len(re.findall(r"\s\W\s", data.headline))
                                                                        + len(re.findall(r"\s\W\s", data.text)))
    error_score = 1 - (error_score / (word_count * ERROR_LIMIT))

    log("[Grammar/Spelling] {} errors in {} words ({} errors ignored), {:.3f} errors per word"
        .format(len(matches) - matches_to_ignore, word_count, matches_to_ignore, error_score / word_count))

    return max(error_score, 0)
