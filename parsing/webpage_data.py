from parsing.tokenize import word_tokenize, sent_tokenize


class WebpageData:
    """Holds parsed webpage information.

    :param html: The complete webpage as html object.
    :param headline: The article/page title.
    :param text: The webpage's main text body.
    :param authors: The article authors.
    :param url: The webpage's URL.
    :param text_sentences: The article text's tokenized sentences.
    :param text_words: The article text's tokenized words.
    """

    def __init__(self,
                 html: str = "",
                 headline: str = "",
                 text: str = "",
                 authors: list[str] = [],
                 url: str = "",
                 text_sentences: list[str] = None,
                 text_words: list[str] = None):
        self.html = html
        self.headline = headline
        self.text = text
        self.authors = authors
        self.url = url
        self.text_sentences = text_sentences or sent_tokenize(text)
        self.text_words = text_words or word_tokenize(text)
