import io
import json
import logging
import re
from urllib.parse import urlparse

import trafilatura
from bs4 import BeautifulSoup
from newspaper import Article
from nltk import sent_tokenize

from parsing.webpage_data import WebpageData

# parser used for text extraction from html data
PARSER = "trafilatura"

logger = logging.getLogger("alpaca")


def parse_data(url: str) -> WebpageData:
    """Extracts data necessary for credibility evaluation given a webpage's URL.

    Fetches HTML data, then parses article text, headline and author(s) from HTML.
    Uses module specified in *PARSER* for text extraction. Webpage is assumed to be in English.
    """

    article = Article(url, language="en", fetch_images=False)
    article.download()
    article.parse()
    if not article.html:
        logger.error("[Parsing] Could not parse webpage html")
        return WebpageData()

    text = _parse_text(article)
    if not text:
        logger.error("[Parsing] Could not parse webpage text")
        return WebpageData()

    authors = article.authors
    if not authors:
        authors = _extract_authors(article.html)

    # tokenize text into list of sentences
    # replace symbols that are problematic for nltk.tokenize
    tokenized_text = sent_tokenize(re.sub("[“‟„”«»❝❞⹂〝〞〟＂]", "\"", re.sub("[‹›’❮❯‚‘‛❛❜❟]", "'", text)))
    if not tokenized_text or len(tokenized_text) < 1:
        logger.error("[Parsing] Could not tokenize text")
        return WebpageData()

    logger.info("[Parsing] Title: {}".format(article.title))
    logger.info("[Parsing] Authors: {}".format(authors))
    logger.info("[Parsing] Text length: {} symbols, {} sentences".format(len(text) - 1, len(tokenized_text)))
    logger.info("[Parsing] Text: {}".format(text[:200] + " [...] " + text[-200:-1]).replace("\n", " "))
    # logger.debug("[Parsing] Full text: {}".format(text[:-1]))

    return WebpageData(article.html, article.title, text[:-1], authors, url, tokenized_text)


def _parse_text(article: Article) -> str:
    """Parse text from an article using parser *PARSER*. Conducts some basic text cleanup.

    :raise ValueError: If the text parser is unspecified or not recognised.
    """

    if PARSER == "trafilatura":
        # redirect external logging to our own logger
        with io.StringIO() as buf:
            traf_logger = logging.getLogger("trafilatura")
            propagate_state = traf_logger.propagate
            traf_logger.propagate = False
            buf_handler = logging.StreamHandler(buf)
            traf_logger.addHandler(buf_handler)
            text = trafilatura.extract(article.html, include_comments=False, target_language="en", include_tables=False)
            traf_logger.removeHandler(buf_handler)
            traf_logger.propagate = propagate_state
            for message in buf.getvalue().strip().split("\n"):
                if message:
                    logger.debug("[Parsing>Trafilatura] " + message)

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


def _extract_authors(html: str) -> list[str]:
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

    if authors:
        logger.debug("[Parsing] {} additional author(s) detected: {}".format(len(authors), authors))
    return authors


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
