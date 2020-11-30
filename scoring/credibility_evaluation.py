import parsing.website_parser as parser
from parsing.website_data import WebsiteData
from scoring.evaluator_clickbait import evaluate_clickbait
from scoring.evaluator_grammar import evaluate_grammar

# weights for the linear combination of individual signal scores
EVALUATION_WEIGHTS = [0.5,  # grammar
                      0.5]  # clickbait


def _compute_scores(data: WebsiteData) -> list[float]:
    """Given a website's information, collects corresponding credibility scores from different signal evaluators."""
    scores = [evaluate_grammar(data),
              evaluate_clickbait(data)]
    return scores


def evaluate_website(url: str) -> float:
    """
    todo documentation

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
