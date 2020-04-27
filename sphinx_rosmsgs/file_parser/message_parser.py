from .comment_field import CommentField
from .empty_line_field import EmptyLineField
from .message_field import MessageField
from .triple_dash_field import TripleDashField, FirstTripleDashField, SecondTripleDashField


class MessageParser:
    def __init__(self):
        self._fields = []
        self._message_fields = {}
        self._prev_line = EmptyLineField()
        self._lock = False
    
    def append(self, curr_line):
        r"""
        State machine for the parser. Once the line has been parsed and identified it is handled
        accordingly to the previous line.

        | Next - Prev | Comment                       | Definition | Block  | Empty  |
        |-------------|-------------------------------|------------|--------|--------|
        | Comment     | Insert in previous            | Append     | Append | Append |
        | Definition  | Insert previous in definition | Append     | Append | Append |
        | Empty       | skip                          | skip       | skip   | skip   |
        | Block       | lock                          | lock       | lock   | lock   |
        """
        if self._lock:
            return
        if isinstance(self._prev_line, CommentField) and isinstance(curr_line, CommentField):
            self._prev_line.join(curr_line)
            return
        if isinstance(self._prev_line, CommentField) and isinstance(curr_line, MessageField):
            self._fields.remove(self._prev_line)
            curr_line.set_text(self._prev_line)
            self._fields.append(curr_line)
            self._message_fields[curr_line.name] = curr_line
            self._prev_line = curr_line
            return
        if isinstance(curr_line, EmptyLineField):
            self._prev_line = curr_line
            return
        if isinstance(curr_line, TripleDashField):
            self._prev_line = curr_line
            self._lock = True
            return
        self._prev_line = curr_line
        self._fields.append(curr_line)

    def unlock(self):
        self._lock = False

    def __len__(self):
        return len(self._fields)

    def __getitem__(self, key):
        if isinstance(key, int):
            return self._fields[key]
        if isinstance(key, str):
            return self._message_fields[key]

    def directive_output(self):
        return [(obj.__class__.__name__, obj) for obj in self._fields]

    def __str__(self):
        field_list = [str(f) for f in self._fields]
        return ("\n").join(field_list)

    @property
    def header(self):
        header = []
        for field in self._fields:
            if isinstance(field, MessageField):
                break
            header.append(field)
        return header
    
    @property
    def definitions(self):
        return list(self._message_fields.values())