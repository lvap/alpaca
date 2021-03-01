class WebpageData:
    """Holds parsed webpage information.

    :param html: The complete webpage as html object.
    :param headline: The article/page title.
    :param text: The webpage's main text body.
    :param authors: The article authors.
    :param url: The webpage's URL.
    """

    def __init__(self,
                 html: str = "",
                 headline: str = "",
                 text: str = "",
                 authors: list[str] = [],
                 url: str = ""):
        self.html = html
        self.headline = headline
        self.text = text
        self.authors = authors
        self.url = url
