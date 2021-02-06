import traceback

import trafilatura
from newspaper import Article

from parsing.website_data import WebsiteData
from logger import log

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
            log("*** Could not fetch webpage.")
            return WebsiteData()

        # TODO language detection (abort if not english)

        if PARSER == "trafilatura":
            paragraphs = trafilatura.extract(article.html, include_comments=False,
                                             include_tables=False).split("\n")
        elif PARSER == "newspaper":
            paragraphs = article.text.split("\n")
        else:
            log("*** No text parser specified.")
            return WebsiteData()

        # remove title if the text begins with it
        if paragraphs[0] == article.title:
            paragraphs.pop(0)
        # add period if article has subtitle without one
        if not has_ending_punctuation(paragraphs[0]):
            paragraphs[0] += "."

        # concatenate paragraphs, removing short parts that are likely not part of the actual text
        text = ""
        for pg in paragraphs:
            if len(pg) > 150 or (len(pg) > 50 and has_ending_punctuation(pg)):
                text += pg + "\n"

        log("*** Title: {}".format(article.title))
        log("*** Authors: {}".format(article.authors))
        log("*** Text: {}".format(text[:200] + " [...] " + text[-200:]).replace("\n", " "))
        log("*** Text length: {}".format(len(text)))

        return WebsiteData(article.html, article.title, text[:-1], article.authors, url)

    except Exception:
        traceback.print_exc()
        return WebsiteData()


def has_ending_punctuation(text: str) -> bool:
    """ Checks whether the text ending contains proper punctuation.
    Evaluates the last 3 characters of text to allow for parentheses and quotation marks.

    :param text: A string to check for ending punctuation.
    :return: True if the last three characters of text contain any of . ! ? : and False otherwise.
    """

    ending_punctuation = set(".!?:")
    if any((char in ending_punctuation) for char in text[-3:]):
        return True
    return False
