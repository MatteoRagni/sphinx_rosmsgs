import re


class TripleDashField:
    # https://regex101.com/r/AQ7L8R/1
    PARSER = re.compile(r'^-{3}\s*$')

    @classmethod
    def parse(klass, text_line):
        match = klass.PARSER.match(text_line)
        if match:
            return klass()

    def __init__(self):
        pass

    def __str__(self):
        return "--- 0 ---"


class FirstTripleDashField(TripleDashField):

    def __str__(self):
        return "--- 1 ---"


class SecondTripleDashField(TripleDashField):

    def __str__(self):
        return "--- 2 ---"
