import logging

from parsing.tokenize import word_tokenize
from parsing.webpage_data import WebpageData
import stats_collector

logger = logging.getLogger("alpaca")

# value limits for subscores
WORDS_LIMITS_TEXT = [300, 900]
WORDS_LIMITS_TITLE = [10, 25]
SENTENCES_LIMITS = [5, 30]
TTR_LIMITS = [0.5, 1]
WORDLENGTH_LIMITS_TEXT = [4, 8]
WORDLENGTH_LIMITS_TITLE = [4, 8]

# boundary checks
if not (1 <= WORDS_LIMITS_TEXT[0] < WORDS_LIMITS_TEXT[1] and 1 <= WORDS_LIMITS_TITLE[0] < WORDS_LIMITS_TITLE[1]
        and 1 <= SENTENCES_LIMITS[0] < SENTENCES_LIMITS[1] and 0 < TTR_LIMITS[0] < TTR_LIMITS[1] <= 1
        and 1 <= WORDLENGTH_LIMITS_TEXT[0] < WORDLENGTH_LIMITS_TEXT[1]
        and 1 <= WORDLENGTH_LIMITS_TITLE[0] < WORDLENGTH_LIMITS_TITLE[1]):
    raise ValueError("A constant for language structure evaluation is set incorrectly")


def evaluate_word_count_text(data: WebpageData) -> float:
    """Evaluates the number of words in the text body of a webpage.

    Returned score is linear between **WORDS_LIMITS_TEXT[0]** or fewer words (worst score => 0)
    and **WORDS_LIMITS_TEXT[1]** or more words (best score => 1).

    :return: Score between 0 and 1, with 0 indicating low number of words and 1 high number of words.
    """

    word_count = len(data.text_words)
    logger.debug("[Lang_structure] Words in text: " + str(word_count))
    stats_collector.add_result(data.url, "word_count_text", word_count)

    word_score = (word_count - WORDS_LIMITS_TEXT[0]) / (WORDS_LIMITS_TEXT[1] - WORDS_LIMITS_TEXT[0])
    return min(max(word_score, 0), 1)


def evaluate_word_count_title(data: WebpageData) -> float:
    """Evaluates the number of words in the headline of a webpage.

    Returned score is linear between **WORDS_LIMITS_TITLE[0]** or fewer words (worst score => 0)
    and **WORDS_LIMITS_TITLE[1]** or more words (best score => 1).

    :return: Score between 0 and 1, with 0 indicating low number of words and 1 high number of words.
    """

    if not data.headline:
        stats_collector.add_result(data.url, "word_count_title", -10)
        return 0

    word_count = len(word_tokenize(data.headline))

    logger.debug("[Lang_structure] Words in title: " + str(word_count))
    stats_collector.add_result(data.url, "word_count_title", word_count)

    word_score = (word_count - WORDS_LIMITS_TITLE[0]) / (WORDS_LIMITS_TITLE[1] - WORDS_LIMITS_TITLE[0])
    return 1 - min(max(word_score, 0), 1)


def evaluate_sentence_count(data: WebpageData) -> float:
    """Evaluates the number of sentences in the text body of a webpage.

    Returned score is linear between **SENTENCES_LIMITS[0]** or fewer sentences (worst score => 0)
    and **SENTENCES_LIMITS[1]** or more sentences (best score => 1).

    :return: Score between 0 and 1, with 0 indicating low number of sentences and 1 high number of sentences.
    """

    sentence_count = len(data.text_sentences)

    logger.debug("[Lang_structure] Sentences in text: " + str(sentence_count))
    stats_collector.add_result(data.url, "sentence_count", sentence_count)

    score = (sentence_count - SENTENCES_LIMITS[0]) / (SENTENCES_LIMITS[1] - SENTENCES_LIMITS[0])
    return min(max(score, 0), 1)


def evaluate_ttr(data: WebpageData) -> float:
    """Evaluates the type-token-ratio of a webpage's main text body.

    Type-token-ratio (TTR) is equal to number of unique words divided by total number of words.
    Returned score is linear between a TTR value of **TTR_LIMITS[0]** or lower (worst score => 0)
    and a TTR value of **TTR_LIMITS[1]** or higher (best score => 1).

    :return: Score between 0 and 1, with 0 indicating high redundancy and 1 low redundancy.
    """

    ttr = len(set(data.text_words)) / len(data.text_words)

    logger.debug("[Lang_structure] Type-token-ratio: " + str(ttr))
    stats_collector.add_result(data.url, "ttr", ttr)

    ttr_score = (ttr - TTR_LIMITS[0]) / (TTR_LIMITS[1] - TTR_LIMITS[0])
    return max(ttr_score, 0)


def evaluate_word_length_text(data: WebpageData) -> float:
    """Evaluates the average length of words in the text body of a webpage.

    Returned score is linear between **WORDLENGTH_LIMITS_TEXT[0]** or fewer characters per word (worst score => 0)
    and **WORDLENGTH_LIMITS_TEXT[1]** or more characters per word (best score => 1).

    :return: Score between 0 and 1, with 0 indicating relatively short words and 1 relatively long words on average.
    """

    word_length = sum(len(word) for word in data.text_words) / len(data.text_words)

    logger.debug("[Lang_structure] Word length text: " + str(word_length))
    stats_collector.add_result(data.url, "word_length_text", word_length)

    score = (word_length - WORDLENGTH_LIMITS_TEXT[0]) / (WORDLENGTH_LIMITS_TEXT[1] - WORDLENGTH_LIMITS_TEXT[0])
    return min(max(score, 0), 1)


def evaluate_word_length_title(data: WebpageData) -> float:
    """Evaluates the average length of words in the headline of a webpage.

    Returned score is linear between **WORDLENGTH_LIMITS_TITLE[0]** or fewer characters per word (worst score => 0)
    and **WORDLENGTH_LIMITS_TITLE[1]** or more characters per word (best score => 1).

    :return: Score between 0 and 1, with 0 indicating relatively short words and 1 relatively long words on average.
    """

    if not data.headline:
        stats_collector.add_result(data.url, "word_length_title", -10)
        return 0

    headline_tokens = word_tokenize(data.headline)
    word_length = sum(len(word) for word in headline_tokens) / len(headline_tokens)

    logger.debug("[Lang_structure] Word length title: " + str(word_length))
    stats_collector.add_result(data.url, "word_length_title", word_length)

    score = (word_length - WORDLENGTH_LIMITS_TITLE[0]) / (WORDLENGTH_LIMITS_TITLE[1] - WORDLENGTH_LIMITS_TITLE[0])
    return min(max(score, 0), 1)
