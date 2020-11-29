class WebsiteData:
    def __init__(self, headline: str = "", text: str = "", author_stated: bool = False, url: str = ""):
        self.headline = headline
        self.text = text
        self.author_stated = author_stated
        self.url = url
