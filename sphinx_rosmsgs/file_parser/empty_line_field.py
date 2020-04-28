class EmptyLineField():
    r"""
    Field for a empty line (not comment)
    """

    @classmethod
    def parse(klass, text_line=""):
        r"""
        Parse an empty line (always returns an empty line)

        :param text_line: discarded input, here only for consistency
        """
        return klass()
