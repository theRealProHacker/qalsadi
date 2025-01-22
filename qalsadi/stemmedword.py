import pyarabic.araby as araby
from . import stemmedaffix

GLOBAL_AFFIXES = {}


class StemmedWord:
    def __init__(self, resultdict=None):
        # given word attributes
        self.word = ("",)
        # ~"""input word"""
        self.vocalized = ("",)
        # ~"""vocalized form of the input word """
        self.unvocalized = ""

        # ~"""semivocalized form of the input word without inflection mark"""
        self.semivocalized = ""

        self.tags = ("",)
        # ~"""tags of affixes and tags extracted form lexical dictionary"""
        self.affix_key = "-"
        affix_tags = ""
        # ~"""tags of affixes"""

        # stemmed word attributes
        self.stem = ("",)
        # ~"""the word stem"""

        # _original word attributes from dictionary.
        self.original_tags = ("",)
        # ~""" tags extracted form lexical dictionary"""
        self.freq = (0,)  # the word frequency from _word _frequency database
        self.type = ("",)  # the word type
        self.original = ""  # original word from lexical dictionary
        self.tag_regular = (
            True  # the stemmed word is regular or irregular سالم أو تكسير
        )
        # تستعمل في الجمع
        if resultdict:
            self.word = resultdict.get("word", "")
            self.vocalized = resultdict.get("vocalized", "")
            self.semivocalized = resultdict.get("semivocalized", "")
            self.stem = resultdict.get("stem", "")
            self.root = resultdict.get("root", "")
            self.affix = "-".join(resultdict.get("affix", []))

            affix_tags = resultdict.get("tags", "")
            self.tags = ":".join(
                [resultdict.get("tags", ""), resultdict.get("originaltags", "")]
            )
            self.freq = resultdict.get("freq", "")
            self.type = resultdict.get("type", "")
            self.original = resultdict.get("original", "")
            # tags of stop word
            # action: the word role
            self.action = resultdict.get("action", "")
            # object_type: the next word type if is submitted to the action
            # the type of next word needed by the actual stop word
            self.object_type = resultdict.get("object_type", "")
            self.need = resultdict.get("need", "")
            self.tag_type = self.__get_type(resultdict.get("type", ""))

        self.affix_key = self.affix

        # init
        self.tag_added = False
        self.tag_initial = False
        self.tag_transparent = False
        self.tag_mamnou3 = False
        self.tag_break = False
        self.tag_voice = False
        self.tag_mood = False
        self.tag_confirmed = False
        self.tag_pronoun = False
        self.tag_transitive = False
        self.tag_person = self.__get_person(resultdict.get("person", None))
        # ~ x = resultdict.get('gender', None)
        # ~ if x : print x.encode('utf8'), self.word.encode('utf8')
        self.tag_original_number = resultdict.get("number", None)
        self.tag_original_gender = resultdict.get("gender", None)
        self.tag_number = self.__get_number()
        self.tag_gender = self.__get_gender()
        if self.is_noun():
            self.tag_added = self._is_added()
            self.tag_mamnou3 = self._is_mamnou3()
            # grouped attributes
            self.affix_key = "|".join([self.affix_key, self.word])
        if self.is_verb():
            self.tag_tense = resultdict.get("tense", "")
            self.tag_voice = resultdict.get("voice", "")
            self.tag_mood = resultdict.get("mood", "")
            self.tag_confirmed = resultdict.get("confirmed", "")
            self.tag_pronoun = resultdict.get("pronoun", "")
            self.tag_transitive = resultdict.get("transitive", False)
            # print ("stemmedword", self.tag_transitive)

            # #if the word is verb: we must add the tense and pronoun
            # to the affixkay.
            # #because for verbs, same affixes don't give same tags
            self.affix_key = "|".join([self.affix_key, affix_tags])
        if self.is_stopword():
            # #if the word is a stop word: we must add the word
            # to the affixkay.
            # #because for stopwords, same affixes don't give same tags
            self.affix_key = "|".join([self.affix_key, self.word])
        if self.affix_key not in GLOBAL_AFFIXES:
            GLOBAL_AFFIXES[self.affix_key] = stemmedaffix.StemmedAffix(resultdict)
            # ~ self.tag_transitive     ='y' in self.tags
        if self.is_stopword():
            self.tag_transparent = self._is_transparent()
        self.tag_initial = self._is_initial()

        # redandente
        self.tag_break = self._is_break()

    #  tags extracted from word dictionary
    # --------------------------
    def _is_initial(self):
        """Return True if the word mark the begin of next sentence."""
        word = self.word
        return word == "" or word[0] in (".", "?", "", ":")

    def __get_number(self):
        """
        Return the int code of the number state.
        the number cases are coded in binary like
        not defined        : 0  00000
        single  : 1  00001
        dual    : 2  00010
        plural  : 4  00100
        masculin plural: 8  01000
        feminin plural : 16 10000
        irregular plural : 32 100000
        this codification allow to have two marks for the same case,
        like irregular plural and single can have the same mark
        هذا الترميز يسمح بترميز المفرد وجمع التكسير معا
        @return: get the number state .
        @rtype: int
        """
        # غير محدد

        self.tag_number = 0
        # إذا لم يكن في الزوائد ما يدل على الجمع
        if not self._affix_is_plural() and not self._affix_is_dual():
            if "مفرد" in self.tags or ("مفرد" in self.tag_original_number):
                self.tag_number += 1
        if not self._affix_is_plural():
            if "مثنى" in self.tags:
                self.tag_number += 2
        if (
            self._affix_is_plural()
            or "جمع" in self.tags
            or ("جمع" in self.tag_original_number)
        ):
            self.tag_number += 4
            if "جمع مذكر سالم" in self.tags:
                self.tag_number += 8
            if "جمع مؤنث سالم" in self.tags:
                self.tag_number += 16
            if "جمع تكسير" in self.tag_original_number:
                self.tag_number += 32
        # if all previous case not used
        if self.tag_number == 0:
            self.tag_number += 1
        return self.tag_number

    def __get_person(self, given_person_tag=""):
        """
        Return the int code of the person state.
        the person cases are coded in binary like
        not defined        : 0  00000
        first  : 1  00001
        second    : 2  00010
        third  : 4  00100
        @return: get the person state .
        @rtype: int
        """
        self.tag_person = 0
        # ~ print self.tags.encode('utf8')
        if "متكلم" in self.tags or (given_person_tag and "متكلم" in given_person_tag):
            self.tag_person += 1
        if "مخاطب" in self.tags or (given_person_tag and "مخاطب" in given_person_tag):
            self.tag_person += 2
        if "غائب" in self.tags or (given_person_tag and "غائب" in given_person_tag):
            self.tag_person += 4
        if not self.tag_person:
            self.tag_person = 4
        # ~ print self.tag_person
        # tempdislay
        # ~ print self.word.encode('utf8'), self.tags.encode('utf8'), self.tag_person
        # ~ if given_person_tag: print "--",given_person_tag.encode('utf8')
        return self.tag_person

    def __get_type(self, input_type):
        """
        Return the numeric code of word type.
        the number cases are coded in binary like
        not defined        : 0  00000
        stopword  : 1  00001
        verb    : 2  00010
        noun  : 4  00100
        this codification allow to have two types for the same case,
        like a stop word can be a noun, the correspendant code is 101
        هذا الترميز يسمح بترميز الحروف والأسماء،
        بعض الأدوات هي أسماء
        @return: numeric code of type .
        @rtype: int
        """
        # غير محدد
        self.tag_type = 0
        if not input_type:
            return 0
        if "STOPWORD" in input_type:
            self.tag_type += 1
        if "Verb" in input_type:
            self.tag_type += 2
        if "Noun" in input_type or "اسم" in input_type or "مصدر" in input_type:
            self.tag_type += 4
        if "مصدر" in input_type:
            self.tag_type += 8
        # adjective
        # ~ print "tags", self.word.encode('utf8'), self.tags.encode('utf8')
        if (
            "صفة" in input_type
            or "اسم مفعول" in input_type
            or "اسم فاعل" in input_type
            or "صيغة مبالغة" in input_type
            or "فاعل" in input_type
            or "اسم تفضيل" in input_type
            or "منسوب" in self.tags
            # ~ or 'منسوب' in self.get_affix_tags()
            or "منسوب" in input_type
            or "adj" in input_type
        ):
            self.tag_type += 16
            # ~ print "is adj", self.word.encode('utf8')
        if "noun_prop" in input_type:
            self.tag_type += 32
        if "POUNCT" in input_type:
            self.tag_type += 64
        if "NUMBER" in input_type:
            self.tag_type += 128
        # ~ print self.tag_type
        return self.tag_type

    def __get_gender(self, input_gender=""):
        """
        Return the int code of the gender state.
        the number cases are coded in binary like
        not defined        : 0  00000
        masculin  : 1  00001
        feminin    : 2  00010
        this codification allow to have case in the same word
        @return: get the numeric sex state .
        @rtype: int
        """
        # غير محدد
        self.tag_gender = 0
        # إذا كان الاسم مذكرا وغير  متصل بما يؤنثه
        if not self._affix_is_feminin():
            if "مذكر" in self.tag_original_gender:
                self.tag_gender = 1
            elif (
                "اسم فاعل" in self.type
                or "اسم مفعول" in self.type
                or "صفة مشبهة" in self.type
            ):
                self.tag_gender = 1
            # يكون المصدر مذكرا إذا لم يحتوي على تاء مربوطة و لم يكن جمع تكسير
            elif (
                "مصدر" in self.type
                and araby.TEH_MARBUTA not in self.original
                and "جمع" not in self.tag_original_number
            ):
                self.tag_gender = 1

        # يتحدد المؤنث
        # بزيادة التاء المربوطة
        # جمع مؤنث سالم
        # ما كات اصله تاء مربوطة
        # للعمل TODO
        # دالة حاصة للكلمات المؤنثة
        ##print "stemmedword", self.original, (araby.TEH_MARBUTA in self.original)
        if araby.TEH_MARBUTA in self.original:
            self.tag_gender += 2
        elif "مؤنث" in self.tag_original_gender or "مؤنث" in self.tags:
            self.tag_gender += 2
        elif "جمع مؤنث سالم" in self.tags:
            self.tag_gender += 2
        elif self._affix_is_feminin():  # إذا كان متصلا بمايؤنثه
            self.tag_gender += 2
        # الحالات غير المثبتة والتي نحاول استخلاصها بقاعدة
        elif "مصدر" in self.type and (
            araby.TEH_MARBUTA in self.original or "جمع" in self.tag_original_number
        ):
            self.tag_gender += 2

        # جمع التكسير للمصادر والجوامد مؤنث
        elif "جمع" in self.tag_original_number and (
            "جامد" in self.type or "مصدر" in self.type
        ):
            self.tag_gender += 2

        # ~ print "gender", self.word.encode('utf8'), self.tag_gender
        return self.tag_gender

    def _is_transparent(self):
        """
        Return True if the word has the state transparent,
        which can trasnpose the effect of the previous factor.
        @return: has the state transparent.
        @rtype: True/False
        """
        # temporary,
        # the transparent word are stopwords like هذا وذلك
        # the stopword tags have اسم إشارة,
        # a punctuation can has the transparent tag like quotes.,
        # which havent any gramatical effect.
        # Todo
        # حالة بذلك الرجل
        # return  ('شفاف' in self.tags or 'إشارة'in self.tags  ) and self.has_jar()
        return "شفاف" in self.tags

    def _is_mamnou3(self):
        """
        Return True if the word is forbiden from Sarf ممنوع من الصرف.
        @return: is mamnou3 min sarf.
        @rtype: True/False
        """
        return "ممنوع من الصرف" in self.tags or "noun_prop" in self.type

    def get_procletic(
        self,
    ):
        """Get the procletic"""
        # return self.procletic
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].get_procletic()
        return ""

    def has_jonction(
        self,
    ):
        """return if the word has jonction"""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_3tf()
        return ""

    def has_procletic(
        self,
    ):
        """return True if has procletic"""
        # return self.procletic! = ''
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].has_procletic()
        return False

    def is_transitive(
        self,
    ):
        """return True if the verb is transitive"""
        return self.tag_transitive

    def is_indirect_transitive(
        self,
    ):
        """return True if the verb is indirect transitive  متعدي بحرف"""
        return self.tag_transitive

    def get_prefix(
        self,
    ):
        """Get the prefix"""
        # return self.prefix
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].get_prefix()
        return ""

    def get_suffix(
        self,
    ):
        """Get the suffix"""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].get_suffix()
        return ""

    def get_encletic(
        self,
    ):
        """Get the encletic"""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].get_encletic()
        return ""

    def has_encletic(
        self,
    ):
        """return True if has encletic"""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].has_encletic()
        return False

    # Mixed affix and dictionary attrrubutes
    # ---------------------------------------
    def _affix_is_added(self):
        """Return True if the word has the state added مضاف."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_added()
        return False

    def _is_added(self):
        """Return True if the word has the state added مضاف."""
        # ~ return self._affix_is_added() or 'اسم إضافة' in self.tags
        return self._affix_is_added()

    def _affix_is_feminin(self):
        """Return True if the word is Feminin."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_feminin()
        return False

    def _affix_is_plural(self):
        """Return True if the word is a plural."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_plural()
        return False

    def _affix_is_dual(self):
        """Return True if the word is a dual."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_dual()
        return False

    def _is_break(self):
        """Return True if the word has break."""
        # تكون الكلمة فاصلة إذا كانت منفصلة عمّا قبلها.
        # الحالات التي تقطع
        # - حرف جر متصل
        # فاصلة أو نقطة
        result = False
        if self.is_punct() and "break" in self.tags:
            result = True
        elif self.is_stopword() and not self.is_noun() and not self.is_transparent():
            result = True
        elif (
            self.affix_key in GLOBAL_AFFIXES
            and GLOBAL_AFFIXES[self.affix_key].is_break()
        ):
            result = True
        elif self.has_procletic():
            if self.has_jar() or self.has_istfham():
                result = True
        return result

    def get_tags_to_display(
        self,
    ):
        """
        Get the tags form of the input word
        """
        return self.tags + "T%dG%dN%d" % (
            self.tag_type,
            self.tag_gender,
            self.tag_number,
        )

    #  حالة المضاف إليه
    # --------------------------
    def is_unknown(self):
        """Return True if the word is unknown."""
        return "unknown" in self.type

    def is_stopword(self):
        """Return True if the word is a stop word."""
        return bool(self.tag_type % 2)

    def is_indirect_transitive_stopword(self):
        """Return True if the word is a stop word."""
        return self.is_stopword() and self.original in ("فِي", "عَنْ", "إِلَى", "عَلَى")

    def is_verb(self):
        """Return True if the word is a verb."""
        return bool(self.tag_type // 2 % 2)

    def is_noun(self):
        """Return True if the word is a noun."""
        return bool(self.tag_type // 4 % 2)

    def is_masdar(self):
        """Return True if the word is a masdar."""
        return bool(self.tag_type // 8 % 2)

    def is_adj(self):
        """Return True if the word is an adjective."""
        return bool(self.tag_type // 16 % 2)

    def is_proper_noun(self):
        """Return True if the word is a proper noun."""
        return bool(self.tag_type // 32 % 2)

    def is_punct(self):
        """Return True if the word is a punctuation."""
        return bool(self.tag_type // 64 % 2)

    def is_number(self):
        """Return True if the word is a number."""
        return bool(self.tag_type // 128 % 2)

    def is_transparent(self):
        """Return True if the word has the state transparent,
        which can trasnpose the effect of the previous factor.
        """
        # temporary,
        # the transparent word are stopwords like هذا وذلك
        # the stopword tags have اسم إشارة,
        # a punctuation can has the transparent tag like quotes.,
        # which havent any gramatical effect.
        # Todo
        # حالة بذلك الرجل
        return self.tag_transparent

        # ----------------------------
        # affixes boolean attributes
        # ----------------------------

    def is_majrour(self):
        """Return True if the word has the state majrour."""
        # Like بهذه بتلك
        # ~ print "maj",self.word.encode('utf8'), self.has_jar()

        if self.is_mabni() or self.has_jar():
            return True
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_majrour()

        return False

    def is_mansoub(self):
        """Return True if the word has the state mansoub."""
        # ~ print "mansoub",self.word.encode('utf8'), self.has_jar()
        if self.is_mabni():
            if self.has_jar():
                return False
            else:
                return True
        if "منصوب" in self.tags and self.is_feminin_plural():
            return True
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_mansoub()
        return False

    def is_marfou3(self):
        """Return True if the word has the state marfou3."""
        # ~ print "marf3",self.word.encode('utf8'), self.has_jar()

        if self.is_mabni():
            if self.has_jar():
                return False
            else:
                return True
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_marfou3()
        return False

    def is_majzoum(self):
        """Return True if the word has the state majrour."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_majzoum()
        return False

    def is_mabni(self):
        """Return True if the word has the state mabni."""
        if "مبني" in self.tags:
            return True
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_mabni()
        return False

    def is_defined(self):
        """Return True if the word has the state definde."""
        # ~ المعرفة: ما يقصد منه معيّن: والمعرفة سبعة أقسام هي:
        # ~ الضمير، العلم، اسم الإشارة، الاسم الموصول، المحلَّى بأل، المضاف إلى معرفة، المنادى.
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_defined()
        elif "ضمير" in self.tags:
            return True
        elif "اسم إشارة" in self.tags:
            return True
        elif "اسم موصول" in self.tags:
            return True
        elif "noun_prop" in self.tags:
            return True
        return False

    def is_past(self):
        """Return True if the word has the tense past."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_past()
        return False

    def is_passive(self):
        """Return True if the word has the tense passive."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_passive()
        return False

    def is_present(self):
        """Return True if the word has the tense present."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_present()
        return False

    def is_speaker_person(self):
        """Return True if the word has the 1st person."""
        return bool(self.tag_person % 2)

    def is_present_person(self):
        """Return True if the word has the 2nd person."""
        return bool(self.tag_person // 2 % 2)

    def is_absent_person(self):
        """Return True if the word has the 3rd person."""

        return bool(self.tag_person // 4 % 2)

    def is1stperson(self):
        """Return True if the word has the 1st person."""
        return bool(self.tag_person % 2) and self.is_single()

    def is2ndperson(self):
        """Return True if the word has the 2nd person."""
        return bool(self.tag_person // 2 % 2) and self.is_single()

    def is3rdperson(self):
        """Return True if the word has the 3rd person."""
        # ~ print "tag_person", self.tag_person, self.word.encode('utf8')
        return bool(self.tag_person // 4 % 2) and self.is_single()

    def is3rdperson_feminin(self):
        """Return True if the word has the 3rd person."""
        return bool(self.tag_person // 4 % 2) and self.is_single() and self.is_feminin()

    def is3rdperson_masculin(self):
        """Return True if the word has the 3rd person."""
        return (
            bool(self.tag_person // 4 % 2) and self.is_single() and self.is_masculin()
        )
        # ~
        # ~ if self.affix_key in GLOBAL_AFFIXES:
        # ~ return GLOBAL_AFFIXES[self.affix_key].is3rdperson_masculin()
        # ~ return False

    def has_imperative_pronoun(self):
        """Return True if the word has the 3rd person."""
        return bool(self.tag_person // 2 % 2)
        # ~ return (':أنت:' in self.tags or ':أنتِ:' in self.tags) \
        # ~ and 'أنتما' in self.tags and  ':أنتما مؤ:' in self.tags \
        # ~ and ':أنتم:' in self.tags and  ':أنتن:' in self.tags

    def is_tanwin(self):
        """Return True if the word has tanwin."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_tanwin()
        return False

    def has_jar(self):
        """Return True if the word has tanwin."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].has_jar()
        return False

    def has_istfham(self):
        """Return True if the word has tanwin."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].has_istfham()
        return False

    def is_break(self):
        """Return True if the word has break."""
        # تكون الكلمة فاصلة إذا كانت منفصلة عمّا قبلها.
        # الحالات التي تقطع
        # - حرف جر متصل
        # فاصلة أو نقطة
        return self.tag_break

    def is_masculin_plural(self):
        """Return True if the word is  Masculin plural."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_masculin_plural()
        return False

    def is_dual(self):
        """Return True if the word is  dual."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_dual()
        return False

    def is_feminin_plural(self):
        """Return True if the word is  Feminin plural."""
        if self.affix_key in GLOBAL_AFFIXES:
            return GLOBAL_AFFIXES[self.affix_key].is_feminin_plural()
        return False

    # -----------------------------
    # Mixed extraction attributes tests
    # -----------------------------

    def is_masculin(self):
        """Return True if the word is masculin."""
        return bool(self.tag_gender % 2)

    def is_feminin(self):
        """Return True if the word is Feminin."""
        return bool(self.tag_gender // 2 % 2)

    def is_plural(self):
        """Return True if the word is a plural."""
        return bool(self.tag_number // 4 % 2)

    def is_broken_plural(self):
        """Return True if the word is broken  plural."""
        return bool(self.tag_number // 32 % 2)

    def is_mamnou3(self):
        """Return True if the word is Mamnou3 min Sarf."""
        return self.tag_mamnou3

    def is_single(self):
        """Return True if the word is single."""
        return not self.is_plural() and not self.is_dual()

    def is_added(self):
        """Return True if the word has the state added مضاف."""
        return self.tag_added

    def __str__(self):
        """Display objects result from analysis"""
        text = "{"
        stmword = self.__dict__
        stmword["affix"] = "Taha"
        for key in stmword.keys():
            text += "\n\t\t'%s' = '%s', " % (key, stmword[key])
        text += "\n\t\t}"
        return text  # .encode('utf8')
