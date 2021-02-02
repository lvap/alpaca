import traceback

import trafilatura
from newspaper import Article

from parsing.website_data import WebsiteData

PARSER = "trafilatura"


def parse_data(url: str) -> WebsiteData:
    """Returns data necessary for credibility evaluation given a webpage's URL.
    Uses module specified in variable PARSER for text extraction.

    :param url: Location of the website that should be parsed.
    :return: The relevant data from the given website.
    """

    try:
        article = Article(url=url, language="en", fetch_images=False)
        article.download()
        article.parse()

        if article.html is None or article.html == "":
            print("*** Could not fetch webpage.")
            return WebsiteData()

        # TODO language detection (abort if not english)

        if PARSER == "trafilatura":
            paragraphs = trafilatura.extract(article.html, include_comments=False,
                                             include_tables=False).split("\n")
        elif PARSER == "newspaper":
            paragraphs = article.text.split("\n")
        else:
            print("*** No text parser specified.")
            return WebsiteData()

        # remove title if the text begins with it
        if paragraphs[0] == article.title:
            paragraphs.pop(0)

        # concatenate paragraphs, removing short strings that are likely not part of the main text
        text = ""
        for pg in paragraphs:
            if len(pg) > 50:
                text += pg + " "

        print("*** Title: {}".format(article.title))
        print("*** Authors: {}".format(article.authors))
        print("*** Text: {}".format(text[:200] + " [...] " + text[-200:]))

        return WebsiteData(article.html, article.title, text, article.authors, url)

    except Exception:
        traceback.print_exc()
        return WebsiteData()
