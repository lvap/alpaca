import parsing.website_parser as parser

from scoring.grammar import evaluate_grammar
from scoring.clickbait import evaluate_clickbait


class CredibilityEvaluator:
    evaluator_weights = [0.5,  # grammar
                         0.5]  # clickbait

    def __init__(self):
        self.data = None

    def evaluate_website(self, url: str) -> float:
        self.get_data(url)

        scores = []
        scores[0] = evaluate_grammar(self.data)
        scores[1] = evaluate_clickbait(self.data)
        print(scores)

        result = sum(score * weight for score, weight in zip(scores, self.evaluator_weights))
        return result

    def get_data(self, url: str):
        self.data = parser.parse_data(url)
