import nltk

import _readability as readability
from logger import log
from parsing.website_data import WebsiteData
from parsing.website_parser import has_ending_punctuation


def evaluate_readability(data: WebsiteData) -> float:
    """Evaluates readability of the website's text. TODO further documentation

    :param data: Parsed website data necessary for credibility evaluation.
    :return: TODO.
    """

    headline_period = "" if has_ending_punctuation(data.headline) else ". "
    full_text = (data.headline + headline_period + data.text).replace("\n", " ")
    sent_tokeniser = nltk.data.load('tokenizers/punkt/english.pickle')
    tokens = sent_tokeniser.tokenize(full_text, realign_boundaries=True)
    log("*** {} sentence tokens".format(len(tokens)))

    metrics = readability.getmeasures(tokens, lang="en")
    log("*** Text properties: "
        "{} chr | {} syl | {} wrd | {} pag | "
        "{:.3f} cpw | {:.3f} spw | {:.3f} wps | {:.3f} spp | "
        "{} w_t | {} l_w | {} c_w"
        .format(metrics["sentence info"]["characters"],
                metrics["sentence info"]["syllables"],
                metrics["sentence info"]["words"],
                data.text.count("\n") + 1,
                metrics["sentence info"]["characters_per_word"],
                metrics["sentence info"]["syll_per_word"],
                metrics["sentence info"]["words_per_sentence"],
                metrics["sentence info"]["sentences_per_paragraph"],
                metrics["sentence info"]["wordtypes"],
                metrics["sentence info"]["long_words"],
                metrics["sentence info"]["complex_words"]))
    log("*** Readability metrics: "
        "Fl-Ki grade {:.3f} | Fl-Ki reading ease {:.3f} | G-Fog {:.3f} | SMOG {:.3f} | ARI {:.3f} | C-Liau {:.3f}"
        .format(metrics["readability grades"]["Kincaid"],
                metrics["readability grades"]["FleschReadingEase"],
                metrics["readability grades"]["GunningFogIndex"],
                metrics["readability grades"]["SMOGIndex"],
                metrics["readability grades"]["ARI"],
                metrics["readability grades"]["Coleman-Liau"],))
    return 1.0
