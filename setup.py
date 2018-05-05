# coding=utf-8

"""
    setup.py
    ~~~~~~~~

    Setup script.

    :copyright: (c) 2016 by Ali Ghaffaari.
    :license: MIT, see LICENSE for more details.
"""

import os
import codecs
from setuptools import setup, find_packages


_HERE = os.path.abspath(os.path.dirname(__file__))

# Get package release information.
_PACKAGE_NAME = "stream"
_RELEASE_INFO = {}
with open(os.path.join(_HERE, _PACKAGE_NAME, 'release.py')) as release_file:
    exec(release_file.read(), _RELEASE_INFO)  # pylint: disable=exec-used

# Get the long description from the README file.
with codecs.open(os.path.join(_HERE, 'README.md'), encoding='utf-8') as f:
    LONG_DESCRIPTION = f.read()

_PYPINAME = "pystream-protobuf"
_PACKAGES = find_packages(exclude=['test'])
_GITHUB_BASE = "https://github.com/cartoonist/"
_VCS_URL = _GITHUB_BASE + _PYPINAME
_TAR_URL = _VCS_URL + "/tarball/" + _RELEASE_INFO['__version__']

setup(
    name=_PYPINAME,
    packages=_PACKAGES,
    version=_RELEASE_INFO['__version__'],
    description=_RELEASE_INFO['__description__'],
    long_description=LONG_DESCRIPTION,
    long_description_content_type='text/markdown',
    author=_RELEASE_INFO['__author__'],
    author_email=_RELEASE_INFO['__email__'],
    license=_RELEASE_INFO['__license__'],
    url=_VCS_URL,
    download_url=_TAR_URL,
    keywords=_RELEASE_INFO['__keywords__'],
    classifiers=_RELEASE_INFO['__classifiers__'],
    install_requires=_RELEASE_INFO['__requires__'],
    tests_require=_RELEASE_INFO['__tests_require__'],
    extras_require=_RELEASE_INFO['__extras_require__'],
    setup_requires=_RELEASE_INFO['__setup_requires__'],
    entry_points=_RELEASE_INFO['__entry_points__'],
)
