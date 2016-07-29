try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='pystream-protobuf',
    packages=['stream'],
    version='0.9.1',
    description='Python implementation of stream library',
    author='Ali Ghaffaari',
    author_email='ali.ghaffaari@gmail.com',
    url='https://github.com/cartoonist/pystream-protobuf',
    download_url='https://github.com/cartoonist/pystream-protobuf/tarball/0.9.1',
    keywords=['protobuf', 'stream', 'protocol buffer'],
    classifiers=[],
    install_requires=['protobuf==3.0.0b4'],
)
