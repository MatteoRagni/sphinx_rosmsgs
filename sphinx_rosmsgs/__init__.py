# from pathlib import Path
from .message_directive import MessageDirective
from .message_indexer import MessageIndexer
# from sphinx.domains.std import StandardDomain


# class MessagesDomain(StandardDomain):
#     name = "ros2_msgs"
#     label = "ROS 2 Messages"

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
        'version': '0.1',
    }


