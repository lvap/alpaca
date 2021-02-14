import re

import language_tool_python as ltp

from logger import log
from parsing.website_data import WebsiteData

# toggle some file-specific logging messages
LOGGING_ENABLED = False


def evaluate_grammar(data: WebsiteData) -> float:
    """Evaluates credibility of the webpage by analysing the headline's and text body's language correctness.

    :param data: Parsed website data necessary for credibility evaluation.
    :return: Value between 0 and 1 to represent how many spelling or grammar errors were encountered on the page,
        scaled to overall word count. Specifically, the returned score is max(1 - average errors per word, 0).
        1 means no errors, 0 means at least as many errors as words.
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
    # words = strings bounded by whitespaces, excluding strings consisting of a single non-alphanumeric character
    word_count = len(data.headline.split()) + len(data.text.split()) - (len(re.findall(r"\s\W\s", data.headline))
                                                                        + len(re.findall(r"\s\W\s", data.text)))
    error_score = 1.0 - (error_score / word_count)

    log("*** {} errors in {} words ({} errors ignored)"
        .format(len(matches) - matches_to_ignore, word_count, matches_to_ignore))

    return error_score if error_score >= 0.0 else 0.0
