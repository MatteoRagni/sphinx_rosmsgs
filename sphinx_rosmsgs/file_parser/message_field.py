
import re
import os

import sphinx
from docutils import nodes
from .comment_field import CommentField


class MessageField:
    r"""
    The field represents a definition line for a ROS message. The definition in it's complete case follows
    (the one presented is not actually valid, but shows all the parts we are interested in)::

        std_msgs/string[2] message_field = ["1", "2"]
        ┬───────────────── ┬──────────── ┬ ┬─────────
        └ type_text (str)  └ name (str)  │ └ default (str)
                                         └ has_default (bool)

        std_msgs/string [ 2 ]
        ┬────────────── ┬ ┬
        └ type (str)    │ └ list_size (str) / if no number is present: is_variable (bool)
                        └ is_list (bool)

    The idea is to split all those part of the definition in order to create the single attributes. The parsing
    of this kind of string is made by a regular expression.

    :param match: the match coming from the regular expression
    """

    # https://regex101.com/r/a2vqhn/1
    #                          ---type---------------  ---is_list--------------------------          ---name---------------     ---is_equal------------------        
    #                                                                ---list_size----------                                                      ---value---
    PARSER = re.compile(r'^\s*(?P<type>[a-zA-Z0-9/_]+)(?P<is_list>\[(?P<list_size>[0-9]*)\]){0,1}\s*(?P<name>[a-zA-Z0-9/_]+)\s*(?P<is_equal>=\s*(?P<value>.*)){0,1}$')

    @classmethod
    def parse(klass, text_line):
        r"""
        Parse a string and return an instance of message field if compatible, 
        None if not compatible.

        :param text_line: a single line of text
        :return: nothing or a message field
        :rtype: NoneType, MessageField 
        """ 
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
        r"""
        If the complex type is a list of the base type

        :return: if the complex type is a list of the base type
        :rtype: bool
        """
        return self._is_list

    @property
    def has_default(self):
        r"""
        If there is a default value

        :return: if there is a default value
        :rtype: bool
        """
        return self._has_default

    @property
    def type(self):
        r"""
        The base type (not including list)

        :return: the base type (not including list)
        :rtype: str
        """
        return self._type

    @property
    def is_variable(self):
        r"""
        If it is a list, it is true if the length is not specified

        :return: if it is a list, it is true if the length is not specified
        :rtype: bool
        """
        return self._is_variable

    @property
    def name(self):
        r"""
        The name of the field

        :return: the name of the field
        :rtype: str
        """
        return self._name

    @property
    def size(self):
        r"""
        If it is a list, the size of the list if it is not variable:
        :warning: default value (not list or variable list) is zero!

        :return: the size of the list
        :rtype: NoneType, str
        """
        return self._size

    @property
    def default(self):
        r"""
        The default value of the field
        :warning: the attribute is an empty string if the field has default is false

        :return: the default value
        :rtype: str
        """
        return self._default

    @property
    def text(self):
        r"""
        The comment field associated with the message, that contains its escription
        """
        return self._text
    
    def set_text(self, new_text):
        r"""
        Set a new comment field
        """
        if isinstance(new_text, CommentField):
            self._text = new_text

    @property
    def type_text(self):
        r"""
        Compound type text (including list and list size)

        :return: the compoind type
        :rtype: str
        """
        type_text = f"{self.type}"
        if self.is_list:
            type_text += " ["
            if not self.is_variable:
                type_text += str(self.size)
            type_text += "] "
        return type_text
    
    @property
    def default_text(self):
        r"""
        Default text (the stuff after the equal). The resulting string will contain the equal.
        To get only the value use attr:`default`

        :return: the default value, with ``=`` in front
        :rtype: str
        """
        default_text = ""
        if self.has_default:
            default_text += f" = {self.default}"
        return default_text

    def __str__(self):
        return f"{self.type_text} {self.name} {self.default_text} (\n{self.text}\n)\n"