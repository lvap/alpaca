import re

from parsing.webpage_data import WebpageData


def evaluate_domain_ending(data: WebpageData) -> float:
    """Evaluates the webpage URL's domain ending. Returns 1 if the domain ending is .org or .gov, 0 otherwise."""

    if re.search(r"\.gov[./]", data.url) or re.search(r"\.org[./]", data.url) or re.search(r"\.edu[./]", data.url):
        return 1
    return 0
