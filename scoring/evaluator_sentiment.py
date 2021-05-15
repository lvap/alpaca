import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from logger import log
from parsing.webpage_data import WebpageData
from parsing.webpage_parser import has_ending_punctuation

# toggle some file-specific logging messages
LOGGING_ENABLED = True

# lower limit for polarity (upper limit is 1)
POLARITY_MINIMUM = 0.5


def evaluate_polarity(data: WebpageData) -> float:
    """Evaluates the polarity of the webpage through sentiment analysis.

    Performs sentiment analysis to determine a webpage's positivity/negativity score between -1 and 1, then looks at the
    absolute value as indicator of "extremism"/"emotionality". Final score is linear from 0 (absolute polarity is 1)
    to 1 (absolute polarity is below *POLARITY_MINIMUM*). Uses average of spaCy and VADER sentiment analysis.

    :return: Value between 0 (extreme polarity) and 1 (relatively low polarity).
    """

    # TODO decide on the better-performing sentiment analysis tool as indicator of credibility

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
    combined_score = (combined_score - POLARITY_MINIMUM) / POLARITY_MINIMUM
    return min(1 - combined_score, 1)


def evaluate_subjectivity(data: WebpageData) -> float:
    """Evaluates the subjectivity of the webpage using spaCy.

    :return: Value between 0 (very high webpage subjectivity) and 1 (very low webpage subjectivity).
    """

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe("spacytextblob")
    headline_ending = " " if has_ending_punctuation(data.headline) else ". "
    doc = nlp(data.headline + headline_ending + data.text)
    subjectivity = doc._.subjectivity

    log("[Sentiment] Article subjectivity: {:.3f}".format(subjectivity), LOGGING_ENABLED)

    return 1 - subjectivity
