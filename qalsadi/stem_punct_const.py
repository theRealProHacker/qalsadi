#!/usr/bin/python
# -*- coding=utf-8 -*-
"""
Constants for punctuation stemming
"""
PUNCTUATION = {}

PUNCTUATION["."] = {
    "word": ".",
    "tags": "نقطة:break",
}
PUNCTUATION["~"] = {
    "word": "~",
    "tags": "شفاف",
}

PUNCTUATION[","] = {
    "word": ",",
    "tags": "فاصلة:break",
}
PUNCTUATION["،"] = {
    "word": "،",
    "tags": "فاصلة:break",
}
# PUNCTUATION[u',']={'word':u',', 'tags':u'فاصلة:شفاف',}
# PUNCTUATION[u'،']={'word':u'،', 'tags':u'فاصلة:شفاف',}

PUNCTUATION["?"] = {
    "word": "?",
    "tags": "استفهام:break",
}
PUNCTUATION["؟"] = {
    "word": "؟",
    "tags": "استفهام:break",
}
PUNCTUATION["!"] = {
    "word": "!",
    "tags": "تعجب:break",
}

PUNCTUATION[";"] = {
    "word": ";",
    "tags": "نقطة فاصلة:break",
}
PUNCTUATION["-"] = {
    "word": "-",
    "tags": "مطة:break",
}

PUNCTUATION[":"] = {
    "word": ":",
    "tags": "نقطتان:break",
}

PUNCTUATION["'"] = {
    "word": "'",
    "tags": "تنصيص مفرد:شفاف",
}
PUNCTUATION[" "] = {
    "word": " ",
    "tags": "فراغ:شفاف",
}

PUNCTUATION['"'] = {
    "word": '"',
    "tags": "تنصيص مزدوج:شفاف",
}

PUNCTUATION[")"] = {
    "word": ")",
    "tags": "قوس",
}
PUNCTUATION["("] = {
    "word": "(",
    "tags": "قوس",
}

PUNCTUATION["["] = {
    "word": "[",
    "tags": "عارضة",
}
PUNCTUATION["]"] = {
    "word": "]",
    "tags": "عارضة",
}

PUNCTUATION["{"] = {
    "word": "{",
    "tags": "حاضنة",
}
PUNCTUATION["}"] = {
    "word": "}",
    "tags": "حاضنة:break",
}
# treat newline as punct for now
PUNCTUATION["\n"] = {
    "word": "\n",
    "tags": "سطر جديد:newline:break",
}
