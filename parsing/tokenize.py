import nltk
import regex as re
import spacy


def word_tokenize(text: str) -> list[str]:
    """Tokenizes text into words. Keeps full stops with abbreviations."""

    # convert all apostrophes to '
    text = re.sub("[‹›’❮❯‚‘‛❛❜❟]", "'", text)

    words = re.compile(r"\b(?:Mr|Ms|Mrs|vs|etc|Dr|Prof|Rev|Pres|Inc|Est|Dept|St|Blvd)\."  # common abbreviations
                       r"|\b(?:i\.(?=\se\.)|e\.(?=\sg\.)|P\.(?=\sS\.))"  # first part of i. e., e. g., P. S.
                       r"|(?<=\bi\.\s)e\.|(?<=\be\.\s)g\.|(?<=\bP\.\s)S\."  # second part of i. e., e. g., P. S.
                       r"|\b\d\d:\d\d(?::\d\d)?\b"  # time
                       r"|\b\d+(?:(?:\.\d+)+|(?:,\d+)+)?(?:[.,]\d+)?(?:\p{Sc}|\b)"  # numbers/monetary values
                       r"|(?:\b|\p{Sc})\d+(?:(?:\.\d+)+|(?:,\d+)+)?(?:[.,]\d+)?\b"  # numbers/monetary values
                       r"|\b(?:\w\.){2,}"  # abbreviations with alternating single letter/full stop
                       r"|\b\w+(?:[-']?\w+)*\b",  # normal words including hyphens and apostrophes
                       re.IGNORECASE)
    tokens = words.findall(text)

    # fix abbreviated names (single upper-case letters + full stop)
    nlp = spacy.load("en_core_web_sm")
    doc = nlp(text)
    entities = ["PERSON", "NORP", "FAC", "FACILITY", "ORG", "EVENT", "LAW"]
    names = set([ent.text for ent in doc.ents if ent.label_ in entities])
    for index, token in enumerate(tokens):
        if len(token) == 1 and token.upper() == token and any(token + "." in name.split() for name in names):
            tokens[index] = token + "."

    return tokens


def sent_tokenize(text: str) -> list[str]:
    """Tokenizes text into sentences using nltk.sent_tokenize."""

    # replace symbols that are problematic for nltk.tokenize
    text = re.sub("[“‟„”«»❝❞⹂〝〞〟＂]", "\"", re.sub("[‹›’❮❯‚‘‛❛❜❟]", "'", text))
    return nltk.sent_tokenize(text)
