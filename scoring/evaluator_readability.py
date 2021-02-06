from nltk.tokenize import sent_tokenize
import readability

from logger import log
from parsing.website_data import WebsiteData
from parsing.website_parser import has_ending_punctuation


def evaluate_readability(data: WebsiteData) -> float:
    """Evaluates readability of the website's text. TODO further documentation

    :param data: Parsed website data necessary for credibility evaluation.
    :return: TODO.
    """

    headline_period = "" if has_ending_punctuation(data.headline) else ". "
    full_text = (data.headline + headline_period + data.text).replace("\n", " ")
    tokens = sent_tokenize(full_text)
    log("*** Tokenisation: {} sentences".format(len(tokens)))

    # readability_results = readability.getmeasures(tokens, lang="en")
    # log(readability_results)
    return 1.0
