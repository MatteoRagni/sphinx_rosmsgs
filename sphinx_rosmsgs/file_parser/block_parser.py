from sphinx_rosmsgs.file_parser.comment_field import CommentField
from sphinx_rosmsgs.file_parser.empty_line_field import EmptyLineField
from sphinx_rosmsgs.file_parser.message_field import MessageField
from sphinx_rosmsgs.file_parser.triple_dash_field import TripleDashField, FirstTripleDashField, SecondTripleDashField


class BlockParser:
    r"""
    Class container of one of the blocks of the message. The block is agnostic if it 
    is a `request`, a `response` or a `feddback`. The block has a header, which is all the comment
    fields before the first message field.

    One class:`FileParser` has three class:`BlockParser`  
    """

    def __init__(self):
        self._fields = []
        self._message_fields = {}
        self._prev_field = EmptyLineField()
        self._lock = False
    
    def append(self, curr_field):
        r"""
        State machine for the parser. Once the field has been parsed and identified it is handled
        accordingly to the previous field.
        
        ============= =============================== ============ ======== ========
         Next - Prev   Comment                         Definition   Block    Empty 
        ============= =============================== ============ ======== ========
         Comment       insert in previous              append       append   append  
         Definition    insert previous in definition   append       append   append  
         Empty         skip                            skip         skip     skip    
         Block         lock                            lock         lock     lock    
        ============= =============================== ============ ======== ========

        lock means that the block will not accept more fields to be appendend

        :param curr_field: the parameter is one of the existing field, and it is inserted in the
                           current block. A new field can modify the previous field.
        """
        if self._lock:
            return
        if isinstance(self._prev_field, CommentField) and isinstance(curr_field, CommentField):
            self._prev_field.join(curr_field)
            return
        if isinstance(self._prev_field, CommentField) and isinstance(curr_field, MessageField):
            self._fields.remove(self._prev_field)
            curr_field.set_text(self._prev_field)
            self._fields.append(curr_field)
            self._message_fields[curr_field.name] = curr_field
            self._prev_field = curr_field
            return
        if isinstance(curr_field, EmptyLineField):
            self._prev_field = curr_field
            return
        if isinstance(curr_field, TripleDashField):
            self._prev_field = curr_field
            self._lock = True
            return
        self._prev_field = curr_field
        self._fields.append(curr_field)

    def __len__(self):
        r"""
        Returns the number of fields in the current block

        :return: the number of fields in the current block
        :rtype: int
        """
        return len(self._fields)

    def __getitem__(self, key):
        r"""
        Return the blockin a certain position or the definition (in name was given)

        :param key: if it is an ``int`` it will return the field in that position,
                    if it is a ``str`` it will return the definition if exists
        :return: a field accordingly to the key
        :rtype: CommentField, MessageField
        :raise KeyError: if the key is a ``str`` and the definition does not exists
        :raise IndexError: if thekey is a ``int`` and exceedes the length of the block
        """
        if isinstance(key, int):
            return self._fields[key]
        if isinstance(key, str):
            return self._message_fields[key]

    @property
    def header(self):
        r"""
        Returns all the fields that are **before** the first definition in the 
        current block

        :return: all the fields before the first definition
        :rtype: list
        """
        header = []
        for field in self._fields:
            if isinstance(field, MessageField):
                break
            header.append(field)
        return header
    
    @property
    def definitions(self):
        r"""
        Return a list of all the definition of a block. This will not include
        headers or comment blocks between definition separated with an empty line

        :return: all the definitions in a message (with their definition comment)
        :rtype: list
        """
        return list(self._message_fields.values())