import traceback

import trafilatura
from newspaper import Article

from parsing.website_data import WebsiteData

PARSER = "trafilatura"


def parse_data(url: str) -> WebsiteData:
    """Returns data necessary for credibility evaluation given a webpage's URL.
    Uses module specified in PARSER for text extraction.

    :param url: Location of the website that should be parsed.
    :return: The relevant data from the given website.
    """

    global PARSER

    try:
        article = Article(url=url, language="en", fetch_images=False)
        article.download()
        article.parse()

        if article.html is None or article.html == "":
            print("*** Could not fetch webpage.")
            return WebsiteData()

        if PARSER == "trafilatura":
            paragraphs = trafilatura.extract(article.html, target_language="en", include_comments=False,
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
        # and adding full stops when a paragraph ends without one (likely sub titles or non-article text)
        text = ""
        for pg in paragraphs:
            if len(pg) > 50:
                text += pg
                text += ". " if pg[len(pg) - 1] not in [".", ";", "!", "?", ":", "”", "\"", "\'"] else " "

        # debug/logging prints
        print("*** Title: {}".format(article.title))
        print("*** Authors: {}".format(article.authors))
        print("*** Text: {}".format(text[:200] + " [...] " + text[-200:]))

        return WebsiteData(article.title, text, article.authors != [""], url)

    except Exception:
        traceback.print_exc()
        return WebsiteData()
