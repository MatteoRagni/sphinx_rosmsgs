from docutils import nodes
from sphinx import addnodes
from sphinx.util.docutils import SphinxDirective
from .message_indexer import MessageIndexer
from docutils.statemachine import ViewList
from sphinx.util.nodes import nested_parse_with_titles
import re


class MessageDirective(SphinxDirective):

    required_argument = 1
    optional_argument = 0
    has_content = True

    def run_section(self, comment, ids):
        comment_file = f"comment_{id(comment)}.rst"
        rst = ViewList()
        for line_no, line_txt in enumerate(comment.text.splitlines()):
            rst.append(line_txt, comment_file, line_no)
        section = nodes.section(ids=[ids], classes=[ids])
        section.document = self.state.document
        nested_parse_with_titles(self.state, rst, section)
        return section

    def run_definition(self, definition, base_ids):
        ids = f"{base_ids}.{definition.name}"
        desc_type = addnodes.desc_type(text=definition.type_text + " ")
        desc_name = addnodes.desc_name(text=definition.name + " ")
        desc_annotation = addnodes.desc_annotation(text=definition.default_text + " ")
        desc_signature = addnodes.desc_signature(ids=[ids])
        desc_signature += desc_type
        desc_signature += desc_name
        desc_signature += desc_annotation

        section = self.run_section(definition.text, f"{ids}.description")
        desc_content = addnodes.desc_content()
        desc_content += section.children
        desc = addnodes.desc(objtype="attribute")
        desc += desc_signature
        desc += desc_content
        return desc

    def run_block(self, message_block, base_ids, block_name, request_title=True):
        if len(message_block) == 0:
            return None
        ids = f"{base_ids}.{block_name}"
        section = nodes.section(ids=[ids], classes=[ids])
        if request_title:
            section += nodes.title(text=block_name)
        for block in message_block:
            if block.__class__.__name__ == "CommentField":
                section += self.run_section(block, f"{ids}.comment-{id(block)}")
            if block.__class__.__name__ == "MessageField":
                section += self.run_definition(block, ids)
        if request_title:
            return section
        else:
            return section.children

    def run(self):
        name = ("").join(self.content)
        parsed_message = self.indexer.parse(name)
        
        ids = re.sub("/", ".", name)
        
        section = nodes.section(ids=[f"{name}"], classes=[f"{name}"])       
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
        return MessageIndexer.retrieve_global()
