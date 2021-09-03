import logging

import _readability as readability
import stats_collector as stats
from parsing.webpage_data import WebpageData

logger = logging.getLogger("alpaca")


def evaluate_readability(data: WebpageData) -> float:
    """Evaluates the readability of a webpage's text body by averaging several common readability grades.

    Computes the average of the Flesch-Kincaid grade, Flesch reading ease, Gunning-Fog, SMOG, ARI and Coleman-Liau
    readability scores of the webpage's text.

    :return: Combined readability score between 0 and 1, with 0 indicating easy understandability (low text complexity)
        and 1 indicating hard understandability (high text complexity).
    """

    # TODO decide on best-performing readability grades as indicators of credibility (+documentation)
    # TODO then create constants for score scaling instead of in-method

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

    # preliminary scoring: assign highest credibility for complex text, equivalent to 11th-grade reading level
    # Flesch-Kincaid grade level score range 1-17, 11-17 best
    # Flesch reading ease score range 1-100, 1-50 best
    # Gunning-Fog score range 1-17, 11-17 best
    # SMOG score range 5-22, 16-22 best
    # ARI score range 1-14, 11-14 best
    # Coleman-Liau score range 1-17, 11-17 best
    readability_scores = [(11 - read_metrics["readability grades"]["Kincaid"]) / 10,
                          1 - ((100 - read_metrics["readability grades"]["FleschReadingEase"]) / 50),
                          (11 - read_metrics["readability grades"]["GunningFogIndex"]) / 10,
                          (16 - read_metrics["readability grades"]["SMOGIndex"]) / 11,
                          (11 - read_metrics["readability grades"]["ARI"]) / 10,
                          (11 - read_metrics["readability grades"]["Coleman-Liau"]) / 10]

    for index, score in enumerate(readability_scores):
        readability_scores[index] = 1 - max(min(score, 1), 0)
    logger.debug("[Readability] Readability scores text: {}".format([round(score, 3) for score in readability_scores]))

    return sum(readability_scores) / len(readability_scores)
