"""
setup.py
"""

import sys
import subprocess

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

PYPI_DISTNAME = "pystream-protobuf"

PROC = subprocess.run(["git", "log", "-n1", "--pretty=%h"],
                      stdout=subprocess.PIPE, stderr=subprocess.PIPE)

if PROC.returncode == 0:
    COMMIT = PROC.stdout.decode("utf-8").strip()
    PROC = subprocess.run(["git", "describe", "--exact-match", "--tags", COMMIT],
                        stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    if PROC.returncode != 0:
        print("ERROR: there's no tag associated with the current commit",
            file=sys.stderr)
        print("> %s" % PROC.stderr.decode("utf-8").strip(), file=sys.stderr)
        exit(1)

    TAG = PROC.stdout.decode("utf-8").strip()
else:
    import pkg_resources
    dist = pkg_resources.get_distribution(PYPI_DISTNAME)
    TAG = dist.version

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
