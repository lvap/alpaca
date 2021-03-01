import re

import nltk.data

import _readability as readability
from logger import log
from parsing.webpage_data import WebpageData
from parsing.webpage_parser import has_ending_punctuation

# toggle some file-specific logging messages
LOGGING_ENABLED = True


def evaluate_readability(data: WebpageData) -> float:
    """Evaluates the webpage's readability by computing the Flesch-Kincaid grade level, Flesch reading ease,
    Gunning-Fog, SMOG, ARI and Coleman-Liau scores of its headline and main text.

    :param data: Parsed webpage data necessary for credibility evaluation.
    :return: Combined readability score between 0 and 1, 0 indicating easy understandability (low text complexity)
    and 1 indicating hard understandability (high text complexity).
    """

    headline_ending = "\n" if has_ending_punctuation(data.headline) else ".\n"
    # replace characters that are problematic for nltk.tokenize
    full_text = re.sub("[“‟„”«»❝❞⹂〝〞〟＂]", "\"",
                       re.sub("[‹›’❮❯‚‘‛❛❜❟]", "'", data.headline + headline_ending + data.text))
    sent_tokeniser = nltk.data.load('tokenizers/punkt/english.pickle')
    tokens = sent_tokeniser.tokenize(full_text, realign_boundaries=True)
    log("*** {} sentence tokens".format(len(tokens)), LOGGING_ENABLED)

    metrics = readability.getmeasures(tokens, lang="en")
    paragraph_count = data.text.count("\n") + 1

    log("*** Text properties: "
        "{} char | {} syll | {} word | {} pargr | "
        "{:.3f} char_p_w | {:.3f} syll_p_w | {:.3f} word_p_s | {:.3f} sent_p_p | "
        "{} wrd_typ | {} long_wrd | {} compl_wrd"
        .format(metrics["sentence info"]["characters"],  # alphanumeric symbols and hyphens (-)
                metrics["sentence info"]["syllables"],
                metrics["sentence info"]["words"],  # strings of alphanumerics and hyphens (isn't = 2 words)
                paragraph_count,
                metrics["sentence info"]["characters_per_word"],
                metrics["sentence info"]["syll_per_word"],
                metrics["sentence info"]["words_per_sentence"],
                metrics["sentence info"]["sentences"] / paragraph_count,
                metrics["sentence info"]["wordtypes"],
                metrics["sentence info"]["long_words"],
                metrics["sentence info"]["complex_words"]), LOGGING_ENABLED)
    log("*** Readability metrics: "
        "Fle-Kin grade {:.3f} | Fle reading ease {:.3f} | Gun-Fog {:.3f} | SMOG {:.3f} | ARI {:.3f} | Col-Liau {:.3f}"
        .format(metrics["readability grades"]["Kincaid"],
                metrics["readability grades"]["FleschReadingEase"],
                metrics["readability grades"]["GunningFogIndex"],
                metrics["readability grades"]["SMOGIndex"],
                metrics["readability grades"]["ARI"],
                metrics["readability grades"]["Coleman-Liau"], ))

    # preliminary scoring: assign highest credibility for complex text, equivalent to  11th-grade reading level
    # Flesch-Kincaid grade level score range 1-17, 11-17 best
    # Flesch reading ease score range 1-100, 1-50 best
    # Gunning-Fog score range 1-17, 11-17 best
    # SMOG score range 5-22, 16-22 best
    # ARI score range 1-14, 11-14 best
    # Coleman-Liau score range 1-17, 11-17 best
    readability_scores = [(11.0 - metrics["readability grades"]["Kincaid"]) / 10.0,
                          1.0 - ((100.0 - metrics["readability grades"]["FleschReadingEase"]) / 50.0),
                          (11.0 - metrics["readability grades"]["GunningFogIndex"]) / 10.0,
                          (16.0 - metrics["readability grades"]["SMOGIndex"]) / 11.0,
                          (11.0 - metrics["readability grades"]["ARI"]) / 10.0,
                          (11.0 - metrics["readability grades"]["Coleman-Liau"]) / 10.0]

    for index, score in enumerate(readability_scores):
        if score < 0:
            readability_scores[index] = 0.0
        elif score > 1:
            readability_scores[index] = 1.0
    log("*** Readability scores: {}".format([round(score, 3) for score in readability_scores]), LOGGING_ENABLED)

    final_score = 1.0 - (sum(readability_scores) / len(readability_scores))
    return final_score
