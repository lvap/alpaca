import parsing.webpage_parser as parser
from logger import log
from parsing.webpage_data import WebpageData
from scoring.evaluator_authors import evaluate_authors
# from scoring.evaluator_clickbait import evaluate_clickbait
from scoring.evaluator_grammar import evaluate_grammar
from scoring.evaluator_readability import evaluate_readability
from scoring.evaluator_tonality import evaluate_punctuation, evaluate_capitalisation

# weights for the linear combination of individual signal scores
EVALUATION_WEIGHTS = {"authors": 0.25,
                      "grammar": 0.25,
                      "tonality_punctuation": 0.3,
                      "tonality_capitalisation": 0.3,
                      "readability": 1.0,
                      # "clickbait": 0.0,
                      }


def _compute_scores(data: WebpageData) -> dict[str, float]:
    """Given a webpage's information, collects corresponding credibility scores from different signal evaluators.

    :param data: All necessary parsed data from the webpage to be evaluated.
    :return: A list of credibility scores for the webpage from all the evaluators. Values range from 0 (very low
        credibility) to 1 (very high credibility). A value of -1 means that particular credibility score could not be
        computed.
    """

    # TODO multithreading/optimise performance?
    scores = {"authors": evaluate_authors(data),
              "grammar": evaluate_grammar(data),
              "tonality_punctuation": evaluate_punctuation(data),
              "tonality_capitalisation": evaluate_capitalisation(data),
              "readability": evaluate_readability(data),
              # "clickbait": evaluate_clickbait(data),
              }
    return scores


def evaluate_webpage(url: str) -> float:
    """Scores a webpage's credibility from 0 to 1 by combining the credibility scores of different evaluators.

    :param url: URL of the webpage to be evaluated.
    :return: A credibility score from 0 (very low credibility) to 1 (very high credibility).
        Returns -1 if the webpage could not be evaluated.
    """

    data = parser.parse_data(url)

    if data is None or data.headline == "" or data.text == "":
        print("Webpage parsing failed.")
        return -1.0

    scores = _compute_scores(data)
    if scores is None or len(scores) is not len(EVALUATION_WEIGHTS):
        print("Computation of sub-scores failed.")
        return -1.0

    scores_to_print = ""
    for score_name, score in scores.items():
        scores_to_print += score_name + " {} | ".format(round(score, 3))
    log("*** Individual scores: " + scores_to_print[:-2])

    # linear combination of individual scores
    final_score = sum(scores[signal] * EVALUATION_WEIGHTS[signal] for signal in scores.keys())
    final_score /= sum(EVALUATION_WEIGHTS.values())

    return final_score
