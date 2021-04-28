import re
from typing import NamedTuple, Callable

import parsing.webpage_parser as parser
from logger import log
from parsing.webpage_data import WebpageData
from scoring.evaluator_authors import evaluate_authors
from scoring.evaluator_clickbait import evaluate_clickbait
from scoring.evaluator_grammar import evaluate_grammar
from scoring.evaluator_readability import evaluate_readability
from scoring.evaluator_tonality import evaluate_exclamation_marks, evaluate_question_marks, evaluate_capitalisation
from scoring.evaluator_url import evaluate_domain_ending
from scoring.evaluator_vocabulary import evaluate_profanity


class CredibilitySignal(NamedTuple):
    """Represents a credibility signal, including its evaluator function and weight towards the overall webpage score.

    :param weight: Default weight to be used when combining different sub-scores into the overall webpage score.
    :param evaluator: Returns signal sub-score given some webpage data.
    :param alt_weight: Alternate weight to be used if alt_condition evaluates to True.
    :param alt_condition: If True for this signal's sub-score as input, use alternate weight instead of weight
    """
    weight: float
    evaluator: Callable[[WebpageData], float]
    alt_weight: float
    alt_condition: Callable[[float], bool]


# holds signal evaluator methods and weights for linear combination into final score
evaluation_signals = {
    "authors":                      CredibilitySignal(0.2, evaluate_authors, -1, lambda score: False),
    "url_domain_ending":            CredibilitySignal(0.0, evaluate_domain_ending, 0.2, lambda score: score == 1),
    "grammar":                      CredibilitySignal(0.3, evaluate_grammar, -1, lambda score: False),
    "tonality_question_marks":      CredibilitySignal(0.2, evaluate_question_marks, -1, lambda score: False),
    "tonality_exclamation_marks":   CredibilitySignal(0.3, evaluate_exclamation_marks, -1, lambda score: False),
    "tonality_capitalisation":      CredibilitySignal(0.3, evaluate_capitalisation, -1, lambda score: False),
    "readability":                  CredibilitySignal(1.0, evaluate_readability, -1, lambda score: False),
    "vocabulary_profanity":         CredibilitySignal(0.0, evaluate_profanity, 1, lambda score: score < 1),
    "clickbait":                    CredibilitySignal(0.3, evaluate_clickbait, 1, lambda score: score == 0),
}


def evaluate_webpage(url: str) -> float:
    """Scores a webpage's credibility by combining the credibility scores of different evaluators.

    Obtains the webpage data from parser, retrieves the signal sub-scores, validates the results and then generates an
    overall webpage credibility score via linear combination of the sub-scores using the *evaluation_weights* dict.

    :param url: URL of the webpage to be evaluated.
    :return: A credibility score from 0 (very low credibility) to 1 (very high credibility).
        Returns -1 if the webpage could not be parsed, and -2 if it could not be evaluated.
    """

    data = parser.parse_data(url)

    # check for valid data
    if data is None or not re.search(r"\b\w+\b", data.headline) or len(data.text) < 50:
        print("Webpage parsing failed.")
        return -1

    scores = {}
    weight_sum = 0
    final_score = 0

    # compute sub-scores and sum up overall score via linear combination
    for signal_name, signal in evaluation_signals.items():
        score = signal.evaluator(data)
        scores[signal_name] = score
        weight = signal.weight if not signal.alt_condition(score) else signal.alt_weight
        final_score += score * weight
        weight_sum += weight

    # check for valid scores
    if (scores is None or len(scores) != len(evaluation_signals)
            or not all(0 <= score <= 1 for score in scores.values())):
        print("Computation of sub-scores failed.")
        log(scores)
        return -2

    log("[Evaluation] Individual sub-scores: {}".format(
        [signal_name + " {}".format(round(score, 3)) for signal_name, score in scores.items()]))

    return final_score / weight_sum
