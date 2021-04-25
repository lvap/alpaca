import re

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

# weights for the linear combination of individual signal scores
evaluation_weights = {"authors": 0.2,
                      "url_domain_ending": 0.2,
                      "grammar": 0.3,
                      "tonality_question_marks": 0.2,
                      "tonality_exclamation_marks": 0.3,
                      "tonality_capitalisation": 0.3,
                      "readability": 1,
                      "vocabulary_profanity": 0.5,
                      "clickbait": 0.3,
                      }

# variable to check  for legal length of score dictionary
mandatory_entries = 0


def _compute_scores(data: WebpageData) -> dict[str, float]:
    """Given data for a webpage, collects corresponding credibility scores from different evaluators.

    :param data: All necessary parsed data from the webpage to be evaluated.
    :return: A dictionary of credibility scores for the webpage from all the signal evaluators.
        Values range from 0 (very low credibility) to 1 (very high credibility).
        A negative value means that the particular credibility score could not be computed.
    """

    # TODO multithreading/optimise performance?
    # compute signal sub-scores
    scores = {"authors": evaluate_authors(data),
              "grammar": evaluate_grammar(data),
              "tonality_question_marks": evaluate_question_marks(data),
              "tonality_exclamation_marks": evaluate_exclamation_marks(data),
              "tonality_capitalisation": evaluate_capitalisation(data),
              "readability": evaluate_readability(data),
              "clickbait": evaluate_clickbait(data),
              }

    global mandatory_entries
    mandatory_entries = len(scores)

    if scores["clickbait"] == 0:
        # higher impact on score if headline is clickbait than if it is not
        evaluation_weights["clickbait"] = 1

    if (url_score := evaluate_domain_ending(data)) == 1:
        # domain ending evaluator can only improve score
        scores["url_domain_ending"] = url_score

    if 0 <= (profanity_score := evaluate_profanity(data)) < 1:
        # profanity evaluator can only decrease score
        scores["vocabulary_profanity"] = profanity_score

    return scores


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

    scores = _compute_scores(data)

    # check for valid scores
    if (scores is None or not mandatory_entries <= len(scores) <= len(evaluation_weights)
            or not all(0 <= score <= 1 for score in scores.values())):
        print("Computation of sub-scores failed.")
        log(scores)
        return -2

    log("[Evaluation] Individual scores: {}".format(
        [score_name + " {}".format(round(score, 3)) for score_name, score in scores.items()]))

    # TODO better formula to emphasise low scores?
    # linear combination of sub-scores
    final_score = sum(scores[signal] * evaluation_weights[signal] for signal in scores.keys())
    weight_sum = sum(evaluation_weights[signal] for signal in scores.keys())
    return final_score / weight_sum
