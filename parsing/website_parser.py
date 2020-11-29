import requests

from parsing.website_data import WebsiteData


def parse_data(url: str) -> WebsiteData:
    """
    Extracts necessary website data for credibility evaluation given a URL.

    :param url: Location of the website that should be parsed.
    :return: The relevant data from the given website.
    """
    try:
        get = requests.head(url)
        if get.status_code >= 400:
            print(get)
        return WebsiteData("", "", False, "")
    except ConnectionError:
        print("Cannot connect to website.")
