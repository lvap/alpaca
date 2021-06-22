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


def get_real_url(url: str) -> str:
    """Extracts the real URL if using an archived webpage via web.archive.org, else returns input URL."""

    if not valid_address(url):
        return ""

    if match := re.search(r"https?://web\.archive\.org/web/\d+/", url):
        if valid_address(url[match.end():]):
            return url[match.end():]

    return url


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

    paragraphs = parsed_text.split("\n")
    text = ""
    # remove title if the text begins with it
    if paragraphs[0] == article.title:
        paragraphs.pop(0)
    # concatenate paragraphs, removing those without a single alphanumeric character
    for paragraph in paragraphs:
        if any(char.isalnum() for char in paragraph):
            text += paragraph + "\n"

    return text.strip()


def _extract_authors(html: str) -> list[str]:
    """Extracts web article author(s) for specific html site structures."""

    authors = []
    soup = BeautifulSoup(html, "html.parser")

    for match in soup.findAll("script", type="application/ld+json"):
        try:
            page_dict = json.loads("".join(match.contents))
            if page_dict and type(page_dict) is dict:

                # BBC.com (e.g. https://www.bbc.com/news/world-asia-57516630)
                if "author" in page_dict:
                    author_dict = page_dict["author"]
                    if (author_dict and type(author_dict) is dict and "name" in author_dict
                            and not ("@type" in author_dict and author_dict["@type"] != "Person")):
                        authors.append(author_dict["name"])

                # snopes.com (e.g.http://www.snopes.com/politics/obama/photos/kenyasign.asp)
                elif "@graph" in page_dict and type(page_dict["@graph"]) is list:
                    for graph_dict in page_dict["@graph"]:
                        if (type(graph_dict) is dict and "@type" in graph_dict and graph_dict["@type"] == "Person"
                                and "name" in graph_dict):
                            authors.append(graph_dict["name"])
                            break

        except json.JSONDecodeError as err:
            logger.debug("[Parsing>json] " + str(err))

    # theguardian.com
    for meta_author in soup.findAll("meta", property="article:author"):
        if meta_author.has_attr("content"):
            authors.append(meta_author["content"])

    if authors:
        logger.debug("[Parsing] {} additional author(s) detected: {}".format(len(authors), authors))
    return authors
