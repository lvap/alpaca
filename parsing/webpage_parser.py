import io
import json
import logging
from urllib.parse import urlparse

import trafilatura
from bs4 import BeautifulSoup
from newspaper import Article

from logger import log
from parsing.webpage_data import WebpageData

# toggle some file-specific logging messages
LOGGING_ENABLED = False

# parser used for text extraction from html data
PARSER = "trafilatura"


def parse_data(url: str) -> WebpageData:
    """Extracts data necessary for credibility evaluation given a webpage's URL.

    Fetches HTML data, then parses article text, headline and author(s) from HTML.
    Uses module specified in *PARSER* for text extraction. Webpage is assumed to be in English.
    """

    article = Article(url, language="en", fetch_images=False)
    article.download()
    article.parse()

    if not article.html:
        log("[Parsing] Could not parse webpage html")
        return WebpageData()

    text = _parse_text(article)

    if not text:
        log("[Parsing] Could not parse webpage text")
        return WebpageData()

    authors = article.authors
    if not authors:
        authors = extract_authors(article.html)

    log("[Parsing] Title: {}".format(article.title))
    log("[Parsing] Authors: {}".format(authors))
    log("[Parsing] Text length: {} symbols".format(len(text) - 1))
    log("[Parsing] Text: {}".format(text[:200] + " [...] " + text[-200:]).replace("\n", " "), not LOGGING_ENABLED)
    log("[Parsing] Full text: {}".format(text), LOGGING_ENABLED)

    return WebpageData(article.html, article.title, text[:-1], authors, url)


def _parse_text(article: Article) -> str:
    """Parse text from an article using parser *PARSER*. Conducts some basic text cleanup.

    :raise ValueError: If the text parser is unspecified or not recognised.
    """

    if PARSER == "trafilatura":
        # redirect external logging to our own logger
        ext_logger = logging.getLogger("trafilatura")
        logger_state = ext_logger.propagate
        ext_logger.propagate = False
        buf = io.StringIO()
        buf_handler = logging.StreamHandler(buf)
        ext_logger.addHandler(buf_handler)
        text = trafilatura.extract(article.html, include_comments=False, target_language="en", include_tables=False)
        for message in buf.getvalue().strip().split("\n"):
            log("[Trafilatura] " + message, LOGGING_ENABLED and message)
        ext_logger.propagate = logger_state

    elif PARSER == "newspaper":
        text = article.text
    else:
        raise ValueError("No text parser specified")

    if text:
        paragraphs = text.split("\n")
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

    return text


def has_ending_punctuation(text: str) -> bool:
    """Checks whether the text ending (last three characters) contains any of . ! ? :"""

    ending_punctuation = set(".!?:")
    # evaluate the last 3 characters of text to allow for parentheses and quotation marks
    return any((char in ending_punctuation) for char in text[-3:])


def valid_address(user_input: str) -> bool:
    """Returns True if the given string is a valid http or https URL, False otherwise."""

    try:
        result = urlparse(user_input)
        return all([result.scheme, result.netloc, result.path]) and result.scheme in ["http", "https"]
    except ValueError:
        return False


def extract_authors(html: str) -> list[str]:
    """Extracts web article author(s) for specific html site structures."""

    authors = []
    soup = BeautifulSoup(html, "html.parser")

    # BBC.com
    if matches := soup.find("script", {"type": "application/ld+json"}):
        page_dict = json.loads("".join(matches.contents))
        if page_dict and type(page_dict) is dict:
            authors.extend(
                [value.get("name") for (key, value) in page_dict.items() if key == "author" and value.get("name")])

    # theguardian.com
    authors.extend(
        [meta_author.get("content") for meta_author in soup.findAll("meta", attrs={"property": "article:author"})
         if meta_author.get("content")])

    log("[Parsing] {} additional author(s) detected".format(len(authors)), LOGGING_ENABLED and authors)
    return authors
