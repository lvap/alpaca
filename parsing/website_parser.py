import requests
from bs4 import BeautifulSoup

from parsing.website_data import WebsiteData


def parse_data(url: str) -> WebsiteData:
    """Extracts necessary website data for credibility evaluation given a URL.

    :param url: Location of the website that should be parsed.
    :return: The relevant data from the given website.
    """

    try:
        page = requests.get(url)
        print("*** Request code: {}".format(page.status_code))
        soup = BeautifulSoup(page.content, "html.parser")

        title = soup.title.text
        print("*** Page title: {}".format(title))

        text = page.text
        print("*** some_html")

        return WebsiteData(title, text, [""], False, url)

    except ConnectionError:
        print("Cannot connect to website.")
