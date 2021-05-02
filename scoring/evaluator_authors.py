from urllib.parse import urlparse

from parsing.webpage_data import WebpageData
from parsing.webpage_parser import valid_address


def evaluate_authors(data: WebpageData) -> float:
    """Verifies whether the webpage specifies one or more authors. Returns 1 if it does, 0 otherwise."""

    for author in data.authors:
        # check whether author contains at least one letter and isn't just the site address or a URL
        if (any(letter.isalpha() for letter in author) and not urlparse(data.url).hostname.endswith(author)
                and not valid_address(author)):
            return 1
    return 0
