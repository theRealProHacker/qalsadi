import naftawayh.wordtag

DISAMBIGUATATION_TABLE = {
    # إذا كانت الكلمة الحالية "أن" تكون "أنْ" حرف نصب إذا سبقت فعلا
    # وتكون أنّ، من أخوات إنّ إذا كان ما بعدها اسما
    "أن": {
        "verb": {"tag": "t", "vocalized": "أَنْ"},
        "noun": {"tag": "t", "vocalized": "أَنَّ"},
        "previous": {
            # أنّ
            "غير": "أَنَّ",
            "لو": "أَنَّ",
            "لولا": "أَنَّ",
            "بما": "أَنَّ",
            "ربما": "أَنَّ",
            "لعل": "أَنَّ",
            "ليت": "أَنَّ",
            "إلا": "أَنَّ",
            "أم": "أَنَّ",
            "كما": "أَنَّ",
            "رغم": "أَنَّ",
            "بيد": "أَنَّ",
            "حتى": "أَنَّ",
            "بحجة": "أَنَّ",
            "ثم": "أَنَّ",
            "يعني": "أَنَّ",
            #                   'من': 'أَنَّ',
            "في": "أَنَّ",
            #                   'إلى': 'أَنَّ',
            # أنْ
            "هو": "أَنْ",
            "هي": "أَنْ",
            "إما": "أَنْ",
            "أو": "أَنْ",
            # ~ 'على':'أَنْ',
            "بلا": "أَنْ",
            "قبل": "أَنْ",
            "بعد": "أَنْ",
            "منذ": "أَنْ",
            "يجب": "أَنْ",
            "ينبغي": "أَنْ",
            "يمكن": "أَنْ",
            "يكاد": "أَنْ",
            "تكاد": "أَنْ",
            "كاد": "أَنْ",
            "عسى": "أَنْ",
            "يريد": "أَنْ",
            "تريد": "أَنْ",
            "أريد": "أَنْ",
            "أراد": "أَنْ",
            "أرادت": "أَنْ",
            "أوشك": "أَنْ",
            "أوشكت": "أَنْ",
        },
    },
    "إن": {
        "verb": {"tag": "t", "vocalized": "إِنْ"},
        "noun": {"tag": "t", "vocalized": "إِنَّ"},
        "previous": {
            # أنّ
            "والله": "إِنَّ",
            "ألا": "إِنَّ",
            "أما": "إِنَّ",
            "كلا": "إِنَّ",
            "حتى": "إِنَّ",
            # أنْ
            #   'هو':'إِنْ',
        },
    },
    # إذا كانت الكلمة الحالية "من" تكون "مَنْ" حرف استفهام  إذا سبقت فعلا
    # وتبقى ملتبسة إذا سبقت اسما.
    "من": {
        "verb": {"tag": "t", "vocalized": "مَنْ"},
        "noun": {"tag": "t", "vocalized": "ْمِن"},
    },
    # 'ثنا':{'abbr':'ثَنَا',}
}

class Disambiguator:
    """
    A class to remove ambiguation in text analysis
    """

    def __init__(
        self,
    ):
        self.tagger = naftawayh.wordtag.WordTagger()

    def disambiguate_words(self, word_list, tag_list):
        """
        Disambiguate some word according to tag guessing to reduce cases.
        return word list with dismbiguate.
        @param word_list: the given word lists.
        @type word_list: unicode list.
        @param tag_list: the given tag lists, produced by naftawayh
        @type tag_list: unicode list.
        @return: a new word list
        @rtype: unicode list
        """
        # print u" ".join(word_list).encode('utf8');
        # print u" ".join(tag_list).encode('utf8');

        if not word_list or len(word_list) != len(tag_list):
            # print "error"
            return word_list
        else:
            newwordlist = []
            wordtaglist = list(zip(word_list, tag_list))
            # print wordtaglist
            for i, wordtag in enumerate(wordtaglist):
                currentword = wordtag[0]
                # if the current exists in disambig table,
                if self.is_ambiguous(currentword):
                    if i - 1 >= 0:
                        previousword = wordtaglist[i - 1][0]
                    else:
                        previousword = ""
                    # disambiguate the word according the previous  word
                    tmpword = self.get_disambiguated_by_prev_word(
                        currentword, previousword
                    )
                    if tmpword != currentword:
                        currentword = tmpword
                    elif i + 1 < len(wordtaglist):
                        # print "*5"
                        nexttag = wordtaglist[i + 1][1]
                        # ~ nextword = wordtaglist[i + 1][0]
                        # if the next is similar to the expected tag,
                        # return vocalized word form
                        # test if expected tag is verb and
                        if self.tagger.is_verb_tag(
                            nexttag
                        ) and self.is_disambiguated_by_next_verb(currentword):
                            currentword = self.get_disambiguated_by_next_verb(
                                currentword
                            )
                        elif self.tagger.is_noun_tag(
                            nexttag
                        ) and self.is_disambiguated_by_next_noun(currentword):
                            currentword = self.get_disambiguated_by_next_noun(
                                currentword
                            )
                newwordlist.append(currentword)
            return newwordlist

    @staticmethod
    def is_ambiguous(word):
        """test if the word is an ambiguous case
        @param word: input word.
        @type word: unicode.
        @return : if word is ambiguous
        @rtype: True/False.
        """
        return word in DISAMBIGUATATION_TABLE

    @staticmethod
    def get_disambiguated_by_next_noun(word):
        """get The disambiguated form of the word by the next word is noun.
        The disambiguated form can be fully or partially vocalized.
        @param word: input word.
        @type word: unicode.
        @return : if word is ambiguous
        @rtype: True/False.
        """
        return (
            DISAMBIGUATATION_TABLE.get(word, {})
            .get("noun", {})
            .get("vocalized", word)
        )

    @staticmethod
    def get_disambiguated_by_prev_word(word, previous):
        """get The disambiguated form of the word by the previous.
        The disambiguated form can be fully or partially vocalized.
        @param word: input word.
        @type word: unicode.
        @param previous: input previous word.
        @type previous: unicode.
        @return : if word is ambiguous
        @rtype: True/False.
        """
        return (
            DISAMBIGUATATION_TABLE.get(word, {})
            .get("previous", {})
            .get(previous, word)
        )

    @staticmethod
    def get_disambiguated_by_next_word(word, w_next):
        """get The disambiguated form of the word by the next.
        The disambiguated form can be fully or partially vocalized.
        @param word: input word.
        @type word: unicode.
        @param next: input next word.
        @type next: unicode.
        @return : if word is ambiguous
        @rtype: True/False.
        """
        return (
            DISAMBIGUATATION_TABLE.get(word, {})
            .get("next", {})
            .get(w_next, word)
        )

    @staticmethod
    def get_disambiguated_by_next_verb(word):
        """get The disambiguated form of the word by the next word is a verb.
        The disambiguated form can be fully or partially vocalized.
        @param word: input word.
        @type word: unicode.
        @return : if word is ambiguous
        @rtype: True/False.
        """
        return (
            DISAMBIGUATATION_TABLE.get(word, {})
            .get("verb", {})
            .get("vocalized", word)
        )

    @staticmethod
    def is_disambiguated_by_next_noun(word):
        """test if the word can be disambiguated if the next word is a noun
        @param word: input word.
        @type word: unicode.
        @return : if word has an disambiguated.
        @rtype: True/False.
        """
        return "noun" in DISAMBIGUATATION_TABLE.get(word, {})  # .has_key('noun')

    @staticmethod
    def is_disambiguated_by_next_verb(word):
        """test if the word can be disambiguated if the next word is a verb
        @param word: input word.
        @type word: unicode.
        @return : if word has an disambiguated.
        @rtype: True/False.
        """
        return "verb" in DISAMBIGUATATION_TABLE.get(word, {})  # .has_key('verb')
