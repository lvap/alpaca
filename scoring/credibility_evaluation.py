import re
from typing import NamedTuple, Callable

import parsing.webpage_parser as parser
from logger import log
from parsing.webpage_data import WebpageData
from scoring.evaluator_authors import evaluate_authors
from scoring.evaluator_clickbait import evaluate_clickbait
from scoring.evaluator_grammar_spelling import evaluate_grammar_spelling
from scoring.evaluator_links import evaluate_links_external
from scoring.evaluator_readability import evaluate_readability_grades, evaluate_text_lengths
from scoring.evaluator_tonality import evaluate_exclamation_marks, evaluate_question_marks, evaluate_capitalisation
from scoring.evaluator_url import evaluate_domain_ending
from scoring.evaluator_vocabulary import evaluate_profanity


class CredibilitySignal(NamedTuple):
    """A webpage credibility signal, including its evaluator and weight functions.

    :param evaluator: Returns the signal sub-score given some webpage data. Between 0 - 1 unless extended_score is True
    :param weight_func: Returns weight to be used for this signal when combining all sub-scores into the overall webpage
    score, takes own sub-score as input.
    """
    evaluator: Callable[[WebpageData], float]
    weight_func: Callable[[float], float]


# TODO perhaps increased weight for low sub-scores?
# holds credibility signals: signal evaluator and weight functions
evaluation_signals = {
    "authors":                      CredibilitySignal(evaluate_authors,
                                                      lambda score: 0.3),
    "url_domain_ending":            CredibilitySignal(evaluate_domain_ending,
                                                      lambda score: 0.2 if score == 1 else 0),
    "grammar_spelling":             CredibilitySignal(evaluate_grammar_spelling,
                                                      lambda score: 0.3 if score > 0.8 else 0.45),
    "tonality_question_marks":      CredibilitySignal(evaluate_question_marks,
                                                      lambda score: 0.2 if score > 0 else 0.3),
    "tonality_exclamation_marks":   CredibilitySignal(evaluate_exclamation_marks,
                                                      lambda score: 0.2 if score > 0.8 else 0.3 if score > 0 else 0.45),
    "tonality_capitalisation":      CredibilitySignal(evaluate_capitalisation,
                                                      lambda score: 0 if score > 0.8 else 0.3),
    "readability_grades":           CredibilitySignal(evaluate_readability_grades,
                                                      lambda score: 1),
    "readability_text_lengths":     CredibilitySignal(evaluate_text_lengths,
                                                      lambda score: 0.8),
    "vocabulary_profanity":         CredibilitySignal(evaluate_profanity,
                                                      lambda score: 0 if score == 1 else 1),
    "clickbait":                    CredibilitySignal(evaluate_clickbait,
                                                      lambda score: 0.3 if score > 0 else 0.8),
    "links_external":               CredibilitySignal(evaluate_links_external,
                                                      lambda score: 0.3 if score == 0 or score == 1 else 0)
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
    # TODO possibly parellelise different signal evaluation calls to improve performance
    for signal_name, signal in evaluation_signals.items():
        subscore = signal.evaluator(data)
        weight = signal.weight_func(subscore)
        scores[signal_name] = subscore
        final_score += subscore * weight
        weight_sum += weight

    # check for valid scores
    if (scores is None or len(scores) != len(evaluation_signals)
            or not all(0 <= score <= 1 for score in scores.values())):
        print("Computation of sub-scores failed.")
        log(scores)
        return -2

    log("[Evaluation] Individual sub-scores: {}".format(
        [signal_name + " {:.3f}".format(score) for signal_name, score in scores.items()]))

    return final_score / weight_sum
