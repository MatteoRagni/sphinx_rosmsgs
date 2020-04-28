import re


class TripleDashField:
    r"""
    Parse an input string in order to understand if it is a block
    separator (in ROS messages it is the ``---`` triple dash string 
    at the beginning of a new line)
    """

    # https://regex101.com/r/AQ7L8R/1
    PARSER = re.compile(r'^-{3}\s*$')

    @classmethod
    def parse(klass, text_line):
        r"""
        Parse a string and return an instance of triple dash field if compatible, 
        None if not compatible.

        :param text_line: a single line of text
        :return: nothing or a triple dash field
        :rtype: NoneType, TripleDashField
        """ 
        match = klass.PARSER.match(text_line)
        if match:
            return klass()


class FirstTripleDashField(TripleDashField):
    pass

class SecondTripleDashField(TripleDashField):
    pass
