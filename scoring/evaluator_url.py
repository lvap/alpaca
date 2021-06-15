import re
from urllib.parse import urlparse

from parsing.webpage_data import WebpageData
from parsing.webpage_parser import valid_address


def evaluate_domain_ending(data: WebpageData) -> float:
    """Evaluates whether the webpage URL's domain ending contains .org, .edu or .gov.

    Since .edu and .gov are often the second-level domain, we check for both top-level as well as second-level domains.

    :return: Returns 1 if the domain ending contains .org, .edu or .gov, 0 otherwise."""

    if not valid_address(data.url):
        return 0

    domain_ending = urlparse(data.url).hostname

    for ending in ["gov", "org", "edu"]:
        if re.search(r"\." + ending + r"(?:\.[a-z]+)?$", domain_ending):
            return 1
    return 0
