from urllib.parse import urlparse

from bs4 import BeautifulSoup

from logger import log
from parsing.webpage_data import WebpageData
from parsing.webpage_parser import valid_address

# toggle some file-specific logging messages
LOGGING_ENABLED = False

# modify external links score gradient given this threshold
LINKS_EXTERNAL_THRESHOLD = 3


def evaluate_links_external(data: WebpageData) -> float:
    """Evaluates webpage usage of external (site outbound) links.

    Returned score is linear from 0 external links (worst score => 0) to at least
    *LINKS_EXTERNAL_THRESHOLD* links (best score => 1).

    :return: 1 for high and 0 for low usage of external links."""

    local_domain = urlparse(data.url).hostname
    if local_domain.startswith("www."):
        local_domain = local_domain[4:]

    soup = BeautifulSoup(data.html, "html.parser")
    links = {}

    for link in soup.findAll('a'):
        link_url = link.get("href")

        if link.text and link_url not in links and valid_address(link_url):
            link_domain = urlparse(link_url).hostname
            if link_domain.startswith("www."):
                link_domain = link_domain[4:]

            # check whether url is external and link text appears in article text
            if (not local_domain.endswith(link_domain) and not link_domain.endswith(local_domain)
                    and link.text in data.text):
                links[link_url] = link.text

    log("[Links] External links: {} found".format(len(links)), not LOGGING_ENABLED)
    log("[Links] External links: {}".format(links), LOGGING_ENABLED)

    score = len(links) / LINKS_EXTERNAL_THRESHOLD
    return min(score, 1)
