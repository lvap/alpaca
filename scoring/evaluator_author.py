from urllib.parse import urlparse

from parsing.webpage_data import WebpageData
from parsing.webpage_parser import valid_address


def evaluate_author(data: WebpageData) -> float:
    """Verifies whether the webpage specifies one or more authors. Returns 1 if it does, 0 otherwise."""

    host = urlparse(data.url).hostname if valid_address(data.url) else ""
    for author in data.authors:
        # check whether author contains at least one letter and isn't just the site address or URL
        if (any(letter.isalpha() for letter in author) and "www." not in author and "http" not in author
                and not (host and host in author)):
            return 1
    return 0
