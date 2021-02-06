from nltk.tokenize import sent_tokenize

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
    # TODO poor tokenization for quotation marks at end of sentences. use syntok?
    tokens = sent_tokenize(full_text)
    log("*** Tokenisation: {} sentences".format(len(tokens)))

    return 1.0
