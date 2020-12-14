from parsing.website_data import WebsiteData


def evaluate_authors(data: WebsiteData) -> float:
    """Evaluates credibility of the webpage by analysing the authors.

    :param data: Parsed website data necessary for credibility evaluation.
    :return: 1 if the website specifies authors, 0 otherwise.
    """

    if data.authors is None or data.authors == [] or data.authors[0] == "":
        return 0.0
    return 1.0
