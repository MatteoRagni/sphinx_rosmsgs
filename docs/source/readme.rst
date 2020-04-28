Sphinx ROS Messages Extension
=============================

Installation
------------

Extension for parsing ROS / ROS 2 messages in Sphinx with a Docutils directive.

This project is still in beta, and many things are missing. It is not exactly easy to understand
how Sphinx works, but the main idea is that you install the extension::

    pip install -U git+https://github.com/matteoragni/sphinx_rosmsgs.git@master#egg=sphinx_rosmsgs

then you configure your ``conf.py`` with this global variable::

    rosmsg_path_root = [
        '../path/to/your/package_0', 
        '../path/to/your/package_1']


where the entries are the directory of your messages (where the ``package.xml`` is stored). To document a message use the following directive in your code::

    .. ros_message:: package_0/message_name


the message file will be searched inside the package. To document a message insert a continuous block of comments before the entry you want to comment, with reStructured text format.

You can also add a descriptive header in the message: to do so, leave a blank line (not a comment line) before the the first comment line of the first definition.

To Do
-----

A directive is still missing, in order to cross reference entry type in the documentation.
I should also clean the code, but the main problem with the whole codebase is that the actual parser of a file is not exactly complaint with the Sphinx application, so there are some things that are not exactly perfect.

I'm not keeping track of the current file and current line of file, that from a parser perspective it kinda sucks. It is possible to include this information in the Fields, and make them propagate from the ``FileParser`` and from the ``BlockParser`` to the final field, in order to have them available in the actual directive, to be Sphinx complaint. I will consider this maybe in the future.