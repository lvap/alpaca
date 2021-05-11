import spacy
from spacytextblob.spacytextblob import SpacyTextBlob

from logger import log
from parsing.webpage_data import WebpageData

# toggle some file-specific logging messages
LOGGING_ENABLED = True


def evaluate_polarity(data: WebpageData) -> float:
    """TODO documentation"""

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe("spacytextblob")
    doc = nlp(data.text)
    polarity = doc._.polarity

    log("[Sentiment] Text polarity: {}".format(polarity), LOGGING_ENABLED)

    # we are interested in the degree of polarity, not the direction
    if polarity < 0:
        polarity *= -1

    score = (polarity - 0.5) * 2
    return min(1 - score, 1)


def evaluate_subjectivity(data: WebpageData) -> float:
    """TODO documentation"""

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe("spacytextblob")
    doc = nlp(data.text)
    subjectivity = doc._.subjectivity

    log("[Sentiment] Text subjectivity: {}".format(subjectivity), LOGGING_ENABLED)

    return 1 - subjectivity
