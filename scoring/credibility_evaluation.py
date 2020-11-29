import parsing.website_parser as parser
from parsing.website_data import WebsiteData

from scoring.grammar import evaluate_grammar
from scoring.clickbait import evaluate_clickbait


# weights for the linear combination of individual signal scores
EVALUATION_WEIGHTS = [0.5,  # grammar
                      0.5]  # clickbait


def _compute_scores(data: WebsiteData) -> list[float]:
    """Collects the credibility scores from different signal evaluators given a website's information."""
    scores = [evaluate_grammar(data),
              evaluate_clickbait(data)]
    return scores


def evaluate_website(url: str) -> float:
    """
    TODO documentation

    :param url:
    :return:
    """
    try:
        data = parser.parse_data(url)

        scores = _compute_scores(data)
        print(scores)

        result = sum(score * weight for score, weight in zip(scores, EVALUATION_WEIGHTS))
        return result

    except ConnectionError:
        # website could not be parsed
        return -1.0
