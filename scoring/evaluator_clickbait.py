import io
import logging
import pickle
import re
import string
from contextlib import redirect_stderr
from pathlib import Path

from scipy import sparse

import stats_collector
from parsing.webpage_data import WebpageData

logger = logging.getLogger("alpaca")


def evaluate_clickbait(data: WebpageData) -> float:
    """Determines whether a webpage's headline is clickbait.

    :return: 1 if the headline is not clickbait (or empty), 0 if it is.
    """

    score = 0 if data.headline and _is_clickbait(data.headline) else 1
    stats_collector.add_result(data.url, "clickbait", score if data.headline else -10)
    return score


def _is_clickbait(headline: str) -> bool:
    """Clickbait classifier by Alison Salerno https://github.com/AlisonSalerno/clickbait_detector

    :return: True if submitted headline is clickbait, False otherwise.
    """

    # load pickled model and tfidf vectorizer, redirect external error prints to our logger
    with redirect_stderr(io.StringIO()) as buf:
        model = pickle.load(open((Path(__file__).parent / "files/nbmodel.pkl").resolve(), "rb"))
        vectorizer = pickle.load(open((Path(__file__).parent / "files/tfidf.pkl").resolve(), "rb"))
        for message in buf.getvalue().strip().split("\n"):
            if message:
                logger.debug("[Clickbait>External] " + str(message))

    cleaned_headline = _clean_text(headline)
    headline_words = len(cleaned_headline.split())
    question = _contains_question(cleaned_headline)
    exclamation = _contains_exclamation(cleaned_headline)
    starts_with_num = _starts_with_number(cleaned_headline)

    logger.debug("[Clickbait] Cleaned headline: " + cleaned_headline)

    vectorizer_input = [cleaned_headline]
    vectorized = vectorizer.transform(vectorizer_input)
    final = sparse.hstack([question, exclamation, starts_with_num, headline_words, vectorized])
    result = model.predict(final)

    return result == 1


def _clean_text(text: str) -> str:
    """Make text lowercase, remove text in square brackets, remove punctuation and remove words containing numbers."""

    text = text.lower()
    # text = re.sub("\w*\d\w*", " ", text)
    text = re.sub("\n", " ", text)
    text = re.sub("  ", " ", text)
    text = re.sub(r"^https?:\/\/.*[\r\n]*", "", text, flags=re.MULTILINE)
    text = re.sub(r"\w+:\/{2}[\d\w-]+(\.[\d\w-]+)*(?:(?:\/[^\s/]*))*", "", text)
    text = re.sub("\[.*?\]", " ", text)
    text = re.sub("[%s]" % re.escape(string.punctuation), "", text)
    text = re.sub("“", "", text)
    text = re.sub("”", "", text)
    text = re.sub("’", "", text)
    text = re.sub("–", "", text)
    text = re.sub("‘", "", text)
    return text


def _contains_question(headline: str) -> int:
    if "?" in headline or headline.startswith(("who", "what", "where", "why", "when", "whose", "whom", "would", "will",
                                               "how", "which", "should", "could", "did", "do")):
        return 1
    else:
        return 0


def _contains_exclamation(headline: str) -> int:
    return 1 if "!" in headline else 0


def _starts_with_number(headline: str) -> int:
    return 1 if headline.startswith(("1", "2", "3", "4", "5", "6", "7", "8", "9")) else 0
