
import re
import os

import sphinx
from docutils import nodes
from .comment_field import CommentField


class MessageField:
    # https://regex101.com/r/a2vqhn/1
    #                          ---type---------------  ---is_list--------------------------          ---name---------------     ---is_equal------------------        
    #                                                                ---list_size----------                                                      ---value---
    PARSER = re.compile(r'^\s*(?P<type>[a-zA-Z0-9/_]+)(?P<is_list>\[(?P<list_size>[0-9]*)\]){0,1}\s*(?P<name>[a-zA-Z0-9/_]+)\s*(?P<is_equal>=\s*(?P<value>.*)){0,1}$')

    @classmethod
    def parse(klass, text_line):
        match = klass.PARSER.match(text_line)
        if match:
            return klass(match)

    def __init__(self, match):
        self._match = match
        self._type = match.group("type")
        self._name = match.group("name")
        self._is_list = not (match.group("is_list") is None)
        self._has_default = not (match.group("is_equal") is None)

        self._is_variable = False
        self._size = 0
        self._default = ""
        
        if self._is_list:
            self._is_variable = (match.group("list_size") is None)
            if not self._is_variable:
                # This should be an int(value) but throws an error
                # and I have noidea why
                self._size = match.group("list_size")
        
        if self._has_default:
            self._default = match.group("value")
        self._text = CommentField.empty()

    @property
    def is_list(self):
        return self._is_list

    @property
    def has_default(self):
        return self._has_default

    @property
    def type(self):
        return self._type

    @property
    def is_variable(self):
        return self._is_variable

    @property
    def name(self):
        return self._name

    @property
    def size(self):
        return self._size

    @property
    def default(self):
        return self._default

    @property
    def text(self):
        return self._text
    
    def set_text(self, new_text):
        if isinstance(new_text, CommentField):
            self._text = new_text

    @property
    def type_text(self):
        type_text = f"{self.type}"
        if self.is_list:
            type_text += "["
            if not self.is_variable:
                type_text += str(self.size)
            type_text += "]"
        return type_text
    
    @property
    def default_text(self):
        default_text = ""
        if self.has_default:
            default_text += f"= {self.default}"
        return default_text

    def __str__(self):
        return f"{self.type_text} {self.name} {self.default_text} (\n{self.text}\n)\n"