import sys
sys.path.insert(0, ".")
import sphinx_rosmsgs
from setuptools import setup

setup(name='sphinx_rosmsgs',
      version=sphinx_rosmsgs.__version__,
      description='A Shinx extension for parsing ROS / ROS 2 messages',
      url='http://github.com/matteoragni/sphinx_rosmsgs',
      author='Matteo Ragni',
      author_email='info@ragni.me',
      license='MIT',
      packages=['sphinx_rosmsgs', 'sphinx_rosmsgs.file_parser'],
      zip_safe=False)