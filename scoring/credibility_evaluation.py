import parsing.webpage_parser as parser
from logger import log
from parsing.webpage_data import WebpageData
from scoring.evaluator_authors import evaluate_authors
from scoring.evaluator_grammar import evaluate_grammar
from scoring.evaluator_readability import evaluate_readability
from scoring.evaluator_clickbait import evaluate_clickbait

# weights for the linear combination of individual signal scores
EVALUATION_WEIGHTS = {"grammar": 0.3,
                      "authors": 0.2,
                      "readability": 1.0,
                      "clickbait": 0.0}


def _compute_scores(data: WebpageData) -> dict[str, float]:
    """Given a webpage's information, collects corresponding credibility scores from different signal evaluators.

    :param data: All necessary parsed data from the webpage to be evaluated.
    :return: A list of credibility scores for the webpage from all the evaluators. Values range from 0 (very low
        credibility) to 1 (very high credibility). A value of -1 means that particular credibility score could not be
        computed.
    """

    # TODO multithreading/optimise performance?
    scores = {"grammar": evaluate_grammar(data),
              "authors": evaluate_authors(data),
              "readability": evaluate_readability(data),
              "clickbait": evaluate_clickbait(data)}
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

    log("*** Individual scores: {}".format([round(score, 3) for score in scores.values()]))

    # linear combination of individual scores
    final_score = sum(scores.get(signal) * EVALUATION_WEIGHTS.get(signal) for signal in scores.keys())
    final_score /= sum(EVALUATION_WEIGHTS.values())

    return final_score
