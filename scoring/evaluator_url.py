import re
from urllib.parse import urlparse

from parsing.webpage_data import WebpageData
from parsing.webpage_parser import valid_address, get_real_url


def evaluate_domain_ending(data: WebpageData) -> float:
    """Evaluates whether the webpage URL's domain ending contains .org, .edu or .gov.

    Since .edu and .gov are often the second-level domain, we check for both top-level as well as second-level domains.

    :return: Returns 1 if the url is a valid http(s) address and the domain ending contains .org, .edu or .gov,
        0 otherwise.
    """

    if not valid_address(data.url):
        return 0

    url = get_real_url(data.url)
    domain = urlparse(url).hostname

    for ending in ["gov", "org", "edu"]:
        if re.search(r"\." + ending + r"(?:\.[a-z]+)?$", domain):
            return 1
    return 0
