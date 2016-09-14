# coding=utf-8

"""Setup script."""

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

import stream

_PYPINAME = "pystream-protobuf"
_PACKAGES = [stream.release.__title__] + stream.release.__subpackages__
_GITHUB_BASE = "https://github.com/cartoonist/"
_VCS_URL = _GITHUB_BASE + _PYPINAME
_TAR_URL = _VCS_URL + "/tarball/" + stream.release.__version__


setup(
    name=_PYPINAME,
    packages=_PACKAGES,
    version=stream.release.__version__,
    description=stream.release.__description__,
    author=stream.release.__author__,
    author_email=stream.release.__email__,
    url=_VCS_URL,
    download_url=_TAR_URL,
    keywords=stream.release.__keywords__,
    classifiers=stream.release.__classifiers__,
    install_requires=stream.release.__requires__,
    tests_require=stream.release.__tests_require__,
)
