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

        text = ""
        page = trafilatura.fetch_url(url)
        paragraphs = trafilatura.extract(page, target_language="en", include_comments=False,
                                         include_tables=False).split("\n")
        for pg in paragraphs:
            if len(pg) > 25:
                text += pg + " "

        print("*** Title: {}".format(article.title))
        print("*** Authors: {}".format(article.authors))
        print("\n*** Text: {}\n".format(text))

        return WebsiteData(article.title, text, [], article.authors != [""], url)

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

        text = ""
        paragraphs = article.text.split("\n")
        for pg in paragraphs:
            if len(pg) > 25:
                text += pg + " "

        print("*** Title: {}".format(article.title))
        print("*** Authors: {}".format(article.authors))
        print("\n*** Text: {}\n".format(text))

        return WebsiteData(article.title, text, [], article.authors != [""], url)

    except Exception:
        traceback.print_exc()
        return WebsiteData()
