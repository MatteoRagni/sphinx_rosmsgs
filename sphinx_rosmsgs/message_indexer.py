import re
from pathlib import Path
import xml.etree.cElementTree as ElementTree
from .file_parser import FileParser


class MessageIndexer:
    global_name = "__message__indexer__"
    message_ext = ".msg"
    service_ext = ".srv"
    action_ext = ".action"
    package_xml = "package.xml"
    message_type_list = ["message", "service", "action"]
    is_init = False

    @classmethod
    def register_global(klass, path_list):
        globals()[klass.global_name] = klass(path_list)

    @classmethod
    def retrieve_global(klass):
        return globals()[klass.global_name]

    @classmethod
    def init_class(klass):
        r"""
        Initialize the class with some used variable, like the name parsers
        """
        if not klass.is_init:
            klass.is_init = True
            klass.extension_list = [klass.message_ext, klass.service_ext, klass.action_ext]
            klass.parser_base_string = lambda extension: f"(([a-zA-Z_0-9-\\.]+)\\/)+(?P<name>[a-zA-Z_0-9]+)\\{extension}"
            klass.parser_list = [re.compile(klass.parser_base_string(ext)) for ext in klass.extension_list]
 
    def __init__(self, path_list):
        self.__class__.init_class()
        self.path_list = path_list
        self.index = {}
        self.type_index = {}
        self.index_all()

    def index_all(self):
        for path in self.path_list:
            self.index_path(path)

    def parse_package_xml(self, path):
        r"""
        Extract current package name from package.xml ROS file
        """
        package_xml = path / self.__class__.package_xml
        if not package_xml.exists():
            raise RuntimeError(f"The file `{package_xml}` does not exists. Is this a ROS package?")
        
        package_name = ""
        try:
            package_tree = ElementTree.parse(package_xml)
            package_root = package_tree.getroot()
            package_name = package_root.find("./name").text
        except Exception as e:
            err = f"Cannot parse `{package_xml}`: is a valid ROS package xml file? Error: {e}"
            raise RuntimeError(err)
        return package_name

    def index_path(self, path):
        r"""
        Search for all messages in one of the provided path. In this way we have a mapping
        between a file and its path. The user will put in the directive the name of the message
        in ROS terms and we will extract directly the file name
        """
        path = Path(path)
        if not path.exists():
            raise RuntimeError(f"The path `{path}` does not exists")

        package_name = self.parse_package_xml(path)
        
        for ext, msg_type, name_parser in zip(self.__class__.extension_list, 
                                              self.__class__.message_type_list,
                                              self.__class__.parser_list):
            file_list = [str(path.as_posix()) for path in path.glob(f"**/*{ext}")]
            for message in file_list:
                name_match = name_parser.match(message)
                if name_match is None:
                    raise RuntimeError(f"Cannot parse name for file `{message}`")
                name_str = f"{package_name}/{name_match.group('name')}"
                self.index[name_str] = message
                self.type_index[name_str] = msg_type

    def __str__(self):
        return_str = []
        for key in self.index:
            return_str.append(f" - {key} ({self.get_type(key)}) -> {self.get_path(key)}")
        return "\n".join(return_str)

    def get_path(self, msg_name):
        return self.index[msg_name]

    def get_type(self, msg_name):
        return self.type_index[msg_name]

    def parse(self, name):
        if name in self.index:
            parser = FileParser(name, self)
            parser.parse()
            return parser
    
    def parse_all(self):
        file_parsers  = {}
        for name in self.index:
            file_parsers[name] = self.parse(name)
        return file_parsers