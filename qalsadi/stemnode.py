from collections import Counter


import pyarabic.araby as araby
from .wordcase import WordCase
from .stemmedword import StemmedWord


def ispunct(word):
    return word in "!\"#$%&'()*+,-./:;<=>?@[\\]^_`{|}~،؟"


def most_frequent(l: list):
    occurence_count = Counter(sorted(l))
    return occurence_count.most_common(1)[0][0]


class StemNode:
    def __init__(self, case_list, vocalized_lemma=False):
        """
        Create the stemNode  from a list of StemmedSynword cases
        """
        # option to handle vocalized lemmas
        self.vocalized_lemma = vocalized_lemma
        self.case_count = len(case_list)

        # convert the case list into StemmedSynword
        tmp_case_list = []
        for case in case_list:
            if isinstance(case, WordCase):
                tmp_case_list.append(StemmedWord(case))
            else:
                tmp_case_list.append(case)
        case_list = tmp_case_list

        # ~""" the number of syntaxtical cases """
        # ~ print("case_list", len(case_list))
        self.word = ""
        # ~""" The unstemmed word """
        self.previous_nodes = {}
        # the  syntaxical previous nodes
        self.next_nodes = {}
        # the  syntaxical next nodes
        self.vocalizeds = []
        if case_list:
            self.vocalizeds = [case.get_vocalized() for case in case_list]
            self.vocalizeds = list(set(self.vocalizeds))
            self.vocalizeds.sort()

        self.tags = []
        if case_list:
            self.tags = [case.get_tags() + ":" + case.get_type() for case in case_list]
            self.tags = list(set(self.tags))
            self.tags.sort()

        # the  affixs  list
        self.affixes = []
        if case_list:
            self.affixes = [case.get_affix() for case in case_list]
            self.affixes = list(set(self.affixes))
            self.affixes.sort()

        # the  roots  list
        self.roots = []
        if case_list:
            self.roots = [case.get_root() for case in case_list]
            self.roots = list(set(self.roots))
            self.roots.sort()

        # ~ all vocalized forms
        self.originals = {}
        # ~ Orginals word from dictionary
        # will be used to extarct semantic relations
        self.guessed_type_tag = ""
        # guessed word type tag given by the word tagger
        self.break_end = False
        # the break position at the end or at the begining
        # the punctuation is an end break
        # a stop word is a start break

        self.lemmas = {
            "verb": [],
            "noun": [],
            "punct": [],
            "stopword": [],
            "all": [],
        }
        self.word_type = {
            "verb": [],
            "noun": [],
            "punct": [],
            "stopword": [],
        }
        self.count = {
            "verb": [],
            "noun": [],
            "punct": [],
            "stopword": [],
        }
        # word type count after analysis
        self.breaks = []
        self.non_breaks = []
        self.syntax_mark = {
            "mansoub": [],
            "marfou3": [],
            "majrour": [],
            "majzoum": [],
            "tanwin_mansoub": [],
            "tanwin_marfou3": [],
            "tanwin_majrour": [],
        }
        self.syn_previous = {}  # generate dict for whole list of cases
        # the syntaxic previous of cases after syntax analysis
        self.syn_nexts = {}  # generate dict for whole list of cases
        # the syntaxic nexts of cases after syntax analysis
        self.sem_previous = {}  # generate dict for whole list of cases
        # the semantic previous of cases after semantic analysis
        self.sem_nexts = {}  # generate dict for whole list of cases
        # the semantic nexts of cases after semantic analysis

        self.chosen_indexes = list(range(len(case_list)))
        # ~ print("chosen indexes", self.chosen_indexes, len(self.chosen_indexes), len(case_list))
        # used to choose specific cases

        # ~""" The list of original words"""
        if case_list:
            self.word = case_list[0].get_word()

        for idx, case in enumerate(case_list):
            # extract originals lists
            # ~ idx = case.order
            # ~ idx = case.order
            if case.get_original() in self.originals:
                self.originals[case.get_original()].append(idx)
            else:
                self.originals[case.get_original()] = [
                    idx,
                ]
            # indexing by word type
            if case.is_verb():
                self.word_type["verb"].append(idx)
                self.lemmas["verb"].append(case.get_original())
            if case.is_noun():
                self.word_type["noun"].append(idx)
                self.lemmas["noun"].append(case.get_original())
            if case.is_stopword():
                self.word_type["stopword"].append(idx)
                self.lemmas["stopword"].append(case.get_original())
            if case.is_punct():
                self.word_type["punct"].append(idx)
                self.lemmas["punct"].append(case.get_original())
            # indexing break and non break word cases
            if case.is_break():
                self.breaks.append(idx)
            else:
                self.non_breaks.append(idx)
            if self.word and ispunct(self.word[0]):
                self.break_end = True
            # indexing by syntax mark and tanwin
            if case.is_tanwin():
                if case.is_mansoub():
                    self.syntax_mark["tanwin_mansoub"].append(idx)
                elif case.is_marfou3():
                    self.syntax_mark["tanwin_marfou3"].append(idx)
                elif case.is_majrour():
                    self.syntax_mark["tanwin_majrour"].append(idx)
            else:
                if case.is_mansoub():
                    self.syntax_mark["mansoub"].append(idx)
                elif case.is_marfou3():
                    self.syntax_mark["marfou3"].append(idx)
                elif case.is_majrour():
                    self.syntax_mark["majrour"].append(idx)
                elif case.is_majzoum():
                    self.syntax_mark["majzoum"].append(idx)
            # ~ # get all syntaxic relations
            # ~ if case.has_previous():
            # ~ self.syn_previous[idx] = case.get_previous()
            # ~ if case.has_next():
            # ~ self.syn_nexts[idx] = case.get_next()
            # ~ if case.has_sem_previous():
            # ~ self.sem_previous[idx] = case.get_sem_previous()
            # ~ if case.has_sem_next():
            # ~ self.sem_nexts[idx] = case.get_sem_next()

        self.count = {
            "verb": len(self.word_type["verb"]),
            # ~""" the number of syntaxtical verb cases """
            "noun": len(self.word_type["noun"]),
            # ~""" the number of syntaxtical noun cases """
            "stopword": len(self.word_type["stopword"]),
            # ~""" the number of syntaxtical stopword cases """
            "punct": len(self.word_type["punct"]),
        }
        # cleans lemmas
        self.lemmas["all"] = self.originals.keys()
        for type_key in self.lemmas:
            # remove duplicates
            self.lemmas[type_key] = list(set(self.lemmas[type_key]))
            if self.vocalized_lemma:
                self.lemmas[type_key] = [l for l in self.lemmas[type_key] if type_key]
            else:
                self.lemmas[type_key] = [
                    araby.strip_tashkeel(l) for l in self.lemmas[type_key] if type_key
                ]

            # think that I sould keep repetition to use it as frequency to select lemma
            # remove duplicates after removing tashkeel
            # ~ self.lemmas[type_key] = list(set(self.lemmas[type_key]))

        # the sematic nexts of cases

    def get_lemmas(
        self,
    ):
        """
        Get all lemmas of the input word
        @return: the given lemmas list.
        @rtype: unicode string
        """
        originals = set(list(self.originals.keys()))
        if self.vocalized_lemma:
            lemmas = [l for l in originals]
        else:
            lemmas = [araby.strip_tashkeel(l) for l in originals]

        lemmas = list(set(lemmas))
        return lemmas

    def get_lemma(self, pos="", return_pos=False):
        """
        Get a lemma of the input word, you can select a POS tag (n,v,s)
        @return: the given lemmas list.
        @rtype: unicode string
        """
        # our strategy to select a lemma from many lemmas
        # if one return it
        # if it's a punct return it directly

        lemma = ""
        lemma_type = ""
        if self.lemmas.get("punct", []):
            lemma = most_frequent(self.lemmas["punct"])
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
            # select according to defined strategy
            for word_type in word_type_strategy:
                if self.lemmas.get(word_type, []):
                    lemma = most_frequent(self.lemmas[word_type])
                    lemma_type = word_type
                    break
        if not return_pos:
            return lemma
        else:
            return (lemma, lemma_type)

    def has_verb(
        self,
    ):
        """
        Return if all cases are verbs.
        @return:True if the node has verb in one case at least.
        @rtype:boolean
        """
        return self.count["verb"] > 0

    def has_noun(
        self,
    ):
        """
        Return if all cases are nouns.
        @return:True if the node has noun in one case at least.
        @rtype:boolean
        """
        return self.count["noun"] > 0

    def has_stopword(
        self,
    ):
        """
        Return if all cases are stopwords.
        @return:True if the node has stopword in one case at least.
        @rtype:boolean
        """
        return self.count["stopword"] > 0

    def has_punct(
        self,
    ):
        """
        Return if all cases are punctuations
        @return:True if the node has punctation in one case at least.
        @rtype:boolean
        """
        return self.count["punct"] > 0

    def is_verb(
        self,
    ):
        """
        Return if all cases are verbs.
        @return: True if the node is verb in all cases.
        @rtype: boolean
        """
        return (
            self.count["verb"]
            and not self.count["punct"]
            and not self.count["stopword"]
            and not self.count["noun"]
        )

    def is_noun(
        self,
    ):
        """
        Return if all cases are nouns.
        @return: True if the node is noun in all cases.
        @rtype: boolean
        """
        return (
            not self.count["punct"]
            and not self.count["stopword"]
            and not self.count["verb"]
            and self.count["noun"]
        )

    def is_stopword(
        self,
    ):
        """
        Return if all cases are stopwords.
        @return: True if the node is stopword in all cases.
        @rtype: boolean
        """
        return (
            not self.count["punct"]
            and self.count["stopword"]
            and not self.count["verb"]
            and not self.count["noun"]
        )

    def is_punct(
        self,
    ):
        """
        Return if all cases are punctuations
        @return:True if the node is punctation in all cases.
        @rtype:boolean
        """
        return (
            self.count["punct"]
            and not self.count["stopword"]
            and not self.count["verb"]
            and not self.count["noun"]
        )

    def is_most_verb(
        self,
    ):
        """
        Return True if most  cases are verbs.
        @return:True if the node is verb in most cases.
        @rtype:boolean
        """

        return (
            self.count["verb"] > self.count["noun"]
            and self.count["verb"] > self.count["stopword"]
        )

    def is_most_noun(
        self,
    ):
        """
        Return True if most  cases are nouns.
        @return:True if the node is noun in most cases.
        @rtype:boolean
        """
        return (
            self.count["noun"] > self.count["verb"]
            and self.count["noun"] > self.count["stopword"]
        )

    def is_most_stopword(
        self,
    ):
        """
        Return True if most cases are stopwords.
        @return:True if the node is stopword in most cases.
        @rtype:boolean
        """
        return (
            self.count["stopword"] > self.count["verb"]
            and self.count["stopword"] > self.count["noun"]
        )

    def get_word_type(
        self,
    ):
        """
        Return the word type.
        @return:the word type or mosttype.
        @rtype:string
        """
        if self.is_noun():
            return "noun"
        elif self.is_verb():
            return "verb"
        elif self.is_stopword():
            return "stopword"
        elif self.is_punct():
            return "punct"
        elif self.is_most_noun():
            return "mostnoun"
        elif self.is_most_verb():
            return "mostverb"
        elif self.is_most_stopword():
            return "moststopword"
        else:
            return "ambiguous"

    def get_break_type(
        self,
    ):
        """
        Return the word break type,
        if the word break the sentences or not.
        @return:the word type or mosttype.
        @rtype:string
        """
        # ~if len(self.breaks) == 0 and len(self.non_breaks) == 0 :
        # ~return 'ambiguous'
        # ~elif
        if self.breaks and not self.non_breaks:
            return "break"
        # إذا كانت الكلمة مستبعدة ولم يكن لها علاقة دلالية بما قبلها
        elif self.has_stopword() and not self.sem_previous and not self.sem_nexts:
            return "break"
        elif self.non_breaks and not self.breaks:
            return "non_break"
        elif len(self.non_breaks) > len(self.breaks):
            return "mostNon_break"
        elif len(self.non_breaks) < len(self.breaks):
            return "most_break"
        else:
            return "ambiguous"

    def is_break_end(
        self,
    ):
        """
        The syn node is break end like puctuation, if it  hasn't any syntaxique or semantique
        relation with the previous word
        """

        return self.break_end

    def is_break(
        self,
    ):
        """
        The syn node is break, if it hasn't any syntaxique or semantique
        relation with the previous word
        """
        # ~ return not self.syn_previous and not self.sem_previous #or self.get_break_type() == "break"
        return self.get_break_type() in ("break", "mostBreak")

    def __repr__(self):
        text = "\n'%s':%s, [%s-%s]{V:%d, N:%d, S:%d} " % (
            self.__dict__["word"],
            ", ".join(self.originals),
            self.get_word_type(),
            self.get_break_type(),
            self.count["verb"],
            self.count["noun"],
            self.count["stopword"],
        )
        text += repr(self.syntax_mark)
        text += repr(self.word_type)
        text += repr(self.originals)
        text += "Indexes : " + repr(self.chosen_indexes)
        return text
