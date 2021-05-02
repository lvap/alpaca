import re

import nltk.data

import _readability as readability
from logger import log
from parsing.webpage_data import WebpageData
from parsing.webpage_parser import has_ending_punctuation

# toggle some file-specific logging messages
LOGGING_ENABLED = False


def evaluate_readability(data: WebpageData) -> float:
    """Evaluates the readability of a webpage..

    Computes and combines (with equal weight) the Flesch-Kincaid grade level, Flesch reading ease,
    Gunning-Fog, SMOG, ARI and Coleman-Liau scores of the webpage headline and main text.

    :return: Combined readability score between 0 and 1, 0 indicating easy understandability (low text complexity)
        and 1 indicating hard understandability (high text complexity).
    """

    headline_ending = "\n" if has_ending_punctuation(data.headline) else ".\n"
    # replace characters that are problematic for nltk.tokenize
    full_text = re.sub("[“‟„”«»❝❞⹂〝〞〟＂]", "\"",
                       re.sub("[‹›’❮❯‚‘‛❛❜❟]", "'", data.headline + headline_ending + data.text))
    sent_tokeniser = nltk.data.load('tokenizers/punkt/english.pickle')
    tokens = sent_tokeniser.tokenize(full_text, realign_boundaries=True)
    log("[Readability] {} sentence tokens".format(len(tokens)), LOGGING_ENABLED)

    read_metrics = readability.getmeasures(tokens, lang="en")
    paragraph_count = data.text.count("\n") + 1

    log("[Readability] Text properties: "
        "{} char | {} syll | {} word | {} pargr | "
        "{:.3f} char_p_w | {:.3f} syll_p_w | {:.3f} word_p_s | {:.3f} sent_p_p | "
        "{} wrd_typ | {} long_wrd | {} compl_wrd"
        .format(read_metrics["sentence info"]["characters"],  # alphanumeric symbols and hyphens (-)
                read_metrics["sentence info"]["syllables"],
                read_metrics["sentence info"]["words"],  # strings of alphanumerics and hyphens (isn't = 2 words)
                paragraph_count,
                read_metrics["sentence info"]["characters_per_word"],
                read_metrics["sentence info"]["syll_per_word"],
                read_metrics["sentence info"]["words_per_sentence"],
                read_metrics["sentence info"]["sentences"] / paragraph_count,
                read_metrics["sentence info"]["wordtypes"],
                read_metrics["sentence info"]["long_words"],
                read_metrics["sentence info"]["complex_words"]), LOGGING_ENABLED)
    log("[Readability] Readability grades: "
        "Fle-Kin grade {:.3f} | Fle reading ease {:.3f} | Gun-Fog {:.3f} | SMOG {:.3f} | ARI {:.3f} | Col-Liau {:.3f}"
        .format(read_metrics["readability grades"]["Kincaid"],
                read_metrics["readability grades"]["FleschReadingEase"],
                read_metrics["readability grades"]["GunningFogIndex"],
                read_metrics["readability grades"]["SMOGIndex"],
                read_metrics["readability grades"]["ARI"],
                read_metrics["readability grades"]["Coleman-Liau"]), LOGGING_ENABLED)

    # FIXME incorporate total words, sentence length and paragraph length minimums in score

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
    log("[Readability] Readability scores: {}".format([round(score, 3) for score in readability_scores]))

    # lower median
    readability_scores.sort()
    return readability_scores[2]
