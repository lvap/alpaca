import logging
from typing import NamedTuple, Callable

import parsing.webpage_parser as parser
import scoring.evaluator_language_structure as ls
from performance_analysis import performance_test
from parsing.webpage_data import WebpageData
from scoring.evaluator_authors import evaluate_authors
from scoring.evaluator_clickbait import evaluate_clickbait
from scoring.evaluator_errors import evaluate_errors
from scoring.evaluator_links import evaluate_links_external
from scoring.evaluator_readability import evaluate_readability_text, evaluate_readability_title
from scoring.evaluator_sentiment import evaluate_polarity_title, evaluate_polarity_text, evaluate_subjectivity
import scoring.evaluator_tonality as tonality
from scoring.evaluator_url import evaluate_domain_ending
from scoring.evaluator_vocabulary import evaluate_profanity, evaluate_emotional_words

logger = logging.getLogger("alpaca")


class CredibilitySignal(NamedTuple):
    """A webpage credibility signal, including its evaluator and weight functions.

    :param evaluator: Returns the signal sub-score given some webpage data. Between 0 - 1
    :param weight_func: Returns weight to be used for this signal when combining all sub-scores into the overall webpage
        score, takes own sub-score and webpage data as input.
    """
    evaluator: Callable[[WebpageData], float]
    weight_func: Callable[[float, WebpageData], float]


# TODO tweak evaluation weights
# holds credibility signals with signal evaluator and weight functions
evaluation_signals = {
    "authors":                      CredibilitySignal(evaluate_authors,
                                                      lambda score, d: 0.3),
    "url_domain_ending":            CredibilitySignal(evaluate_domain_ending,
                                                      lambda score, d: 0 if not d.url or score < 1 else 0.2),
    "errors":                       CredibilitySignal(evaluate_errors,
                                                      lambda score, d: 0.3 if score > 0.8 else 0.45),
    "tonality_questions_text":      CredibilitySignal(tonality.evaluate_questions_text,
                                                      lambda score, d: 0 if score > 0.8 else 0.2),
    "tonality_questions_title":     CredibilitySignal(tonality.evaluate_questions_title,
                                                      lambda s, d: 0 if not d.headline else 0.2 if s > 0 else 0.3),
    "tonality_exclamations_text":   CredibilitySignal(tonality.evaluate_exclamations_text,
                                                      lambda score, d: 0 if score > 0.8 else 0.2),
    "tonality_exclamations_title":  CredibilitySignal(tonality.evaluate_exclamations_title,
                                                      lambda s, d: 0 if not d.headline else 0.2 if s > 0 else 0.3),
    "tonality_all_caps_text":       CredibilitySignal(tonality.evaluate_all_caps_text,
                                                      lambda score, d: 0 if score > 0.8 else 0.3),
    "tonality_all_caps_title":      CredibilitySignal(tonality.evaluate_all_caps_title,
                                                      lambda s, d:
                                                      0 if d.headline.upper() == d.headline else 0.2 if s > 0 else 0.3),
    "readability_text":             CredibilitySignal(evaluate_readability_text,
                                                      lambda score, d: 0.8),
    "readability_title":            CredibilitySignal(evaluate_readability_title,
                                                      lambda score, d: 0.3 if d.headline else 0),
    "ls_word_count_text":           CredibilitySignal(ls.evaluate_word_count_text,
                                                      lambda score, d: 0.5),
    "ls_word_count_title":          CredibilitySignal(ls.evaluate_word_count_title,
                                                      lambda score, d: 0.3 if d.headline else 0),
    "ls_sentence_count":            CredibilitySignal(ls.evaluate_sentence_count,
                                                      lambda score, d: 0.3),
    "ls_type_token_ratio":          CredibilitySignal(ls.evaluate_ttr,
                                                      lambda score, d: 0.4),
    "ls_word_length_text":          CredibilitySignal(ls.evaluate_word_length_text,
                                                      lambda score, d: 0.3),
    "ls_word_length_title":         CredibilitySignal(ls.evaluate_word_length_title,
                                                      lambda score, d: 0.4 if d.headline else 0),
    "vocabulary_profanity":         CredibilitySignal(evaluate_profanity,
                                                      lambda score, d: 0 if score == 1 else 1),
    "vocabulary_emotional_words":   CredibilitySignal(evaluate_emotional_words,
                                                      lambda score, d: 0.6),
    "clickbait":                    CredibilitySignal(evaluate_clickbait,
                                                      lambda s, d: 0 if not d.headline else 0.3 if s > 0 else 0.8),
    "links_external":               CredibilitySignal(evaluate_links_external,
                                                      lambda s, d: 0 if not d.url or not d.html or 0 < s < 1 else 0.3),
    "sentiment_polarity_text":      CredibilitySignal(evaluate_polarity_text,
                                                      lambda score, d: 0.8),
    "sentiment_polarity_title":     CredibilitySignal(evaluate_polarity_title,
                                                      lambda score, d: 0.5 if d.headline else 0),
    "sentiment_subjectivity":       CredibilitySignal(evaluate_subjectivity,
                                                      lambda score, d: 0.4),
}


def evaluate_webpage(url: str) -> float:
    """Scores a webpage's credibility by combining the credibility scores of different evaluators.

    Obtains the webpage data from parser, retrieves the signal sub-scores, validates the results and then generates an
    overall webpage credibility score via linear combination of the sub-scores using the *evaluation_weights* dict.

    :param url: URL of the webpage to be evaluated.
    :return: A credibility score from 0 (very low credibility) to 1 (very high credibility).
        Returns -1 if the webpage could not be parsed, and -2 if it could not be evaluated.
    """

    logger.debug("[Evaluation] Evaluating " + url)

    page_data = parser.parse_data(url)
    # check for valid data
    if not page_data or not page_data.url or not page_data.html or len(page_data.text) < 50:
        logger.error("[Evaluation] Webpage parsing failed for " + url)
        return -1

    scores = {}
    weight_sum = 0
    final_score = 0

    # compute sub-scores and sum up overall score via linear combination
    for signal_name, signal in evaluation_signals.items():
        subscore = signal.evaluator(page_data)
        weight = signal.weight_func(subscore, page_data)
        scores[signal_name] = subscore
        final_score += subscore * weight
        weight_sum += weight
        performance_test.add_result(url, "score_" + signal_name, subscore)

    # check for valid scores
    if not scores or len(scores) != len(evaluation_signals) or not all(0 <= score <= 1 for score in scores.values()):
        logger.error("[Evaluation] Error computing sub-scores: {}".format(scores))
        return -2

    logger.info("[Evaluation] Individual sub-scores: {}".format(
        [signal_name + " {:.3f}".format(score) for signal_name, score in scores.items()]))

    final_score = final_score / weight_sum
    logger.debug("[Evaluation] Overall webpage score: {:.5f} for {}".format(final_score, url))
    return final_score
