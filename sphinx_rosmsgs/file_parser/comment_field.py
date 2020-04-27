import re
import os


class CommentField:
    # https://regex101.com/r/pAbomI/2
    PARSER = re.compile(r'^#\s{0,1}(?P<line>.*)$')

    @classmethod
    def parse(klass, text_line):
        match = klass.PARSER.match(text_line)
        if match:
            return klass(match)        

    @classmethod
    def empty(klass):
        return klass(None, isempty=True)

    def __init__(self, match=None, isempty=False):
        self._match = match
        if isempty:
            self._text = [] 
        else:
            self._text = [match.group("line").rstrip()]

    def join(self, other):
        self._text += other._text
        return self

    @property
    def text(self):
        return os.linesep.join(self._text)

    def __str__(self):
        return self.text
