import logging
import re

from nltk import sent_tokenize

import _readability as readability
from testing import test
from parsing.webpage_data import WebpageData

logger = logging.getLogger("alpaca")


def evaluate_readability_text(data: WebpageData) -> float:
    """Evaluates the readability of a webpage's text body by averaging several common readability grades.

    Computes and combines (with equal weight) the Flesch-Kincaid grade level, Flesch reading ease,
    Gunning-Fog, SMOG, ARI and Coleman-Liau scores of the webpage headline and main text.

    :return: Combined readability score between 0 and 1, with 0 indicating easy understandability (low text complexity)
        and 1 indicating hard understandability (high text complexity).
    """

    # TODO analyse which readability grades perform best as indicators of credibility and exclude the others

    read_metrics = readability.getmeasures(data.text_sentences, lang="en")
    paragraph_count = data.text.count("\n") + 1

    logger.debug("[Readability] Readability grades text: "
                 "Flesch-Kincaid grade {:.3f} | Flesch reading ease {:.3f} | "
                 "Gunning-Fog {:.3f} | SMOG {:.3f} | ARI {:.3f} | Coleman-Liau {:.3f}"
                 .format(read_metrics["readability grades"]["Kincaid"],
                         read_metrics["readability grades"]["FleschReadingEase"],
                         read_metrics["readability grades"]["GunningFogIndex"],
                         read_metrics["readability grades"]["SMOGIndex"],
                         read_metrics["readability grades"]["ARI"],
                         read_metrics["readability grades"]["Coleman-Liau"]))
    test.add_result(data.url, "read_text_flesch_kincaid", read_metrics["readability grades"]["Kincaid"])
    test.add_result(data.url, "read_text_flesch_reading_ease", read_metrics["readability grades"]["FleschReadingEase"])
    test.add_result(data.url, "read_text_gunning_fog", read_metrics["readability grades"]["GunningFogIndex"])
    test.add_result(data.url, "read_text_smog", read_metrics["readability grades"]["SMOGIndex"])
    test.add_result(data.url, "read_text_ari", read_metrics["readability grades"]["ARI"])
    test.add_result(data.url, "read_text_coleman_liau", read_metrics["readability grades"]["Coleman-Liau"])

    # preliminary scoring: assign highest credibility for complex text, equivalent to  11th-grade reading level
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
    logger.info("[Readability] Readability scores text: {}".format([round(score, 3) for score in readability_scores]))

    # median (lower)
    readability_scores.sort()
    return readability_scores[2]


def evaluate_readability_title(data: WebpageData) -> float:
    """Evaluates the readability of a webpage's headline by averaging several common readability grades.

    Computes and combines (with equal weight) the Flesch-Kincaid grade level, Flesch reading ease,
    Gunning-Fog, SMOG, ARI and Coleman-Liau scores of the webpage headline and main text.

    :return: Combined readability score between 0 and 1, with 0 indicating easy understandability (low text complexity)
        and 1 indicating hard understandability (high text complexity).
    """

    # TODO analyse which readability grades perform best as indicators of credibility and exclude the others

    # tokenize headline, removing punctuation that is problematic for nltk.tokenize
    tokenized_title = sent_tokenize(re.sub("[“‟„”«»❝❞⹂〝〞〟＂]", "\"", re.sub("[‹›’❮❯‚‘‛❛❜❟]", "'", data.headline)))
    read_metrics = readability.getmeasures(tokenized_title, lang="en")
    paragraph_count = data.headline.count("\n") + 1

    logger.debug("[Readability] Readability grades title: "
                 "Flesch-Kincaid grade {:.3f} | Flesch reading ease {:.3f} | "
                 "Gunning-Fog {:.3f} | SMOG {:.3f} | ARI {:.3f} | Coleman-Liau {:.3f}"
                 .format(read_metrics["readability grades"]["Kincaid"],
                         read_metrics["readability grades"]["FleschReadingEase"],
                         read_metrics["readability grades"]["GunningFogIndex"],
                         read_metrics["readability grades"]["SMOGIndex"],
                         read_metrics["readability grades"]["ARI"],
                         read_metrics["readability grades"]["Coleman-Liau"]))
    test.add_result(data.url, "read_title_flesch_kincaid", read_metrics["readability grades"]["Kincaid"])
    test.add_result(data.url, "read_title_flesch_reading_ease", read_metrics["readability grades"]["FleschReadingEase"])
    test.add_result(data.url, "read_title_gunning_fog", read_metrics["readability grades"]["GunningFogIndex"])
    test.add_result(data.url, "read_title_smog", read_metrics["readability grades"]["SMOGIndex"])
    test.add_result(data.url, "read_title_ari", read_metrics["readability grades"]["ARI"])
    test.add_result(data.url, "read_title_coleman_liau", read_metrics["readability grades"]["Coleman-Liau"])

    # preliminary scoring: assign highest credibility for complex text, equivalent to  11th-grade reading level
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
    logger.info("[Readability] Readability scores title: {}".format([round(score, 3) for score in readability_scores]))

    # median (lower)
    readability_scores.sort()
    return readability_scores[2]
