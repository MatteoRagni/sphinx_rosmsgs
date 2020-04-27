from .__version__ import __version__
from .message_directive import MessageDirective
from .message_indexer import MessageIndexer


def config_inited_event_callback(app, *args):
    paths = app.config["rosmsg_path_root"]
    if isinstance(paths, str):
        paths = [paths]
    MessageIndexer.register_global(paths)


def setup(app):
    app.add_config_value('rosmsg_path_root', [], 'env')
    app.add_directive("ros_message", MessageDirective)
    app.connect('config-inited', config_inited_event_callback)
    return {
        'version': __version__,
    }


