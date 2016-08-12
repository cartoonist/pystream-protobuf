"""
setup.py
"""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

with open("VERSION", "r") as version:
    TAG = version.readline().strip()

PYPI_DISTNAME = "pystream-protobuf"
PACKAGE_NAME = "stream"
DESCRIPTION = "Python implementation of stream library"
GIT_URL = "https://github.com/cartoonist/"
VCS_URL = GIT_URL + PYPI_DISTNAME
TAR_URL = GIT_URL + PYPI_DISTNAME + "/tarball/" + TAG
KEYWORDS = ['protobuf', 'stream', 'protocol buffer']
REQUIRES = ['protobuf==3.0.0']
AUTHOR = "Ali Ghaffaari"
EMAIL = "ali.ghaffaari@gmail.com"

setup(
    name=PYPI_DISTNAME,
    packages=[PACKAGE_NAME],
    version=TAG,
    description=DESCRIPTION,
    author=AUTHOR,
    author_email=EMAIL,
    url=VCS_URL,
    download_url=TAR_URL,
    keywords=KEYWORDS,
    classifiers=[],
    install_requires=REQUIRES,
)
