import logging
from urllib.parse import urlparse

from bs4 import BeautifulSoup

import stats_collector
from parsing.webpage_data import WebpageData
from parsing.webpage_parser import valid_address, get_real_url

# upper limit for subscore
LINKS_LIMIT = 3

# boundary check
if LINKS_LIMIT < 1:
    raise ValueError("LINKS_EXTRERNAL_THRESHOLD must be equal or greater than 1")

logger = logging.getLogger("alpaca")


def evaluate_links_external(data: WebpageData) -> float:
    """Evaluates webpage usage of external (site outbound) links.

    Returned score is linear from 0 external links (worst score => 0) to at least **LINKS_LIMIT** external links
    (best score => 1). Returns 0 if data.url is not a valid http(s) URL or data.html is empty.

    :return: 1 for high and 0 for low usage of external links.
    """

    if not valid_address(data.url) or not data.html:
        stats_collector.add_result(data.url, "links_count", -10)
        return 0

    url = get_real_url(data.url)
    local_domain = urlparse(url).hostname
    if local_domain.startswith("www."):
        local_domain = local_domain[4:]

    soup = BeautifulSoup(data.html, "html.parser")
    links = {}

    for link in soup.findAll('a'):
        link_url = get_real_url(link.get("href"))

        if link.text and link_url not in links and valid_address(link_url):
            link_domain = urlparse(link_url).hostname
            if link_domain.startswith("www."):
                link_domain = link_domain[4:]

            # check whether url is external and link text appears in article text
            if (not local_domain == link_domain and not local_domain.endswith("." + link_domain)
                    and not link_domain.endswith("." + local_domain) and link.text in data.text):
                links[link_url] = link.text

    logger.debug("[Links] {} external links: {}".format(len(links), links))
    stats_collector.add_result(data.url, "links_count", len(links))

    score = len(links) / LINKS_LIMIT
    return min(score, 1)
