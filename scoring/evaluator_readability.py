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

    logger.debug("[Readability] Readability grades text: "
                 "Flesch-Kincaid grade {:.3f} | Flesch reading ease {:.3f} | "
                 "Gunning-Fog {:.3f} | SMOG {:.3f} | ARI {:.3f} | Coleman-Liau {:.3f}"
                 .format(read_metrics["readability grades"]["Kincaid"],
                         read_metrics["readability grades"]["FleschReadingEase"],
                         read_metrics["readability grades"]["GunningFogIndex"],
                         read_metrics["readability grades"]["SMOGIndex"],
                         read_metrics["readability grades"]["ARI"],
                         read_metrics["readability grades"]["Coleman-Liau"]))
    stats.add_result(data.url, "read_text_flesch_kincaid", read_metrics["readability grades"]["Kincaid"])
    stats.add_result(data.url, "read_text_flesch_read_ease", read_metrics["readability grades"]["FleschReadingEase"])
    stats.add_result(data.url, "read_text_gunning_fog", read_metrics["readability grades"]["GunningFogIndex"])
    stats.add_result(data.url, "read_text_smog", read_metrics["readability grades"]["SMOGIndex"])
    stats.add_result(data.url, "read_text_ari", read_metrics["readability grades"]["ARI"])
    stats.add_result(data.url, "read_text_coleman_liau", read_metrics["readability grades"]["Coleman-Liau"])

    coleman_liau = read_metrics["readability grades"]["Coleman-Liau"]
    read_score = (coleman_liau - READABILITY_LIMITS[0]) / (READABILITY_LIMITS[1] - READABILITY_LIMITS[0])
    return min(max(read_score, 0), 1)
