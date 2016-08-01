"""
setup.py
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PYPI_DISTNAME = "pystream-protobuf"

with open("VERSION", "r") as version:
    TAG = version.readline().strip()

setup(
    name=PYPI_DISTNAME,
    packages=['stream'],
    version=TAG,
    description='Python implementation of stream library',
    author='Ali Ghaffaari',
    author_email='ali.ghaffaari@gmail.com',
    url='https://github.com/cartoonist/pystream-protobuf',
    download_url='https://github.com/cartoonist/pystream-protobuf/tarball/'+TAG,
    keywords=['protobuf', 'stream', 'protocol buffer'],
    classifiers=[],
    install_requires=['protobuf==3.0.0b4'],
)
