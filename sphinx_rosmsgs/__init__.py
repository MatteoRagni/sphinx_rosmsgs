from sphinx_rosmsgs.__version__ import __version__
from sphinx_rosmsgs.message_directive import MessageDirective
from sphinx_rosmsgs.message_indexer import MessageIndexer


def on_config_inited(app, *args):
    r"""
    The event is used to collect the user configuration and register
    a global message indexer accordingly to user configuration.

    The global indexer will be used inside the directive to parse the
    actual files.

    :param app: sphinx app, for configuration
    :param args: unused arguments
    """
    paths = app.config["rosmsg_path_root"]
    if isinstance(paths, str):
        paths = [paths]
    MessageIndexer.register_global(paths)


def setup(app):
    r"""
    Entry point for the extension

    :param app: sphinx application
    :return: disctionary with extension's information
    :rtype: dict
    """
    app.add_config_value('rosmsg_path_root', [], 'env')
    app.add_directive("ros_message", MessageDirective)
    app.connect('config-inited', on_config_inited)
    return {
        'version': __version__,
    }


