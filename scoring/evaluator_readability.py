import logging

import _readability as readability
import stats_collector as stats
from parsing.webpage_data import WebpageData

logger = logging.getLogger("alpaca")

# value limits to compute subscore
READABILITY_LIMITS = [8, 12]


def evaluate_readability(data: WebpageData) -> float:
    """Evaluates the readability of a webpage's text body.

    Computes the Coleman-Liau readability grade and scales linearly between a grade of **READABILITY_LIMITS[0]** or
    less (worst score => 0) and **READABILITY_LIMITS[1]** or more (best score => 1).

    :return: Readability score between 0 and 1, with 0 indicating easy understandability (low text complexity)
        and 1 indicating hard understandability (high text complexity).
    """

    read_metrics = readability.getmeasures(data.text_sentences, lang="en")
    coleman_liau = read_metrics["readability grades"]["Coleman-Liau"]

    logger.debug("[Readability] Readability grade (Coleman-Liau): {:.3f}".format(coleman_liau))
    stats.add_result(data.url, "readability_coleman_liau", coleman_liau)

    read_score = (coleman_liau - READABILITY_LIMITS[0]) / (READABILITY_LIMITS[1] - READABILITY_LIMITS[0])
    return min(max(read_score, 0), 1)
