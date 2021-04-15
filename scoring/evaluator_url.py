from parsing.webpage_data import WebpageData
import re


def evaluate_domain_ending(data: WebpageData) -> float:
    """Evaluates the webpage URL's domain ending.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 if the domain ending is .org or .gov, 0 otherwise.
    """

    if re.search(r"\.gov[./]", data.url) is not None:
        return 1
    if re.search(r"\.org[./]", data.url) is not None:
        return 1
    return 0
