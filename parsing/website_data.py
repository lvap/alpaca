class WebsiteData:
    """Holds parsed website information.

    :param headline: article title
    :param text: main article text
    :param authors: article authors
    :param url: website URL
    """

    def __init__(self,
                 headline: str = "",
                 text: str = "",
                 authors: str = "",
                 url: str = ""):
        self.headline = headline
        self.text = text
        self.authors = authors
        self.url = url
