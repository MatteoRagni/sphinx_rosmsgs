from .comment_field import CommentField
from .empty_line_field import EmptyLineField
from .message_field import MessageField
from .triple_dash_field import TripleDashField, FirstTripleDashField, SecondTripleDashField
from .block_parser import BlockParser


class FileParser:
    r"""
    A parser for the ROS message type. The file parser can parse `message`, `service`
    and `action` files. The message (no matter what the actual type) will be split 
    in three blocks:

     * `request` block, which is not empty in all messages types
     * `response` block, which is not empty in `service` and `action` message types
     * `feedback` block, which is not empty only in `action` message type

    There are two type identification for a message: the type identification provided
    as input by the user (via the contruction of the object) and the one extracted by
    the actual file parsing. Those two should always be the same.

    In the normal usage of the library, this type information comes from the indexer,
    which has extracted it from the message extension. Thus it is possible to check if
    the type coming from the message extension matches the one coming from the content.

    :param message_name: the message name in ROS terms
    :param message_path: the path to the file to open for parsing
    :param message_type: the type of the message provided by the user
    """

    def __init__(self, message_name, message_path, message_type="message"):
        self._message_name = message_name
        self._message_type = message_type
        self._message_path = message_path

        self._content = []
        self._blocks = [BlockParser(), BlockParser(), BlockParser()]
        self._current_block = 0
        self._parse_lock = False

    def parse(self):
        r"""
        Actual parse routine. It will read the file and parse it, populating the content.
        Running parse will unlock the other properties of the current object. The actually
        parsing procedure runs only once, but returns self always.

        :return: the current file parser instance
        :rtype: FileParser
        :raise IOError: if the message file does not exists
        """
        if self._parse_lock:
            return
        self._parse_lock = True
        with open(self._message_path, "r") as message_file:
            self._content = message_file.read().splitlines()
        for line in self._content:
            curr_line = self._parse_line(line)
            if curr_line:
                self._blocks[self._current_block].append(curr_line)
        return self

    def _parse_line(self, line):
        r"""
        Parser for single line.

        :param line: the current entering line
        :return: a field of the current block
        """
        field = CommentField.parse(line)
        if field:
            return field
    
        field = MessageField.parse(line)
        if field:
            return field

        if self._current_block == 0:
            field = FirstTripleDashField.parse(line)
        if self._current_block == 1:
            field = SecondTripleDashField.parse(line)
        if field:
            self._current_block += 1
            return
        return EmptyLineField.parse(line)

    @property
    def name(self):
        r"""
        The name of the ROS message in ROS terms

        :return: The name of the ROS message in ROS terms
        :rtype: str
        """
        return self._message_name

    @property
    def request(self):
        r"""
        Return the first of the blocks of the parsed message. Can be called only
        after the parse method has been caled, it raises an error otherwise.

        :return: the first block of the message
        :rtype: BlockParser
        :raise RuntimeError: when parse has not run on the object
        """
        if not self._parse_lock:
            raise RuntimeError("You must run parse on the file parser before accessing it")
        return self._blocks[0]

    @property
    def message(self):
        r"""
        Alias of attr:`request`
        
        Return the first of the blocks of the parsed message. Can be called only
        after the parse method has been caled, it raises an error otherwise.

        :return: the first block of the message
        :rtype: BlockParser
        :raise RuntimeError: when parse has not run on the object
        """
        return self.request

    @property
    def response(self):
        r"""
        Return the second block of the parsed message. Can be called only
        after the parse method has been caled, it raises an error otherwise.

        :return: the second block of the message
        :rtype: BlockParser
        :raise RuntimeError: when parse has not run on the object
        """
        if not self._parse_lock:
            raise RuntimeError("You must run parse on the file parser before accessing it")
        return self._blocks[1]

    @property
    def feedback(self):
        r"""
        Return the third block of the parsed message. Can be called only
        after the parse method has been caled, it raises an error otherwise.

        :return: the third block of the message
        :rtype: BlockParser
        :raise RuntimeError: when parse has not run on the object
        """
        if not self._parse_lock:
            raise RuntimeError("You must run parse on the file parser before accessing it")
        return self._blocks[2]   

    @property
    def parsed_type(self):
        r"""
        Return the `parsed` type, meaning that the type is extracted from the content of
        the file. It can be one of the following strings: `message`, `service`, `action`

        :return: one of `message`, `service` or `action`
        :rtype: str
        :raise RuntimeError: when parse has not run on the object
        """
        if not self._parse_lock:
            raise RuntimeError("You must run parse on the file parser before accessing it")
        ret = ["message", "service", "action"]
        return ret[self._current_block]

            