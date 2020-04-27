from .comment_field import CommentField
from .empty_line_field import EmptyLineField
from .message_field import MessageField
from .triple_dash_field import TripleDashField, FirstTripleDashField, SecondTripleDashField
from .message_parser import MessageParser


class FileParser:
    def __init__(self, message_name, indexer):
        self._message_name = message_name
        self._message_type = indexer.get_type(message_name)
        self._message_path = indexer.get_path(message_name)

        self._content = []
        self._blocks = [MessageParser(), MessageParser(), MessageParser()]
        self._current_block = 0
        with open(self._message_path, "r") as message_file:
            self._content = message_file.read().splitlines()

    def parse(self):
        for line in self._content:
            curr_line = self.parse_line(line)
            if curr_line:
                self._blocks[self._current_block].append(curr_line)

    def parse_line(self, line):
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
        return self._message_name

    @property
    def request(self):
        return self._blocks[0]

    @property
    def response(self):
        return self._blocks[1]

    @property
    def feedback(self):
        return self._blocks[2]   

    @property
    def parsed_type(self):
        ret = ["message", "service", "action"]
        return ret[self._current_block]

    def __str__(self):
        ret = [str(x) for x in self._blocks]
        ret = ("\n*******\n").join(ret[0:self._current_block + 1])
        ret = f"{self._message_name} - {self._message_type} / {self.parsed_type}\n-*-*-\n{ret}"
        return ret

            