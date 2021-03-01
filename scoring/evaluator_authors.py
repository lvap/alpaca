from parsing.webpage_data import WebpageData


def evaluate_authors(data: WebpageData) -> float:
    """Evaluates credibility of the webpage by analysing the authors.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: 1 if the webpage specifies authors, 0 otherwise.
    """

    if data.authors is None or data.authors == [] or data.authors[0] == "":
        return 0.0
    return 1.0
