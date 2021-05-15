import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from logger import log
from parsing.webpage_data import WebpageData
from parsing.webpage_parser import has_ending_punctuation

# toggle some file-specific logging messages
LOGGING_ENABLED = True


def evaluate_polarity(data: WebpageData) -> float:
    """TODO documentation"""

    # TODO analyse which sentiment analysis tool works better as indicator of credibility, and remove the other (?)

    headline_ending = " " if has_ending_punctuation(data.headline) else ". "
    article = data.headline + headline_ending + data.text

    # sentiment analysis with spacy
    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe("spacytextblob")
    doc = nlp(article)
    polarity_spacy = doc._.polarity

    # sentiment analysis with vader
    polarity_vader = SentimentIntensityAnalyzer().polarity_scores(article)

    # for now we are only interested in the degree of polarity, not the direction
    score_spacy = abs(polarity_spacy)
    score_vader = abs(polarity_vader["compound"])

    combined_score = (score_vader + score_spacy) / 2

    log("[Sentiment] Article polarity: Average {:.3f} | SpaCy {:.3f} | VADER {}".format(
        combined_score, polarity_spacy, polarity_vader), LOGGING_ENABLED)

    # scale combined score in interval [0.5, 1]
    combined_score = (combined_score - 0.5) * 2
    return min(1 - combined_score, 1)


def evaluate_subjectivity(data: WebpageData) -> float:
    """TODO documentation"""

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe("spacytextblob")
    headline_ending = " " if has_ending_punctuation(data.headline) else ". "
    doc = nlp(data.headline + headline_ending + data.text)
    subjectivity = doc._.subjectivity

    log("[Sentiment] Article subjectivity: {:.3f}".format(subjectivity), LOGGING_ENABLED)

    return 1 - subjectivity
