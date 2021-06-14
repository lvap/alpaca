import re
from urllib.parse import urlparse

from parsing.webpage_data import WebpageData


def evaluate_domain_ending(data: WebpageData) -> float:
    """Evaluates the webpage URL's domain ending (top-level or second-level domain).
    Returns 1 if the domain ending is .org, .edu or .gov, 0 otherwise."""

    domain_ending = urlparse(data.url).hostname

    for ending in ["gov", "org", "edu"]:
        if re.search(r"\." + ending + r"(?:\.[a-z]+)?$", domain_ending):
            return 1
    return 0
