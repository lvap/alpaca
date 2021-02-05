import language_tool_python as ltp

from parsing.website_data import WebsiteData


def evaluate_grammar(data: WebsiteData) -> float:
    """Evaluates credibility of the webpage by analysing the headline's and text body's language correctness.

    :param data: Parsed website data necessary for credibility evaluation.
    :return: Value between 0 and 1 to represent how many spelling or grammar errors were encountered on the page,
        scaled to overall word count. 1 means no errors, 0 means at least as many errors as words.
    """

    tool = ltp.LanguageTool("en-US")

    matches = tool.check(data.headline)
    matches += tool.check(data.text)

    unknown_words = []

    # filter out irrelevant errors
    errors_to_ignore = 0
    for match in matches:
        if (match.ruleId in ["EN_QUOTES", "DASH_RULE"]      # ignore use of improper quote or dash punctuation
                or match.category == "REDUNDANCY"           # ignore redundancy style warnings
                or "is British English" in match.message):  # ignore errors for British spelling
            errors_to_ignore += 1
        elif match.ruleIssueType == "misspelling":
            # only penalise unknown words as possible errors once (might be names)
            if match.matchedText in unknown_words:
                errors_to_ignore += 1
            else:
                unknown_words.append(match.matchedText)
                print(match)
        else:
            print(match)

    error_score = len(matches) - errors_to_ignore
    word_count = len(data.headline.split()) + len(data.text.split())
    # error score is 1 - (average errors per word)
    error_score = 1.0 - (error_score / word_count)

    print("*** grammar eval: {} errors ({} ignored) in {} words"
          .format(len(matches) - errors_to_ignore, errors_to_ignore, word_count))

    return error_score if error_score >= 0.0 else 0.0
