import re
from pathlib import Path
import xml.etree.cElementTree as ElementTree
from sphinx_rosmsgs.file_parser import FileParser


class MessageIndexer:
    r"""
    The message indexer parses all the directory provided in a list of paths
    searching for ``package.xml`` files and for indexing all messages in the 
    directory.

    The indexer keeps track of the relationship name source file and the relation
    name type of message (`message`, `service` or `action`). From the name it is
    possible to create a parser, that will read the whole file and parse it in
    blocks, that will contain the comments and the definitions.

    There exists a global indexer, which is created for interpoperation with sphinx,
    but the indexer is independent with respect to the sphinx software.

    Let's make an example: we have ``/path/to/package_0``, a ROS 2 package with file 
    ``/path/to/package_0/package.xml`` and with a service file in the following path:
    ``/path/to/package_0/srv/service_message.srv``. 
    
    If we pass to the indexer the following path list: ``["/path/to/package_0"]`` 
    and the ``<name>package_0</name>`` tag is in the ``package.xml`` file, 
    the indexer will have the following mapping between ``package_0/service_message`` 
    and the ``/path/to/package_0/srv/service_message.srv`` file, and the type mapping 
    between ``package_0/service_message`` to `service` string.

    :param path_list: a list of path to the ROS packages to be included in the 
                      indexer. There should be only one indexer.
    """

    global_name = "__message__indexer__"
    message_ext = ".msg"
    service_ext = ".srv"
    action_ext = ".action"
    package_xml = "package.xml"
    message_type_list = ["message", "service", "action"]
    is_init = False

    @classmethod
    def register_global(klass, path_list):
        r"""
        Register a global indexer to be used by the shping extension. This global indexer is
        kinda sort of singularity.

        :return: the global MessageIndexer
        :rtype: MessageIndexer
        """
        globals()[klass.global_name] = klass(path_list)
        return klass.retrieve_global()

    @classmethod
    def retrieve_global(klass):
        r"""
        Retrieve the global class::`MessageIndexer`. Raises an error if the global message indexer
        was never registered, but in the sphinx extension case is registered when the event
        of complete configuration is triggered.

        :return: the global message indexer
        :rtype: MessageIndexer
        """
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
        r"""
        Index all the entries in the path list to create the maps.

        This method is called inside the contructor.
        """
        for path in self.path_list:
            self._index_path(path)

    def _parse_package_xml(self, path):
        r"""
        Extract current package name from ``package.xml`` ROS file. It raises if
        cannot find or cannot parse the ``package.xml`` file.

        :param path: path of the package, where we search for ``package.xml``
        :raise RuntimeError: when it cannot find the file or cannot parse it
        :return: a string with the name of the package
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

    def _index_path(self, path):
        r"""
        Search for all messages in one of the provided path. In this way we have a mapping
        between a file and its path. The user will put in the func::`get_path` method
        the name of the message in ROS terms and we will extract directly the file 
        name from the indexer. The indexer also scans the type using the extension of
        the file. All the file with recognized extensions are extracted from the package 
        path.

        :param path: path of the package to scan
        :raise RuntimeError: if the file has an invalid name for the message or the 
                             package path does not exists
        """
        path = Path(path)
        if not path.exists():
            raise RuntimeError(f"The path `{path}` does not exists")

        package_name = self._parse_package_xml(path)
        
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

    def get_path(self, msg_name):
        r"""
        Return the path of a message, given its name.

        :param msg_name: the message name in ROS terms
        :return: the path of the file
        :rtype: str
        :raise KeyError: if the name does not exists
        """
        return self.index[msg_name]

    def get_type(self, msg_name):
        r"""
        Return the type of a message, given its name and its file extension.

        :param msg_name: the message name in ROS terms
        :return: one of `message`, `service` or `action` string
        :rtype: str
        :raise KeyError: if the name does not exists
        """
        return self.type_index[msg_name]

    def parse(self, name):
        r"""
        Returns a container with the complete parsed message. The container is also 
        the parser.

        :param name: the name of the message in ROS terms
        :return: a file parser object that has already parsed the message
        :rtype: FileParser
        :raise KeyError: if the name does not exists in the index
        """
        if name in self.index:
            parser = FileParser(name, self.get_path(name), self.get_type(name))
            parser.parse()
            return parser
    
    def parse_all(self):
        r"""
        Shorcut for running the parse on all the indexed messages

        :return: a dictionary with message name pointing to corresponding
                 class:`FileParser` objects
        :rtype: dict
        """
        file_parsers  = {}
        for name in self.index:
            file_parsers[name] = self.parse(name)
        return file_parsers