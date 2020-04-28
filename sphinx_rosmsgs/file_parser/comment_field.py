import re
import os


class CommentField:
    r"""
    The comment field parses a single line of comment or receives another comment
    field in order to create a more complex paragraph of text.

    A commentstart with the character ``#`` at the beginning of the line and 
    continues till the end of the line

    :param match: the result of the match from the parser regular expression
    :param isempty: flag to create an empty line of comment
    """

    # https://regex101.com/r/pAbomI/6
    PARSER = re.compile(r'^#\s{0,1}(?P<line>.*)$')

    @classmethod
    def parse(klass, text_line):
        r"""
        Parse a string and return an instance of comment field if compatible, 
        None if not compatible.

        :param text_line: a single line of text
        :return: nothing or a comment field
        :rtype: NoneType, CommentField 
        """ 
        match = klass.PARSER.match(text_line)
        if match:
            return klass(match)

    @classmethod
    def empty(klass):
        r"""
        Returns an empty comment field (text is ``""``)

        :return: a comment field
        :rtype: CommentField
        """
        return klass(None, isempty=True)

    def __init__(self, match=None, isempty=False):
        self._match = match
        if isempty:
            self._text = [] 
        else:
            self._text = [match.group("line").rstrip()]

    def join(self, other):
        r"""
        Join two comment field. The current field will get the lines
        from the other comment field.

        :return: the current comment field
        :rtype: CommentField
        """
        self._text += other._text
        return self

    @property
    def text(self):
        r"""
        Returns the centent text as a single string

        :return: the comment contents as a single string
        :rtype: str
        """
        return os.linesep.join(self._text)

    @property
    def lines(self):
        r"""
        Returns the centent text as a list of line string

        :return: the comment contents as a list of line string
        :rtype: list
        """
        return self._text

    def __str__(self):
        return self.text
