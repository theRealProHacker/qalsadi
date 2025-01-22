import re
import pyarabic.araby as araby

import arramooz.wordfreqdictionaryclass as wordfreqdictionaryclass
import naftawayh.wordtag  # word tagger
import arabicstopwords.arabicstopwords as stopwords
from . import stem_noun  # noun stemming
from . import stem_verb  # verb stemming
from . import stem_unknown  # unknown word stemming
from . import stem_stop as stem_stopwords  # stopwords word stemming
from . import stem_punct_const  # punctaution constants
from . import disambig  # disambiguation const
from . import wordcase
from . import stemmedword  # the result object for stemming
from . import cache

PARTIAL_VOCALIZED_TAG = "مدخل مشكول"
# fields names and abbriviations

ANALEX_FIELDS_WORD = {
    "word": "w",
    "affix": "a",
    "procletic": "pp",
    "encletic": "ss",
    "prefix": "p",
    "suffix": "s",
    "stem": "st",
    "original": "o",
    "vocalized": "v",
    "semivocalized": "sv",
    "tags": "tg",
    "type": "t",
    "freq": "f",
    "originaltags": "ot",
    "syntax": "sy",
}


class Analex:
    """
    Arabic text morphological analyzer.
    Provides routins  to alanyze text.
    Can treat text as verbs or as nouns.
    """

    def __init__(
        self, cache_path=False, allow_tag_guessing=False, allow_disambiguation=True
    ):
        """
        Create Analex instance.
        """

        self.nounstemmer = stem_noun.NounStemmer()  # to stem nouns
        self.verbstemmer = stem_verb.VerbStemmer()  # to stem verbs
        self.unknownstemmer = stem_unknown.UnknownStemmer()
        # to stem unknown
        self.stopwordsstemmer = stem_stopwords.StopWordStemmer()
        # to stem stopwords

        self.allow_tag_guessing = allow_tag_guessing
        # ~ self.allow_tag_guessing = False
        # allow gueesing tags by naftawayh before analyis
        # if taggin is disabled, the disambiguation is also disabled
        self.allow_disambiguation = allow_disambiguation and allow_tag_guessing
        # allow disambiguation before analyis
        # enable the last mark (Harakat Al-I3rab)
        self.allow_syntax_lastmark = True
        if self.allow_tag_guessing:
            self.tagger = naftawayh.wordtag.WordTagger()
        if self.allow_disambiguation:
            self.disambiguator = disambig.Disambiguator()
        self.wordcounter = 0

        self.clause_pattern = re.compile(
            "([\w%s\s]+)" % ("".join(araby.TASHKEEL),), re.UNICODE
        )

        self.partial_vocalization_support = True

        self.wordfreq = wordfreqdictionaryclass.WordFreqDictionary(
            "wordfreq", wordfreqdictionaryclass.WORDFREQ_DICTIONARY_INDEX
        )

        self.allow_cache_use = False
        self.cache_path = cache_path
        if cache_path:
            self.cache = cache.Cache(cache_path)
        else:
            self.cache = None
        self.fully_vocalized_input = False
        self.error_code = ""
        self.wordfreq_cache = {}

    def __del__(self):
        """
        Delete instance and clear cache
        """
        self.wordfreq = None
        self.nounstemmer = None
        self.verbstemmer = None
        self.unknownstemmer = None
        self.stopwordsstemmer = None
        self.tagger = None
        self.disambiguator = None

    def get_freq(self, word, wordtype):
        """
        Return word_frequency
        """
        if word in self.wordfreq_cache:
            return self.wordfreq_cache[word]
        else:
            freq = self.wordfreq.get_freq(word, wordtype)
            self.wordfreq_cache[word] = freq
            return freq

    def tokenize(self, text=""):
        """
        Tokenize text into words
        @param text: the input text.
        @type text: unicode.
        @return: list of words.
        @rtype: list.
        """
        return araby.tokenize(text)

    def split_into_phrases(self, text):
        """
        Split Text into clauses
        @param text: input text
        @type text: unicode
        @return: list of clauses
        @rtype: list of unicode
        """
        if text:
            list_phrase = self.clause_pattern.split(text)
            if list_phrase:
                j = -1
                newlist = []
                for phr in list_phrase:
                    if not self.clause_pattern.match(phr):
                        # is punctuation or symboles
                        # print 'not match', ph.encode('utf8')
                        if j < 0:
                            # the symbols are in the begining
                            newlist.append(phr)
                            j = 0
                        else:
                            # the symbols are after a phrases
                            newlist[j] += phr
                    else:
                        newlist.append(phr)
                        j += 1
                return newlist
            else:
                return []
        return []

    def text_tokenize(self, text):
        """
        Tokenize text into words, after treatement.
        @param text: the input text.
        @type text: unicode.
        @return: list of words.
        @rtype: list.
        """
        list_word = self.tokenize(text)
        list_word = [word for word in list_word if word]
        return list_word

    def check_text(self, text, mode="all"):
        """
        Analyze text morphologically.
        @param text: the input text.
        @type text: unicode.
        @param mode: the mode of analysis as 'verbs', 'nouns', or 'all'.
        @type mode: unicode.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        list_word = self.text_tokenize(text)
        list_guessed_tag = [""] * len(list_word)
        if self.allow_tag_guessing:
            list_guessed_tag = self.tagger.word_tagging(list_word)
            if len(list_guessed_tag) != len(list_word):
                list_guessed_tag = ["nv"] * len(list_word)
        # disambiguate  some words to speed up the analysis
        if self.allow_disambiguation:
            newwordlist = self.disambiguator.disambiguate_words(
                list_word, list_guessed_tag
            )
            if len(newwordlist) == len(list_word):
                list_word = newwordlist

        resulted_data = []

        if mode == "all":
            for i in range(len(list_word)):
                word = list_word[i]
                guessedtag = list_guessed_tag[i]
                one_data_list = self.check_word(word, guessedtag)
                stemmed_one_data_list = [
                    stemmedword.StemmedWord(w) for w in one_data_list
                ]
                resulted_data.append(stemmed_one_data_list)
        elif mode == "nouns":
            for word in list_word:
                one_data_list = self.check_word_as_noun(word)
                stemmed_one_data_list = [
                    stemmedword.StemmedWord(w) for w in one_data_list
                ]
                resulted_data.append(stemmed_one_data_list)
                # ~ resulted_data.append(one_data_list)
        elif mode == "verbs":
            for word in list_word:
                one_data_list = self.check_word_as_verb(word)
                stemmed_one_data_list = [
                    stemmedword.StemmedWord(w) for w in one_data_list
                ]
                resulted_data.append(stemmed_one_data_list)
        return resulted_data

    def light_tag(self, word):
        """
        tag words as verbs or nouns according to some features
        Some letters are forbiden in some types like TehMarbuta in verbs
        """
        if stopwords.is_stop(word):
            return "stop"
        for c in word:
            if c in "إة":
                return "nonverb"
            if c in araby.TANWIN:
                return "nonverb"
        return ""

    def check_word(self, word, guessedtag=""):
        """
        Analyze one word morphologically as verbs
        @param word: the input word.
        @type word: unicode.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """

        word = araby.strip_tatweel(word)
        word_vocalised = word
        word_nm = araby.strip_tashkeel(word)
        word_nm_shadda = araby.strip_harakat(word)

        if self.allow_cache_use and self.cache.is_already_checked(word_nm):
            result = self.cache.get_checked(word_nm)
        else:
            result = []
            # if word is a punctuation
            result += self.check_word_as_punct(word_nm)
            # Done: if the word is a stop word we have  some problems,
            # the stop word can also be another normal word (verb or noun),
            # we must consider it in future works
            # if word is stopword allow stop words analysis
            if araby.is_arabicword(word_nm):
                if self.light_tag(word) == "stop":
                    result += self.check_word_as_stopword(word_nm)
                if self.allow_tag_guessing:
                    # 2nd method
                    # if word is a possible verb or just a stop word
                    # مشكلة بعض الكلمات المستبعدة تعتبر أفعلا أو اسماء
                    if self.tagger.has_verb_tag(
                        guessedtag
                    ) or self.tagger.is_stopword_tag(guessedtag):
                        result += self.check_word_as_verb(word_nm)
                    # if word is noun
                    if self.tagger.has_noun_tag(
                        guessedtag
                    ) or self.tagger.is_stopword_tag(guessedtag):
                        result += self.check_word_as_noun(word_nm)
                else:
                    # if word is verb
                    if self.light_tag(word) != "nonverb":
                        result += self.check_word_as_verb(word_nm)
                    # if word is noun
                    if self.light_tag(word) != "nonnoun":
                        result += self.check_word_as_noun(word_nm)

            if not result:
                # print (u"1 _unknown %s-%s"%(word, word_nm)).encode('utf8')
                # check the word as unkonwn
                result += self.check_word_as_unknown(word_nm)

            # ------- Filters used to reduce cases
            # 1- with normalized letters
            # 2- with given Shadda
            # 3- vocalized like
            # check if the word is nomralized and solution are equivalent
            result = self.check_normalized(word_nm, result)
            # check if the word is shadda like

            result = self.check_shadda(
                word_nm_shadda, result, self.fully_vocalized_input
            )

            # add word frequency information in tags
            result = self.add_word_frequency(result)

            # add the stemmed words details into Cache
            data_list_to_serialize = [w.__dict__ for w in result]
            if self.allow_cache_use:
                self.cache.add_checked(word_nm, data_list_to_serialize)

        # check if the word is vocalized like results
        if self.partial_vocalization_support:
            result = self.check_partial_vocalized(word_vocalised, result)

        if not result:
            result.append(
                wordcase.WordCase(
                    {
                        "word": word,
                        "affix": ("", "", "", ""),
                        "stem": word,
                        "original": word,
                        "vocalized": word,
                        "semivocalized": word,
                        "type": "unknown",
                        "root": "",
                        "template": "",
                        "freq": self.get_freq(word, "unknown"),
                        "syntax": "",
                    }
                )
            )
        return result

    def add_word_frequency(self, resulted_data):
        """
        If the entred word is like the found word in dictionary,
        to treat some normalized cases,
        the analyzer return the vocalized like words
        ُIf the word is ذئب, the normalized form is ذءب, which can give
        from dictionary ذئبـ ذؤب.
        this function filter normalized resulted word according the
        given word, and give ذئب.
        @param resulted_data: the founded resulat from dictionary.
        @type resulted_data: list of dict.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        for i, item in enumerate(resulted_data):
            original = item.original
            # in the freq attribute we found 'freqverb, or freqnoun,
            #  or a frequency for stopwords or unkown
            # the freqtype is used to note the wordtype,
            # this type is passed by stem_noun , or stem_verb modules
            freqtype = item.freq
            # ~ freqtype = item.get('freq', '')
            if freqtype == "freqverb":
                wordtype = "verb"
            elif freqtype == "freqnoun":
                wordtype = "noun"
            elif freqtype == "freqstopword":
                wordtype = "stopword"
            else:
                wordtype = ""
            if wordtype:
                # if frequency is already get from database,
                # don't access the database
                if self.allow_cache_use and self.cache.exists_cache_freq(
                    original, wordtype
                ):
                    item.freq = self.cache.get_freq(original, wordtype)

                else:
                    freq = self.get_freq(original, wordtype)
                    # ~print freq, wordtype, original.encode('utf8')
                    # store the freq in the cache
                    if self.allow_cache_use:
                        # ~ self.cache['FreqWords'][wordtype][original] = freq
                        self.cache.add_freq(original, wordtype, freq)

                    # ~ item.__dict__['freq'] = freq
                    # ~ item.__dict__['freq'] = freq
                    item.freq = freq
            resulted_data[i] = item
        return resulted_data

    def check_word_as_stopword(self, word):
        """
        Check if the word is a stopword,
        @param word: the input word.
        @type word: unicode.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        return self.stopwordsstemmer.stemming_stopword(word)

    def check_word_as_punct(self, word):
        """
        Check if the word is a punctuation,
        @param word: the input word.
        @type word: unicode.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        detailed_result = []
        if not word:
            return detailed_result
        # ToDo : fix it to isdigit, by moatz saad
        if word.isnumeric():
            detailed_result.append(
                wordcase.WordCase(
                    {
                        "word": word,
                        "affix": ("", "", "", ""),
                        "stem": "",
                        "original": word,
                        "vocalized": word,
                        "tags": "عدد",
                        "type": "NUMBER",
                        "freq": 0,
                        "syntax": "",
                        "root": "",
                    }
                )
            )
        # test if all chars in word are punctuation
        for char in word:
            if char not in stem_punct_const.PUNCTUATION:
                break
        else:
            # if all chars are punct, the word take tags of the first char
            detailed_result.append(
                wordcase.WordCase(
                    {
                        "word": word,
                        "affix": ("", "", "", ""),
                        "stem": "",
                        "original": word,
                        "vocalized": word,
                        "tags": stem_punct_const.PUNCTUATION[word[0]]["tags"],
                        "type": "punct",
                        "freq": 0,
                        "syntax": "",
                        "root": "",
                    }
                )
            )

        return detailed_result

    def check_word_as_verb(self, verb):
        """
        Analyze the word as verb.
        @param verb: the input word.
        @type verb: unicode.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        return self.verbstemmer.stemming_verb(verb)

    def check_word_as_noun(self, noun):
        """
        Analyze the word as noun.
        @param noun: the input word.
        @type noun: unicode.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        return self.nounstemmer.stemming_noun(noun)

    def check_word_as_unknown(self, noun):
        """
        Analyze the word as unknown.
        @param noun: the input word.
        @type noun: unicode.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        return self.unknownstemmer.stemming_noun(noun)

    @staticmethod
    def check_shadda(word_nm_shadda, resulted_data, fully_vocalized_input=False):
        """
        if the entred word is like the found word in dictionary,
        to treat some normalized cases,
        the analyzer return the vocalized like words.
        This function treat the Shadda case.
        @param word_nm_shadda: a word without harakat, but shadda
        @type word_nm_shadda: unicode
        @param resulted_data: the founded resulat from dictionary.
        @type resulted_data: list of dict.
        @param fully_vocalized_input: if the two words must resect the shadda and vocalized.
        @type fully_vocalized_input: Boolean, default is False.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        if fully_vocalized_input:
            # strip harakat keep shadda
            # input word can be vocalized
            # The output word vocalized
            return [
                x
                for x in resulted_data
                if araby.strip_harakat(word_nm_shadda)
                == araby.strip_harakat(x.vocalized)
            ]
        else:
            return [
                x
                for x in resulted_data
                if araby.shaddalike(word_nm_shadda, x.vocalized)
            ]

    # ~ @staticmethod
    def check_normalized(self, word_nm, resulted_data):
        """
        If the entred word is like the found word in dictionary,
        to treat some normalized cases,
        the analyzer return the vocalized like words
        ُIf the word is ذئب, the normalized form is ذءب,
        which can give from dictionary ذئبـ ذؤب.
        this function filter normalized resulted word according
        the given word, and give ذئب.
        @param word_nm the input word.
        @type word_nm: unicode.
        @param word_unvocalised: the input word unvocalized.
        @type word_unvocalised: unicode.
        @param resulted_data: the founded resulat from dictionary.
        @type resulted_data: list of dict.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        return [d for d in resulted_data if d.unvocalized == word_nm]
        # print word_vocalised.encode('utf8')
        # ~ filtred_data = []
        # ~ for item in resulted_data:
        # ~ outputword = item.unvocalized
        # ~ inputword = item.word_nm
        # ~ if inputword == outputword:
        # ~ filtred_data.append(item)
        # ~ return filtred_data

    @staticmethod
    def check_partial_vocalized(word_vocalised, resulted_data):
        """
        if the entred word is vocalized fully or partially,
        the analyzer return the vocalized like words
        This function treat the partial vocalized case.
        @param word_vocalised: the input word.
        @type word_vocalised: unicode.
        @param resulted_data: the founded resulat from dictionary.
        @type resulted_data: list of dict.
        @return: list of dictionaries of analyzed words with tags.
        @rtype: list.
        """
        filtred_data = []
        if not araby.is_vocalized(word_vocalised):
            return resulted_data
        else:
            # compare the vocalized output with the vocalized input
            # print ' is vocalized'
            for item in resulted_data:
                if "vocalized" in item:
                    output = item["vocalized"]
                    is_verb = "Verb" in item["type"]
                    if araby.vocalizedlike(word_vocalised, output):
                        item["tags"] += ":" + PARTIAL_VOCALIZED_TAG
                        filtred_data.append(item)
                        # حالة التقا الساكنين، مع نص مشكول مسبقا، والفعل في آخره كسرة بدل السكون
                    elif (
                        is_verb
                        and word_vocalised.endswith(araby.KASRA)
                        and output.endswith(araby.SUKUN)
                    ):
                        if araby.vocalizedlike(word_vocalised[:-1], output[:-1]):
                            item["tags"] += ":" + PARTIAL_VOCALIZED_TAG
                            filtred_data.append(item)

        return filtred_data
