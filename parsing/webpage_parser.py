import io
import json
import logging
import re
from urllib.parse import urlparse

import trafilatura
from bs4 import BeautifulSoup
from newspaper import Article, ArticleException

from parsing.tokenize import sent_tokenize, word_tokenize
from parsing.webpage_data import WebpageData

logger = logging.getLogger("alpaca")


def has_ending_punctuation(text: str) -> bool:
    """Checks whether the text ending (last two characters) contains any of . ! ? :"""

    # evaluate the last 2 characters of text to allow for parentheses or quotation marks
    ending = re.sub("[“‟„”«»❝❞⹂〝〞〟＂‹›’❮❯‚‘‛❛❜❟]", "\"", text[-2:])
    return bool(re.search("[.!?:]$|[.!?][\")]|[\")][.!?:]", ending))


def valid_address(url: str) -> bool:
    """Returns True if the given string is a valid http or https URL, False otherwise."""

    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc, result.path]) and result.scheme in ["http", "https"]
    except ValueError:
        return False


def parse_data(url: str) -> WebpageData:
    """Extracts data necessary for credibility evaluation given a webpage's URL.

    Fetches HTML data, then parses article text, headline and author(s) from HTML.
    Additionally tokenizes article text into words and sentences. Webpage is assumed to be in English.
    """

    # download & parse article html, redirecting external logging to our own logger
    with io.StringIO() as buf:
        np_logger = logging.getLogger("article")
        propagate_state = np_logger.propagate
        np_logger.propagate = False
        buf_handler = logging.StreamHandler(buf)
        np_logger.addHandler(buf_handler)

        try:
            article = Article(url, language="en", fetch_images=False)
            article.download()
            article.parse()

        except ArticleException as err:
            logger.debug("[Parsing>Newspaper] " + str(err))
        finally:
            np_logger.removeHandler(buf_handler)
            np_logger.propagate = propagate_state
            for message in buf.getvalue().strip().split("\n"):
                if message:
                    logger.debug("[Parsing>Newspaper] " + message)

    if not article or not article.html:
        logger.error("[Parsing] Could not parse webpage html")
        return WebpageData()

    # parse article text
    text = _parse_text(article)
    if not text:
        logger.error("[Parsing] Could not parse webpage text")
        return WebpageData()

    # parse article authors
    authors = article.authors
    if not authors:
        authors = _extract_authors(article.html)

    # tokenize text
    sentences = sent_tokenize(text)
    words = word_tokenize(text)
    if not words or not sentences or len(words) <= 5:
        logger.error("[Parsing] Could not tokenize text")
        return WebpageData()

    logger.info("[Parsing] Title: {}".format(article.title))
    logger.info("[Parsing] Authors: {}".format(authors))
    logger.info("[Parsing] Text length: {} symbols, {} sentences".format(len(text), len(sentences)))
    logger.info("[Parsing] Text: {}".format(text[:200] + " [...] " + text[-200:]).replace("\n", " "))
    # logger.debug("[Parsing] Full text: {}".format(text))

    return WebpageData(article.html, article.title, text, authors, url, sentences, words)


def _parse_text(article: Article) -> str:
    """Parse text from an article. Conducts some basic text cleanup."""

    # parse text from html, redirecting external logging to our own logger
    with io.StringIO() as buf:
        traf_logger = logging.getLogger("trafilatura")
        propagate_state = traf_logger.propagate
        traf_logger.propagate = False
        buf_handler = logging.StreamHandler(buf)
        traf_logger.addHandler(buf_handler)
        parsed_text = trafilatura.extract(article.html, include_comments=False, include_tables=False)
        traf_logger.removeHandler(buf_handler)
        traf_logger.propagate = propagate_state
        for message in buf.getvalue().strip().split("\n"):
            if message:
                logger.debug("[Parsing>Trafilatura] " + message)

    parsed_text = parsed_text or article.text
    if not parsed_text:
        return ""

    # remove title if the text begins with it
    if parsed_text.startswith(article.title):
        parsed_text = parsed_text[len(article.title):]

    """
    for now it seems better to use all page text, even if some snippets may be irrelevant
    # concatenate paragraphs, removing short parts that are likely not part of the actual text
    text = ""
    for paragraph in parsed_text.split("\n"):
        if len(paragraph) > 25 or has_ending_punctuation(paragraph):
            text += paragraph + "\n"
    """

    return parsed_text.strip()


def _extract_authors(html: str) -> list[str]:
    """Extracts web article author(s) for specific html site structures."""

    authors = []
    soup = BeautifulSoup(html, "html.parser")

    # BBC.com
    if matches := soup.find("script", {"type": "application/ld+json"}):
        page_dict = json.loads("".join(matches.contents))
        if page_dict and type(page_dict) is dict:
            for key, value in page_dict.items():
                if key == "author" and value:
                    if type(value) is dict and value["name"]:
                        authors.append(value["name"])
                    elif type(value) is str:
                        authors.append(value)

    # theguardian.com
    for meta_author in soup.findAll("meta", attrs={"property": "article:author"}):
        if type(meta_author) is dict and meta_author["content"]:
            authors.append(meta_author["content"])
        elif type(meta_author) is str:
            authors.append(meta_author)

    if authors:
        logger.debug("[Parsing] {} additional author(s) detected: {}".format(len(authors), authors))
    return authors
