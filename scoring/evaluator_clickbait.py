import pickle
import re
import string
import warnings
from pathlib import Path

import nltk
from nltk.corpus import stopwords
from scipy import sparse

from logger import log
from parsing.webpage_data import WebpageData

warnings.filterwarnings('ignore')
# nltk.download("stopwords")

# toggle some file-specific logging messages
LOGGING_ENABLED = False


def evaluate_clickbait(data: WebpageData) -> float:
    """TODO documentation

    :param data:
    :return:
    """

    return 0 if classify_clickbait(data.headline) else 1


def classify_clickbait(headline: str) -> bool:
    """Clickbait classifier by Alison Salerno (https://github.com/AlisonSalerno/clickbait_detector).
    Return true if submitted headline is clickbait, false otherwise."""

    model_path = (Path(__file__).parent / "../files/nbmodel.pkl").resolve()
    tfidf_path = (Path(__file__).parent / "../files/tfidf.pkl").resolve()

    # loading pickled model and tfidf vectorizer
    model = pickle.load(open(model_path, "rb"))
    stopwords_list = stopwords.words("english")
    vectorizer = pickle.load(open(tfidf_path, "rb"))

    cleaned_headline = clean_text(headline)
    headline_words = len(cleaned_headline.split())
    question = contains_question(cleaned_headline)
    exclamation = contains_exclamation(cleaned_headline)
    starts_with_num = starts_with_number(cleaned_headline)

    log("[Clickbait] Cleaned headline: " + cleaned_headline, LOGGING_ENABLED)

    vectorizer_input = [cleaned_headline]
    vectorized = vectorizer.transform(vectorizer_input)
    final = sparse.hstack([question, exclamation, starts_with_num, headline_words, vectorized])
    result = model.predict(final)

    return result == 1


def clean_text(text: str) -> str:
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


def contains_question(headline: str) -> int:
    if "?" in headline or headline.startswith(("who", "what", "where", "why", "when", "whose", "whom", "would", "will",
                                               "how", "which", "should", "could", "did", "do")):
        return 1
    else:
        return 0


def contains_exclamation(headline: str) -> int:
    return 1 if "!" in headline else 0


def starts_with_number(headline: str) -> int:
    return 1 if headline.startswith(("1", "2", "3", "4", "5", "6", "7", "8", "9")) else 0
