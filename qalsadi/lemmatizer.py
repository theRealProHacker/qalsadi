from . import analex
from . import stemnode


class Lemmatizer:
    """
    Arabic Lemmatizer
    """

    def __init__(self, vocalized_lemma=False):
        self.analexer = analex.Analex()
        self.vocalized_lemma = vocalized_lemma

    def lemmatize_text(self, text, return_pos=False, pos=""):
        stemnodelist = [
            stemnode.StemNode(stemming_list, self.vocalized_lemma)
            for stemming_list in self.analexer.check_text(text)
        ]
        lemmas = [
            stnd.get_lemma(pos=pos, return_pos=return_pos) for stnd in stemnodelist
        ]
        return lemmas

    def lemmatize(self, word, return_pos=False, pos=""):
        lemmas = self.lemmatize_text(word, return_pos=return_pos, pos=pos)
        if lemmas:
            return lemmas[0]

        return () if return_pos else ""
