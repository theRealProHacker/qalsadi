from collections import Counter

from . import analex
from .wordcase import WordCase
from .stemmedword import StemmedWord

import pyarabic.araby as araby


def ispunct(word):
    return word in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~،؟"


def most_frequent(l: list):
    occurence_count = Counter(sorted(l))
    return occurence_count.most_common(1)[0][0]


class Lemmatizer:
    """
    Arabic Lemmatizer
    """

    def __init__(self, vocalized_lemma=False):
        self.analexer = analex.Analex()
        self.vocalized_lemma = vocalized_lemma

    def get_lemma(self, case_list, return_pos=False, pos=""):
        case_list: list[StemmedWord] = [
            StemmedWord(case) if isinstance(case, WordCase) else case
            for case in case_list
        ]

        originals = {}

        lemmas = {
            "verb": [],
            "noun": [],
            "punct": [],
            "stopword": [],
            "all": [],
        }

        for i, case in enumerate(case_list):
            orig = case.original
            originals.setdefault(orig, [])
            originals[orig].append(i)
            if case.is_verb():
                lemmas["verb"].append(orig)
            if case.is_noun():
                lemmas["noun"].append(orig)
            if case.is_stopword():
                lemmas["stopword"].append(orig)
            if case.is_punct():
                lemmas["punct"].append(orig)

        # cleans lemmas
        lemmas["all"] = originals.keys()
        for type_key in lemmas:
            lemmas[type_key] = list(set(lemmas[type_key]))

        lemma = ""
        lemma_type = ""
        if lemmas.get("punct"):
            lemma = most_frequent(lemmas["punct"])
            lemma_type = "punct"
        else:
            # strategy to select lemmas
            word_type_strategy = ["stopword", "noun", "verb", "all"]

            if pos:
                pos = pos.lower()
                if pos in ("s", "stop_words", "stop_word"):
                    pos = "stopword"
                elif pos in ("n",):
                    pos = "noun"
                elif pos in (
                    "p",
                    "punct",
                ):
                    pos = "punct"
                elif pos in ("v",):
                    pos = "verb"
                else:
                    pos = "all"

                word_type_strategy = [
                    pos,
                ]
            for word_type in word_type_strategy:
                if lemmas.get(word_type):
                    lemma = most_frequent(lemmas[word_type])
                    lemma_type = word_type
                    break
        if not self.vocalized_lemma:
            lemma = araby.strip_tashkeel(lemma)
        return (lemma, lemma_type) if return_pos else lemma

    def lemmatize_text(self, text, return_pos=False, pos=""):
        checked_text = self.analexer.check_text(text)
        lemmas = [
            self.get_lemma(stemming_list, pos=pos, return_pos=return_pos)
            for stemming_list in checked_text
        ]
        return lemmas

    def lemmatize(self, word, return_pos=False, pos=""):
        lemmas = self.lemmatize_text(word, return_pos=return_pos, pos=pos)
        if lemmas:
            return lemmas[0]

        return () if return_pos else ""
