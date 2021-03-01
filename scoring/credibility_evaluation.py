import parsing.website_parser as parser
from logger import log
from parsing.website_data import WebsiteData
from scoring.evaluator_authors import evaluate_authors
from scoring.evaluator_grammar import evaluate_grammar
from scoring.evaluator_readability import evaluate_readability

# weights for the linear combination of individual signal scores
EVALUATION_WEIGHTS = {"grammar": 0.3,
                      "authors": 0.2,
                      "readability": 1.0}


def _compute_scores(data: WebsiteData) -> dict[str, float]:
    """Given a website's information, collects corresponding credibility scores from different signal evaluators.

    :param data: All necessary parsed data from the website to be evaluated.
    :return: A list of credibility scores for the website from all the evaluators. Values range from 0 (very low
        credibility) to 1 (very high credibility). A value of -1 means that particular credibility score could not be
        computed.
    """

    # TODO multithreading/optimise performance?
    scores = {"grammar": evaluate_grammar(data),
              "authors": evaluate_authors(data),
              "readability": evaluate_readability(data)}
    return scores


def evaluate_website(url: str) -> float:
    """Scores a website's credibility from 0 to 1 by combining the credibility scores of different evaluators.

    :param url: URL of the website to be evaluated.
    :return: A credibility score from 0 (very low credibility) to 1 (very high credibility).
        Returns -1 if the website could not be evaluated.
    """

    data = parser.parse_data(url)

    if data is None or data.headline == "" or data.text == "":
        print("Website parsing failed.")
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
