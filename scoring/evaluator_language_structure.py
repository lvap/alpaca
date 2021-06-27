import logging

from parsing.tokenize import word_tokenize
from parsing.webpage_data import WebpageData
from analysis import stats_collector

# modify language structure score gradients given these limits
WORDS_TEXT_LOWER = 300
WORDS_TEXT_UPPER = 900
WORDS_TITLE_LOWER = 10
WORDS_TITLE_UPPER = 25
SENTENCES_LOWER = 5
SENTENCES_UPPER = 30
TTR_MINIMUM = 0.5
WLENGTH_TEXT_LOWER = 4
WLENGTH_TEXT_UPPER = 8
WLENGTH_TITLE_LOWER = 4
WLENGTH_TITLE_UPPER = 8

# boundary checks
if not (1 <= WORDS_TEXT_LOWER < WORDS_TEXT_UPPER and 1 <= WORDS_TITLE_LOWER < WORDS_TITLE_UPPER
        and 1 <= SENTENCES_LOWER < SENTENCES_UPPER and 0 < TTR_MINIMUM < 1
        and 1 <= WLENGTH_TEXT_LOWER < WLENGTH_TEXT_UPPER and 1 <= WLENGTH_TITLE_LOWER < WLENGTH_TITLE_UPPER):
    raise ValueError("A constant for language structure evaluation is set incorrectly")

logger = logging.getLogger("alpaca")


# TODO possibly add nouns text/title, stop words title

def evaluate_word_count_text(data: WebpageData) -> float:
    """Evaluates the number of words in the text body of a webpage.

    Returned score is linear between *WORDS_TEXT_LOWER* or fewer words (worst score => 0) and *WORDS_TEXT_UPPER* or
    more words (best score => 1).

    :return: Score between 0 and 1, with 0 indicating low number of words and 1 high number of words.
    """

    word_count = len(data.text_words)
    logger.info("[Lang_structure] Words in text: " + str(word_count))
    stats_collector.add_result(data.url, "word_count_text", word_count)

    word_score = (word_count - WORDS_TEXT_LOWER) / (WORDS_TEXT_UPPER - WORDS_TEXT_LOWER)
    return min(max(word_score, 0), 1)


def evaluate_word_count_title(data: WebpageData) -> float:
    """Evaluates the number of words in the headline of a webpage.

    Returned score is linear between *WORDS_TITLE_LOWER* or fewer words (worst score => 0) and *WORDS_TITLE_UPPER* or
    more words (best score => 1).

    :return: Score between 0 and 1, with 0 indicating low number of words and 1 high number of words.
    """

    word_count = len(word_tokenize(data.headline))
    logger.info("[Lang_structure] Words in title: " + str(word_count))
    stats_collector.add_result(data.url, "word_count_title", word_count)

    word_score = (word_count - WORDS_TEXT_LOWER) / (WORDS_TEXT_UPPER - WORDS_TEXT_LOWER)
    return 1 - min(max(word_score, 0), 1)


def evaluate_sentence_count(data: WebpageData) -> float:
    """Evaluates the number of sentences in the text body of a webpage.

    Returned score is linear between *SENTENCES_LOWER* or fewer sentences (worst score => 0) and *SENTENCES_UPPER* or
    more sentences (best score => 1).

    :return: Score between 0 and 1, with 0 indicating low number of sentences and 1 high number of sentences.
    """

    sentence_count = len(data.text_sentences)
    logger.info("[Lang_structure] Sentences in text: " + str(sentence_count))
    stats_collector.add_result(data.url, "sentence_count", sentence_count)

    score = (sentence_count - SENTENCES_LOWER) / (SENTENCES_UPPER - SENTENCES_LOWER)
    return min(max(score, 0), 1)


def evaluate_ttr(data: WebpageData) -> float:
    """Evaluates the type-token-ratio of a webpage's main text body.

    Type-token-ratio (TTR) is equal to number of unique words divided by total number of words. TTR is a measure of a
    text's redundancy and lexical diversity. Returned score is linear between a TTR value of *TRR_MINIMUM* or lower
    (worst score => 0) and a TTR value of 1 (best score => 1).

    :return: Score between 0 and 1, with 0 indicating high redundancy and 1 low redundancy.
    """

    ttr = len(set(data.text_words)) / len(data.text_words)
    logger.info("[Lang_structure] Type-token-ratio: " + str(ttr))
    stats_collector.add_result(data.url, "ttr", ttr)

    ttr_score = (ttr - TTR_MINIMUM) / TTR_MINIMUM
    return max(ttr_score, 0)


def evaluate_word_length_text(data: WebpageData) -> float:
    """Evaluates the average length of words in the text body of a webpage.

    Returned score is linear between *WLENGTH_TEXT_LOWER* or fewer characters per word (worst score => 0) and
    *WLENGTH_TEXT_UPPER* or more characters per word (best score => 1).

    :return: Score between 0 and 1, with 0 indicating relatively short words and 1 relatively long words on average.
    """

    word_length = sum(len(word) for word in data.text_words) / len(data.text_words)
    logger.info("[Lang_structure] Word length text: " + str(word_length))
    stats_collector.add_result(data.url, "word_length_text", word_length)

    score = (word_length - WLENGTH_TEXT_LOWER) / (WLENGTH_TEXT_UPPER - WLENGTH_TEXT_LOWER)
    return min(max(score, 0), 1)


def evaluate_word_length_title(data: WebpageData) -> float:
    """Evaluates the average length of words in the headline of a webpage.

    Returned score is linear between *WLENGTH_TITLE_LOWER* or fewer characters per word (worst score => 0) and
    *WLENGTH_TITLE_UPPER* or more characters per word (best score => 1).

    :return: Score between 0 and 1, with 0 indicating relatively short words and 1 relatively long words on average.
    """

    headline_tokens = word_tokenize(data.headline)
    word_length = sum(len(word) for word in headline_tokens) / len(headline_tokens)

    logger.info("[Lang_structure] Word length title: " + str(word_length))
    stats_collector.add_result(data.url, "word_length_title", word_length)

    score = (word_length - WLENGTH_TITLE_LOWER) / (WLENGTH_TITLE_UPPER - WLENGTH_TITLE_LOWER)
    return min(max(score, 0), 1)
