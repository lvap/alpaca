import logging
import re
from pathlib import Path

import pandas as pd

from parsing.webpage_data import WebpageData

# modify profanity score gradient given this upper limit
MAX_PROFANITY = 3
# multiplier for emotion intensity per words ratio to modify final emotionality score
EMOTION_INTENSITY_MULTIPLIER = 2

# boundary checks
if MAX_PROFANITY <= 0 or EMOTION_INTENSITY_MULTIPLIER <= 0:
    raise ValueError("A constant for vacabulary evaluation is set incorrectly")

logger = logging.getLogger("alpaca")


def evaluate_profanity(data: WebpageData) -> float:
    """Evaluates webpage by checking for occurrences of profanity.

    Combines and checks webpage headline and text. Profanity score is linear from 0 occurrences (best score => 1) to
    *MAX_PROFANITY* occurrences (worst score => 0).

    :return: Value between 1 (low profanity) and 0 (high profanity).
    """

    # file containing profanity/slurs, one entry per line
    profanity_list_path = "../files/profanity.txt"
    filepath = (Path(__file__).parent / profanity_list_path).resolve()

    fulltext = data.headline.lower() + " " + data.text.lower()
    profanity_matches = {}

    with open(filepath, "r") as profanity_words:
        for line in profanity_words.readlines():
            if match := re.findall(r"\b" + line.strip() + r"\b", fulltext):
                if match[0] in profanity_matches:
                    profanity_matches[match[0]] += len(match)
                else:
                    profanity_matches[match[0]] = len(match)

    if profanity_matches:
        logger.info("[Vocabulary] Profanity matches: {}"
                    .format(["{} ({}x)".format(slur, occurrences) for slur, occurrences in profanity_matches.items()]))

    match_count = sum(profanity_matches.values())
    score = match_count / MAX_PROFANITY
    return 1 - min(score, 1)


def evaluate_emotional_words(data: WebpageData) -> float:
    """Evaluates the vocabulary used by the webpage for its emotionality.

    Compares all words in the headline and text against a list of emotional words with specified emotion intensity
    values. Sums up all intensity values for any matches, scales the total sum by word count. Final score is linear
    between 0 (worst score, words have on average at least 1 / *EMOTION_INTENSITY_MULTIPLIER* emotion intensity) and 1
    (best score, words have 0 emotion intensity on average).

    :return: Value between 0 (high emotionality) and 1 (low emotionality).
    """

    # TODO possibly limit scoring to some subset of emotions

    # file containing words & their degree of association with 8 emotions, one entry per line
    # using emotion intensity lexicon by Saif M. Mohammad https://saifmohammad.com/WebPages/AffectIntensity.htm
    emotion_list_path = "../files/emotion_intensity_list.csv"
    filepath = (Path(__file__).parent / emotion_list_path).resolve()
    emotional_words = pd.read_csv(filepath, sep=";")

    df_size = len(emotional_words)
    fulltext = data.headline.lower() + " " + data.text.lower()
    word_count = 0

    emotionality_results = {"anger": {"count": 0, "intensity": 0},
                            "anticipation": {"count": 0, "intensity": 0},
                            "disgust": {"count": 0, "intensity": 0},
                            "fear": {"count": 0, "intensity": 0},
                            "sadness": {"count": 0, "intensity": 0},
                            "joy": {"count": 0, "intensity": 0},
                            "surprise": {"count": 0, "intensity": 0},
                            "trust": {"count": 0, "intensity": 0}}

    # lookup all words from article in emotional words list
    for article_word in re.findall("[a-z]+", fulltext):
        word_count += 1
        match = emotional_words["word"].searchsorted(article_word)
        if match < df_size and emotional_words.iat[match, 0] == article_word:
            # get emotion intensity data for a word match
            for emotion, emotion_intensity in emotional_words.iloc[match, 1:].items():
                if emotion_intensity > 0:
                    emotionality_results[emotion]["count"] += 1
                    emotionality_results[emotion]["intensity"] += emotion_intensity

    total_emotion_count = sum(emotion_stats["count"] for emotion_stats in emotionality_results.values())
    total_emotion_intensity = sum(emotion_stats["intensity"] for emotion_stats in emotionality_results.values())

    logger.debug("[Vocabulary] Emotionality results: {}".format(
        ["{}: {} words, {:.3f} intensity".format(emotion, emotion_stats["count"], emotion_stats["intensity"])
         for emotion, emotion_stats in emotionality_results.items()]))
    logger.debug("[Vocabulary] Emotionality overall: {} words | {:.3f} intensity | {:.3f} intensity per word".format(
        total_emotion_count, total_emotion_intensity, total_emotion_intensity / word_count))

    emotion_score = (total_emotion_intensity * EMOTION_INTENSITY_MULTIPLIER) / word_count
    return max(1 - emotion_score, 0)
