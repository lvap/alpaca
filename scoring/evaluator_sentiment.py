import io
import logging
from contextlib import redirect_stderr
from pathlib import Path

import fasttext
import numpy as np
import spacy
from spacytextblob.spacytextblob import SpacyTextBlob
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer

from parsing.webpage_data import WebpageData
from parsing.webpage_parser import has_ending_punctuation

# lower limit for polarity scores (greater than 0, lower than 1)
POLARITY_MINIMUM = 0.5

# boundary check
if not 0 < POLARITY_MINIMUM < 1:
    raise ValueError("POLARITY_MINIMUM must be greater than 0 and lower than 1.")

LOGGER = logging.getLogger("alpaca")


def evaluate_polarity(data: WebpageData) -> float:
    """Evaluates the polarity of the webpage through sentiment analysis.

    Performs sentiment analysis to determine a webpage's positivity/negativity score between -1 and 1, then looks at the
    absolute value as indicator of "extremism"/"emotionality". Final score is linear from 0 (absolute polarity is 1)
    to 1 (absolute polarity is at most *POLARITY_MINIMUM*). Uses average of spaCy and VADER sentiment analysis.

    :return: Value between 0 (extreme polarity) and 1 (relatively low polarity).
    """

    # TODO decide on the better-performing sentiment analysis tool(s) as indicator of credibility
    # TODO possibly separate in headline / text

    headline_ending = " " if has_ending_punctuation(data.headline) else ". " if data.headline else ""
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
    # scale polarity scores from interval [POLARITY_MINIMUM, 1]
    score_spacy = 1 - max((score_spacy - POLARITY_MINIMUM) / POLARITY_MINIMUM, 0)
    score_vader = 1 - max((score_vader - POLARITY_MINIMUM) / POLARITY_MINIMUM, 0)

    # sentiment analysis using fasttext
    text_ft = _tokenizer(article.replace("\n", " ")).lower()
    sentiment_ft = _sentiment_analyser([text_ft])
    score_ft = sentiment_ft[0][0] + sentiment_ft[0][4]  # sum of extreme sentiments
    score_ft = 1 - score_ft

    np.set_printoptions(precision=3)
    LOGGER.debug("[Sentiment] Article polarity raw: SpaCy {:.3f} | VADER {} | FastText {}"
                 .format(polarity_spacy, polarity_vader, sentiment_ft[0]))
    LOGGER.debug("[Sentiment] Article polarity scores: SpaCy {:.3f} | VADER {:.3f} | FastText {:.3f}"
                 .format(score_spacy, score_vader, score_ft))

    return (score_spacy + score_vader + score_ft) / 3


def evaluate_subjectivity(data: WebpageData) -> float:
    """Evaluates the subjectivity of the webpage using spaCy.

    :return: Value between 0 (very high webpage subjectivity) and 1 (very low webpage subjectivity).
    """

    nlp = spacy.load('en_core_web_sm')
    nlp.add_pipe("spacytextblob")
    headline_ending = " " if has_ending_punctuation(data.headline) else ". " if data.headline else ""
    doc = nlp(data.headline + headline_ending + data.text)
    subjectivity = doc._.subjectivity

    LOGGER.debug("[Sentiment] Article subjectivity: {:.3f}".format(subjectivity))

    return 1 - subjectivity


def _sentiment_analyser(texts: list[str]) -> np.array([float, ...]):
    """Sentiment analyser by Prashanth Rao https://github.com/prrao87/fine-grained-sentiment-app

    :return: Sentiment analysis of the input texts, classifying each into 5 groups from 0 (very negative) to 5
        (very positive). The numbers in each of the 5 groups represents the probability of the text belonging to it."""

    model_path = (Path(__file__).parent / "../files/sst5_hyperopt.ftz").resolve()
    # redirect external error prints to our own logger
    with redirect_stderr(io.StringIO()) as buf:
        classifier = fasttext.load_model(str(model_path))
        for message in buf.getvalue().strip().split("\n"):
            if message:
                LOGGER.debug("[Sentiment>FastText] " + message)

    labels, probs = classifier.predict(texts, 5)

    # For each prediction, sort the probability scores in the same order for all texts
    result = []
    for label, prob, text in zip(labels, probs, texts):
        order = np.argsort(np.array(label))
        result.append(prob[order])
    return np.array(result)


def _tokenizer(text: str) -> str:
    """Tokenize input string using a spaCy pipeline"""

    nlp = spacy.blank('en')
    nlp.add_pipe("sentencizer")  # Very basic NLP pipeline in spaCy
    doc = nlp(text)
    tokenized_text = ' '.join(token.text for token in doc)
    return tokenized_text
