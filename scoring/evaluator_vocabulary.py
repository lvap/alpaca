import logging
import re
from collections import defaultdict
from pathlib import Path

import pandas as pd

import stats_collector
from parsing.tokenize import word_tokenize
from parsing.webpage_data import WebpageData

# value limits for subscore computation
PROFANITY_LIMIT = 0.0000000001
EMOTION_LIMITS = [0.075, 0.125]

# boundary checks
if PROFANITY_LIMIT <= 0 or not 0 <= EMOTION_LIMITS[0] < EMOTION_LIMITS[1] <= 1:
    raise ValueError("A constant for vocabulary evaluation is set incorrectly")

logger = logging.getLogger("alpaca")


def evaluate_profanity(data: WebpageData) -> float:
    """Evaluates webpage by checking for occurrences of profanity.

    Combines and checks webpage headline and text. Profanity score is linear from 0 occurrences (best score => 1) to
    **PROFANITY_LIMIT** occurrences per word (worst score => 0).

    :return: Value between 1 (low profanity) and 0 (high profanity).
    """

    # file containing profanity/slurs, one entry per line
    profanity_list_path = "files/profanity.txt"
    filepath = (Path(__file__).parent / profanity_list_path).resolve()

    fulltext = data.headline.lower() + " " + data.text.lower()
    profanity_matches = defaultdict(int)

    with open(filepath, "r") as profanity_words:
        for line in profanity_words.readlines():
            if match := re.findall(r"\b" + line.strip() + r"\b", fulltext):
                profanity_matches[match[0]] += len(match)

    logger.debug("[Vocabulary] {} profanity matches: {}"
                 .format(len(profanity_matches),
                         ["{} ({}x)".format(slur, occurrences) for slur, occurrences in profanity_matches.items()]))
    stats_collector.add_result(data.url, "profanity", sum(profanity_matches.values()) / len(fulltext))

    score = sum(profanity_matches.values()) / (len(fulltext) * PROFANITY_LIMIT)
    return 1 - max(min(score, 1), 0)


def evaluate_emotional_words(data: WebpageData) -> float:
    """Evaluates the vocabulary used by the webpage for its emotionality.

    Compares all words in the headline and text against a list of emotional words with specified emotion intensity
    values. Sums up all intensity values for any matches, scales the total sum by word count. Final score is linear
    between **EMOTION_LIMITS[0]** total emotion intensity per word (best score => 1) and **EMOTION_LIMITS[1]** total
    emotion intensity per word (worst score => 0).

    Computes individual and overall emotion values (# words/total words and intensity per word) for comparison
    purposes.

    :return: Value between 0 (high emotionality) and 1 (low emotionality).
    """

    # using emotion intensity lexicon by Saif M.Mohammad https://saifmohammad.com/WebPages/AffectIntensity.htm

    # file containing words & their degree of association with 8 emotions, one entry per line, sorted alphabetically
    emotion_list_path = "files/emotion_intensity_list.csv"
    filepath = (Path(__file__).parent / emotion_list_path).resolve()
    emotional_words = pd.read_csv(filepath, sep=";")

    df_size = len(emotional_words)
    fulltext = word_tokenize(data.headline) + data.text_words
    textlength = len(fulltext)
    emotion_word_count = 0

    emotionality_results = {"anger":        {"count": 0, "intensity": 0},
                            "anticipation": {"count": 0, "intensity": 0},
                            "disgust":      {"count": 0, "intensity": 0},
                            "fear":         {"count": 0, "intensity": 0},
                            "sadness":      {"count": 0, "intensity": 0},
                            "joy":          {"count": 0, "intensity": 0},
                            "surprise":     {"count": 0, "intensity": 0},
                            "trust":        {"count": 0, "intensity": 0}}

    # lookup all words from article in emotional words list
    for article_word in fulltext:
        article_word = article_word.lower()
        match = emotional_words["word"].searchsorted(article_word)
        if match < df_size and emotional_words.iat[match, 0] == article_word:
            emotion_word_count += 1
            # get emotion intensity data for a word match
            for emotion, emotion_intensity in emotional_words.iloc[match, 1:].items():
                if emotion_intensity > 0:
                    emotionality_results[emotion]["count"] += 1
                    emotionality_results[emotion]["intensity"] += emotion_intensity

    emotion_intensity_sum = sum(emotion_stats["intensity"] for emotion_stats in emotionality_results.values())
    emotion_intensity = emotion_intensity_sum / textlength
    emotion_word_ratio = emotion_word_count / textlength

    logger.debug("[Vocabulary] Emotionality results: {}".format(
        ["{}: {} words, {:.3f} intensity, {:.3f} words/total words ratio, {:.3f} intensity/words ratio".format(
            emotion, emotion_stats["count"], emotion_stats["intensity"], emotion_stats["count"] / textlength,
            emotion_stats["intensity"] / textlength)
         for emotion, emotion_stats in emotionality_results.items()]))
    logger.debug("[Vocabulary] Emotionality overall: {} words | {:.3f} emotional words per total words"
                 " | {:.3f} intensity per word".format(emotion_word_count, emotion_word_ratio, emotion_intensity))

    stats_collector.add_result(data.url, "total_emotion_word_ratio", emotion_word_ratio)
    for emotion in emotionality_results.keys():
        stats_collector.add_result(data.url, emotion + "_word_ratio",
                                   emotionality_results[emotion]["count"] / textlength)
        stats_collector.add_result(data.url, emotion + "_intensity",
                                   emotionality_results[emotion]["intensity"] / textlength)

    emotion_score = (emotion_intensity - EMOTION_LIMITS[0]) / (EMOTION_LIMITS[1] - EMOTION_LIMITS[0])
    emotion_score = max(min(emotion_score, 1), 0)
    return 1 - emotion_score
