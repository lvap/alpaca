import language_tool_python as ltp

from parsing.website_data import WebsiteData


def evaluate_grammar(data: WebsiteData) -> float:
    """Evaluates credibility of the webpage by analysing the headline's and text body's language correctness.

    :param data: Parsed website data necessary for credibility evaluation.
    :return: Value between 0 and 1 to represent how many spelling or grammar errors were encountered on the page,
        scaled to overall word count. 1 means no errors, 0 means at least as many errors as words.
    """

    tool = ltp.LanguageTool("en-US")

    errors = tool.check(data.headline)
    errors += tool.check(data.text)

    # filter out irrelevant errors
    errors_to_ignore = 0
    for match in errors:
        if (match.ruleId in ["EN_QUOTES", "DASH_RULE"]      # ignore use of improper quote or dash punctuation
                or match.category == "REDUNDANCY"           # ignore redundancy style warnings
                or "is British English" in match.message):  # ignore "misspelled" words in British English
            errors_to_ignore += 1
        print(match)  # debug

    error_score = len(errors) - errors_to_ignore
    word_count = len(data.headline.split()) + len(data.text.split())
    error_score = 1.0 - (error_score / word_count)

    print("*** grammar eval: {} errors ({} ignored) in {} words"
          .format(len(errors) - errors_to_ignore, errors_to_ignore, word_count))

    return error_score if error_score >= 0.0 else 0.0
