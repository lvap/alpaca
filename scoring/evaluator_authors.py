from parsing.webpage_data import WebpageData


def evaluate_authors(data: WebpageData) -> float:
    """Verifies whether the webpage specifies one or more authors. Returns 1 if it does, 0 otherwise."""

    if not data.authors or all((author == "") for author in data.authors):
        return 0
    return 1
