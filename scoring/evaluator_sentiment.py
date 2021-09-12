import io
import logging
from contextlib import redirect_stderr
from pathlib import Path

import fasttext
import numpy as np
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

import stats_collector
from parsing.webpage_data import WebpageData

# value limits for subscore computation
POLARITY_LIMITS_TEXT = [-0.5, 1]
POLARITY_LIMITS_TITLE = [0, 0.3]
SUBJECTIVITY_LIMITS = [0.4, 0.7]

# boundary check
if not (-1 <= POLARITY_LIMITS_TEXT[0] < POLARITY_LIMITS_TEXT[1] <= 1
        and 0 <= POLARITY_LIMITS_TITLE[0] < POLARITY_LIMITS_TITLE[1] <= 1
        and 0 <= SUBJECTIVITY_LIMITS[0] < SUBJECTIVITY_LIMITS[1] <= 1):
    raise ValueError("Limits for one or more sentiment evaluators set incorrectly")

logger = logging.getLogger("alpaca")

nlp = spacy.load('en_core_web_sm')
nlp.add_pipe("spacytextblob")


def evaluate_polarity_text(data: WebpageData) -> float:
    """Evaluates the polarity of the webpage' text through sentiment analysis.

    Uses VADER sentiment analysis to compute the text's sentiment. Score is linear between a sentiment of
    **POLARITY_LIMITS_TEXT[0]** or lower (worst score => 0) and **POLARITY_LIMITS_TEXT[1]** or higher
    (best score => 1).

    Computes positive, negative and compound sentiment for comparison purposes.

    :return: Value between 0 (relatively negative sentiment) and 1 (relatively positive sentiment).
    """

    polarity_vader = SentimentIntensityAnalyzer().polarity_scores(data.text)

    logger.debug("[Sentiment] Text polarity (VADER): {}".format(polarity_vader))
    stats_collector.add_result(data.url, "sentiment_text_vader", polarity_vader["compound"])
    stats_collector.add_result(data.url, "positivity_text_vader", polarity_vader["pos"])
    stats_collector.add_result(data.url, "negativity_text_vader", polarity_vader["neg"])

    polarity = polarity_vader["compound"] - POLARITY_LIMITS_TEXT[0]
    polarity /= POLARITY_LIMITS_TEXT[1] - POLARITY_LIMITS_TEXT[0]
    return min(max(polarity, 0), 1)


def evaluate_polarity_title(data: WebpageData) -> float:
    """Evaluates the negativity of the webpage's headline through sentiment analysis.

     Uses VADER sentiment analysis to compute the text's negativity. Score is linear between a negativity of
    **POLARITY_LIMITS_TITLE[0]** or lower (best score => 1) and **POLARITY_LIMITS_TITLE[1]** or higher
    (worst score => 0).

    Computes positive, negative and compound sentiment for comparison purposes.

    :return: Value between 0 (low negative sentiment) and 1 (high negative sentiment).
    """

    if not data.headline:
        stats_collector.add_result(data.url, "sentiment_title_vader", -10)
        stats_collector.add_result(data.url, "positivity_title_vader", -10)
        stats_collector.add_result(data.url, "negativity_title_vader", -10)
        return 0

    polarity_vader = SentimentIntensityAnalyzer().polarity_scores(data.headline)

    logger.debug("[Sentiment] Headline polarity (VADER): {}".format(polarity_vader))
    stats_collector.add_result(data.url, "sentiment_title_vader", polarity_vader["compound"])
    stats_collector.add_result(data.url, "positivity_title_vader", polarity_vader["pos"])
    stats_collector.add_result(data.url, "negativity_title_vader", polarity_vader["neg"])

    polarity = polarity_vader["neg"] - POLARITY_LIMITS_TITLE[0]
    polarity /= POLARITY_LIMITS_TITLE[1] - POLARITY_LIMITS_TITLE[0]
    return 1 - max(min(polarity, 1), 0)


def evaluate_subjectivity(data: WebpageData) -> float:
    """Evaluates the subjectivity of the webpage.

    Uses TextBlob (through spaCy) to compute the text's subjectivity. Score is linear between **SUBJECTIVITY_LIMITS[0]**
     subjectivity or lower (best score => 1) and **SUBJECTIVITY_LIMITS[1]** subjectivity or higher (worst score => 0).

    :return: Value between 0 (high webpage subjectivity) and 1 (low webpage subjectivity).
    """

    doc = nlp(data.text)
    subjectivity = doc._.subjectivity

    logger.debug("[Sentiment] Article subjectivity: {:.3f}".format(subjectivity))
    stats_collector.add_result(data.url, "subjectivity", subjectivity)

    subjectivity_score = (subjectivity - SUBJECTIVITY_LIMITS[0]) / (SUBJECTIVITY_LIMITS[1] - SUBJECTIVITY_LIMITS[0])
    subjectivity_score = max(min(subjectivity_score, 1), 0)
    return 1 - subjectivity_score
