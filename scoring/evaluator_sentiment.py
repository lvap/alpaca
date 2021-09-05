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
POLARITY_LIMITS_TEXT = [-0.5, 0.75]
POLARITY_LIMITS_TITLE = [0, 1]
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

    Currently averages the results of VADER, FastText and spaCy sentiment analysis.
    Uses **POLARITY_MINIMUM** as polarity minimum for VADER and spaCy (best score, worst score at 1 absolute).

    :return: Value between 0 (extreme polarity/sentiment) and 1 (relatively moderate polarity/sentiment).
    """

    # TODO decide on the better-performing sentiment analysis tool(s) as indicator of credibility (+documentation)

    # sentiment analysis with spacy
    doc = nlp(data.text)
    polarity_spacy = doc._.polarity

    # sentiment analysis with vader
    polarity_vader = SentimentIntensityAnalyzer().polarity_scores(data.text)

    # sentiment analysis using fasttext
    text_ft = _tokenizer(data.text.replace("\n", " ")).lower()
    sentiment_ft = _sentiment_analyser([text_ft])
    score_ft = sentiment_ft[0][0] + sentiment_ft[0][4]  # sum of extreme sentiments
    score_ft = 1 - score_ft

    np.set_printoptions(precision=3)
    logger.debug("[Sentiment] Text polarity raw: SpaCy {:.3f} | VADER {} | FastText {}"
                 .format(polarity_spacy, polarity_vader, sentiment_ft[0]))
    stats_collector.add_result(data.url, "sentiment_text_spacy", polarity_spacy)
    stats_collector.add_result(data.url, "sentiment_text_vader", polarity_vader["compound"])
    stats_collector.add_result(data.url, "positivity_text_vader", polarity_vader["pos"])
    stats_collector.add_result(data.url, "negativity_text_vader", polarity_vader["neg"])
    stats_collector.add_result(data.url, "sentiment_text_fasttext_1", sentiment_ft[0][0])
    stats_collector.add_result(data.url, "sentiment_text_fasttext_2", sentiment_ft[0][1])
    stats_collector.add_result(data.url, "sentiment_text_fasttext_3", sentiment_ft[0][2])
    stats_collector.add_result(data.url, "sentiment_text_fasttext_4", sentiment_ft[0][3])
    stats_collector.add_result(data.url, "sentiment_text_fasttext_5", sentiment_ft[0][4])

    sentiment = polarity_vader["compound"] - POLARITY_LIMITS_TEXT[0]
    sentiment /= POLARITY_LIMITS_TEXT[1] - POLARITY_LIMITS_TEXT[0]
    return min(max(sentiment, 0), 1)


def evaluate_polarity_title(data: WebpageData) -> float:
    """Evaluates the polarity of the webpage's headline through sentiment analysis.

    Currently averages the results of VADER, FastText and spaCy sentiment analysis.
    Uses **POLARITY_MINIMUM** as polarity minimum for VADER and spaCy (best score, worst score at 1 absolute).

    :return: Value between 0 (extreme polarity/sentiment) and 1 (relatively moderate polarity/sentiment).
    """

    # TODO decide on the better-performing sentiment analysis tool(s) as indicator of credibility (+documentation)

    if not data.headline:
        stats_collector.add_result(data.url, "sentiment_title_spacy", -10)
        stats_collector.add_result(data.url, "sentiment_title_vader", -10)
        stats_collector.add_result(data.url, "positivity_title_vader", -10)
        stats_collector.add_result(data.url, "negativity_title_vader", -10)
        stats_collector.add_result(data.url, "sentiment_title_fasttext_1", -10)
        stats_collector.add_result(data.url, "sentiment_title_fasttext_2", -10)
        stats_collector.add_result(data.url, "sentiment_title_fasttext_3", -10)
        stats_collector.add_result(data.url, "sentiment_title_fasttext_4", -10)
        stats_collector.add_result(data.url, "sentiment_title_fasttext_5", -10)
        return 0

    # sentiment analysis with spacy
    doc = nlp(data.headline)
    polarity_spacy = doc._.polarity

    # sentiment analysis with vader
    polarity_vader = SentimentIntensityAnalyzer().polarity_scores(data.headline)

    # sentiment analysis using fasttext
    text_ft = _tokenizer(data.headline.replace("\n", " ")).lower()
    sentiment_ft = _sentiment_analyser([text_ft])
    score_ft = sentiment_ft[0][0] + sentiment_ft[0][4]  # sum of extreme sentiments
    score_ft = 1 - score_ft

    np.set_printoptions(precision=3)
    logger.debug("[Sentiment] Headline polarity raw: SpaCy {:.3f} | VADER {} | FastText {}"
                 .format(polarity_spacy, polarity_vader, sentiment_ft[0]))
    stats_collector.add_result(data.url, "sentiment_title_spacy", polarity_spacy)
    stats_collector.add_result(data.url, "sentiment_title_vader", polarity_vader["compound"])
    stats_collector.add_result(data.url, "positivity_title_vader", polarity_vader["pos"])
    stats_collector.add_result(data.url, "negativity_title_vader", polarity_vader["neg"])
    stats_collector.add_result(data.url, "sentiment_title_fasttext_1", sentiment_ft[0][0])
    stats_collector.add_result(data.url, "sentiment_title_fasttext_2", sentiment_ft[0][1])
    stats_collector.add_result(data.url, "sentiment_title_fasttext_3", sentiment_ft[0][2])
    stats_collector.add_result(data.url, "sentiment_title_fasttext_4", sentiment_ft[0][3])
    stats_collector.add_result(data.url, "sentiment_title_fasttext_5", sentiment_ft[0][4])

    negativity = polarity_vader["neg"] - POLARITY_LIMITS_TITLE[0]
    negativity /= POLARITY_LIMITS_TITLE[1] - POLARITY_LIMITS_TITLE[0]
    return 1 - max(min(negativity, 1), 0)


def evaluate_subjectivity(data: WebpageData) -> float:
    """Evaluates the subjectivity of the webpage using spaCy.

    Score is linear between **SUBJECTIVITY_LIMITS[0]** subjectivity or lower (best score => 1)
    and **SUBJECTIVITY_LIMITS[1]** subjectivity or higher (worst score => 0).

    :return: Value between 0 (high webpage subjectivity) and 1 (low webpage subjectivity).
    """

    doc = nlp(data.text)
    subjectivity = doc._.subjectivity

    logger.debug("[Sentiment] Article subjectivity: {:.3f}".format(subjectivity))
    stats_collector.add_result(data.url, "subjectivity", subjectivity)

    subjectivity_score = (subjectivity - SUBJECTIVITY_LIMITS[0]) / (SUBJECTIVITY_LIMITS[1] - SUBJECTIVITY_LIMITS[0])
    subjectivity_score = max(min(subjectivity_score, 1), 0)
    return 1 - subjectivity_score


def _sentiment_analyser(texts: list[str]) -> np.array([float, ...]):
    """Sentiment analyser by Prashanth Rao https://github.com/prrao87/fine-grained-sentiment-app

    :return: Sentiment analysis of the input texts, classifying each into 5 groups from 0 (very negative) to 5
        (very positive). The numbers in each of the 5 groups represents the probability of the text belonging to it.
    """

    # load fasttext model, redirect external error prints to logger
    with redirect_stderr(io.StringIO()) as buf:
        classifier = fasttext.load_model(str((Path(__file__).parent / "files/sst5_hyperopt.ftz").resolve()))
        for message in buf.getvalue().strip().split("\n"):
            if message:
                logger.debug("[Sentiment>FastText] " + message)

    labels, probs = classifier.predict(texts, 5)

    # For each prediction, sort the probability scores in the same order for all texts
    result = []
    for label, prob, text in zip(labels, probs, texts):
        order = np.argsort(np.array(label))
        result.append(prob[order])
    return np.array(result)


def _tokenizer(text: str) -> str:
    """Tokenize input string using a spaCy pipeline"""

    _nlp = spacy.blank('en')
    _nlp.add_pipe("sentencizer")  # Very basic NLP pipeline in spaCy
    doc = _nlp(text)
    tokenized_text = ' '.join(token.text for token in doc)
    return tokenized_text
