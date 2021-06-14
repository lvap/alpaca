from urllib.parse import urlparse

from parsing.webpage_data import WebpageData


def evaluate_authors(data: WebpageData) -> float:
    """Verifies whether the webpage specifies one or more authors. Returns 1 if it does, 0 otherwise."""

    for author in data.authors:
        # check whether author contains at least one letter and isn't just the site address or URL
        if (any(letter.isalpha() for letter in author) and "www." not in author and "http" not in author
                and urlparse(data.url).hostname not in author):
            return 1
    return 0
