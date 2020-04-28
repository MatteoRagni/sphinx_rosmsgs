from docutils import nodes
from sphinx import addnodes
from sphinx.util.docutils import SphinxDirective
from sphinx_rosmsgs.message_indexer import MessageIndexer
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
import re


class MessageDirective(SphinxDirective):
    r"""
    The implementation of the ``.. ros_message::`` directive. The directive 
    require a unique argument that is the name of the message to document. 
    
    Only the messages in package added to the ``rosmsg_path_root`` global 
    configuration variable can be documented. Otherwise an error is raised.
    """

    required_argument = 1
    optional_argument = 0
    has_content = True

    def run_section(self, comment, base_ids):
        r"""
        Execute a nested parsing on a block comment that will contains probably
        some restructured text stuff. We are using nested parsing with titles
        and returning the whole section childrens.

        In general it can be seed as a function that converts `CommentField` in
        parsed document, using nested parsing methods.

        :param comment: the comment block to parse
        :param ids: the id to be used for the source file name generation 
                        (Sphinx requirements) and section ids (lost in return)
        :return: the children of a section to be added to the document corpus
        """
        ids = f"{base_ids}.{id(comment)}"
        comment_file = f"{ids}.rst"
        rst = ViewList()
        for line_no, line_txt in enumerate(comment.lines):
            rst.append(line_txt, comment_file, line_no)
        section = nodes.section(ids=[ids], classes=[ids], names=[ids])
        section.document = self.state.document
        nested_parse_with_titles(self.state, rst, section)
        return section.children

    def run_definition(self, definition, base_ids):
        r"""
        Writes down the definition of a field of a message and parses its
        description.

        In general it can be seen as a function that converts `MessageField` in
        parsed document, with a description section containing both signature and
        informative content text.

        The signature are set as `attribute` object type.
        
        :param definition: a definition that should be parsed
        :param base_ids: the base id for indexing, local scope will be added to that 
                         id, based on the name of the field.
        :return: a full `desc` node, to be added to the main document
        """
        ids = f"{base_ids}.{definition.name}"
        desc_type = addnodes.desc_type(text=definition.type_text)
        desc_name = addnodes.desc_name(text=definition.name)
        desc_annotation = addnodes.desc_annotation(text=definition.default_text)
        desc_signature = addnodes.desc_signature(ids=[ids], fullname=[definition.name])
        desc_signature += desc_type
        desc_signature += desc_name
        desc_signature += desc_annotation

        section = self.run_section(definition.text, ids)
        desc_content = addnodes.desc_content()
        desc_content += section
        desc = addnodes.desc(objtype="attribute")
        desc += desc_signature
        desc += desc_content
        return desc

    def run_block(self, message_block, base_ids, block_name, request_title=True):
        r"""
        A ROS message, indipendently from its actual representation is seen in this
        code as a structure with three sections:

         * a _request_ (included in all _messages_, _services_, and _actions_)
         * a _response_ (included in _services_ and _actions_)
         * a _feedback_ (included only in _actions_)

        Each section may have more than one definition or comment block to be parsed.
        This function transforms one of those sections in actual documentation.

        :param message_block: one of the section of the message
        :param base_ids: the base id of the message to be used for indexing. A local scope
                         will be added, bease upon the section title
        :param block_name: the name of the current block: usually one of _Request_, _Response_
                           or _Feedback_
        :param request_title: disable the creation of the title for the section (it is 
                              disabled for _Request_ of _Message_)
        :return: a section node if the title is active, the section children if the title is
                 disabled
        """
        if len(message_block) == 0:
            return None
        ids = f"{base_ids}.{block_name}"
        section = nodes.section(ids=[ids], classes=[ids], names=[ids])
        if request_title:
            section += nodes.title(text=block_name)
        for block in message_block:
            if block.__class__.__name__ == "CommentField":
                section += self.run_section(block, ids)
            if block.__class__.__name__ == "MessageField":
                section += self.run_definition(block, ids)
        if request_title:
            return section
        else:
            return section.children

    def run(self):
        r"""
        The directive run method

        :return: the section node with the documentation of a single complete message
        """
        name = ("").join(self.content)
        parsed_message = self.indexer.parse(name)
        
        ids = re.sub("/", ".", name)
        
        section = nodes.section(ids=[name], classes=[name], names=[name])       
        section.document = self.state.document
        section += nodes.title(text=parsed_message.name)

        request_title = True if parsed_message.parsed_type != "message" else False   
        request = self.run_block(parsed_message.request, ids, "Request", request_title)
        response = self.run_block(parsed_message.response, ids, "Response")
        feedback = self.run_block(parsed_message.feedback, ids, "Feedback")

        if request:
            section += request
        if response:
            section += response
        if feedback:
            section += feedback
        return [section]

    @property
    def indexer(self):
        r"""
        Recovers the global messag indexer, used to extract all the file path of a message
        given its name.

        :return: the global message indexer
        :rtype: MessageIndexer
        """
        return MessageIndexer.retrieve_global()
