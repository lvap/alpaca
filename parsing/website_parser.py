import traceback

import trafilatura
from newspaper import Article

from parsing.website_data import WebsiteData


def parse_data(url: str) -> WebsiteData:
    """Returns necessary website data for credibility evaluation given a URL.

    :param url: Location of the website that should be parsed.
    :return: The relevant data from the given website.
    """

    return _parse_using_trafilatura(url)


def _parse_using_trafilatura(url: str) -> WebsiteData:
    """Extracts necessary website data for credibility evaluation using trafilatura for text extraction.

        :param url: Location of the website that should be parsed.
        :return: The relevant data from the given website.
        """

    try:
        article = Article(url=url, language="en", fetch_images=False)
        article.download()
        article.parse()

        page = trafilatura.fetch_url(url)
        if page is None:
            print("*** Could not fetch webpage.")
            return WebsiteData()

        paragraphs = trafilatura.extract(page, target_language="en", include_comments=False,
                                         include_tables=False).split("\n")

        # remove title if the text begins with it
        if paragraphs[0] == article.title:
            paragraphs.pop(0)

        # add full stop after subtitle
        if paragraphs[0][len(paragraphs[0])-1] not in [".", "!", "?", ":", "”", "\"", "\'"]:
            paragraphs[0] += "."

        # remove short strings that are likely not part of the main text
        text = ""
        for pg in paragraphs:
            if len(pg) > 40:
                text += pg + " "

        print("*** Title: {}".format(article.title))
        print("*** Authors: {}".format(article.authors))
        print("\n*** Text: {}\n".format(text))

        return WebsiteData(article.title, text, article.authors != [""], url)

    except Exception:
        traceback.print_exc()
        return WebsiteData()


def _parse_using_newspaper(url: str) -> WebsiteData:
    """Extracts necessary website data for credibility evaluation using newspaper for text extraction.

        :param url: Location of the website that should be parsed.
        :return: The relevant data from the given website.
        """

    try:
        article = Article(url=url, language="en", fetch_images=False)
        article.download()
        article.parse()

        paragraphs = article.text.split("\n")

        # remove title if the text begins with it
        if paragraphs[0] == article.title:
            paragraphs.pop(0)

        # add full stop for article subtitle
        if paragraphs[0][len(paragraphs[0]) - 1] not in [".", "!", "?", ":", "”", "\"", "\'"]:
            paragraphs[0] += "."

        # remove short strings that are likely not part of the main text
        text = ""
        for pg in paragraphs:
            if len(pg) > 60:
                text += pg + " "

        print("*** Title: {}".format(article.title))
        print("*** Authors: {}".format(article.authors))
        print("\n*** Text: {}\n".format(text))

        return WebsiteData(article.title, text, article.authors != [""], url)

    except Exception:
        traceback.print_exc()
        return WebsiteData()
