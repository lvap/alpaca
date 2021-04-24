import traceback

import trafilatura
from newspaper import Article

from logger import log
from parsing.webpage_data import WebpageData

# toggle some file-specific logging messages
LOGGING_ENABLED = False

# parser used for text extraction from html data
PARSER = "trafilatura"


def parse_data(url: str) -> WebpageData:
    """Returns data necessary for credibility evaluation given a webpage's URL.
    Uses module specified in variable PARSER for text extraction.

    :param url: Location of the webpage that should be parsed.
    :return: The relevant data from the given webpage.
    """

    try:
        article = Article(url=url, language="en", fetch_images=False)
        article.download()
        article.parse()

        if article.html is None or article.html == "":
            log("[Parsing] Could not fetch webpage.")
            return WebpageData()

        # TODO language detection (abort if not english)

        if PARSER == "trafilatura":
            # TODO disable external logging?
            paragraphs = trafilatura.extract(article.html, include_comments=False,
                                             include_tables=False).split("\n")
        elif PARSER == "newspaper":
            paragraphs = article.text.split("\n")
        else:
            log("[Parsing] No text parser specified.")
            return WebpageData()

        # remove title if the text begins with it
        if paragraphs[0] == article.title:
            paragraphs.pop(0)
        # add period if article has subtitle without one
        if not has_ending_punctuation(paragraphs[0]):
            paragraphs[0] += "."

        # concatenate paragraphs, removing short parts that are likely not part of the actual text
        text = ""
        for pg in paragraphs:
            if len(pg) > 125 or (len(pg) > 40 and has_ending_punctuation(pg)):
                text += pg + "\n"

        log("[Parsing] Title: {}".format(article.title))
        log("[Parsing] Authors: {}".format(article.authors))
        log("[Parsing] Text length: {} symbols".format(len(text) - 1))
        log("[Parsing] Text: {}".format(text[:200] + " [...] " + text[-200:]).replace("\n", " "),
            not LOGGING_ENABLED)
        log("[Parsing] Full text: {}".format(text), LOGGING_ENABLED)

        # TODO maybe improve author(s) detection
        return WebpageData(article.html, article.title, text[:-1], article.authors, url)

    except Exception:
        traceback.print_exc()
        return WebpageData()


def has_ending_punctuation(text: str) -> bool:
    """Checks whether the text ending contains proper punctuation.
    Evaluates the last 3 characters of text to allow for parentheses and quotation marks.

    :param text: A string to check for ending punctuation.
    :return: True if the last three characters of text contain any of . ! ? : and False otherwise.
    """

    ending_punctuation = set(".!?:")
    if any((char in ending_punctuation) for char in text[-3:]):
        return True
    return False
