from urllib.parse import urlparse

from parsing.webpage_data import WebpageData


def evaluate_domain_ending(data: WebpageData) -> float:
    """Evaluates the webpage URL's domain ending. Returns 1 if the domain ending is .org, .edu or .gov, 0 otherwise."""

    domain_ending = urlparse(data.url).hostname.split(".")[-1]

    if any(ending in domain_ending for ending in ["gov", "org", "edu"]):
        return 1
    return 0
