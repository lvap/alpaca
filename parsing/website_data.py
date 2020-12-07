class WebsiteData:
    """Holds parsed website information.

    :param headline: article title
    :param text: main article text
    :param links: links contained in the main text body
    :param has_author: whether the site specifies an author
    :param url: website URL
    """
    def __init__(self,
                 headline: str = "",
                 text: str = "",
                 links: list[str] = [""],
                 has_author: bool = False,
                 url: str = ""):
        self.headline = headline
        self.text = text
        self.links = links
        self.has_author = has_author
        self.url = url
