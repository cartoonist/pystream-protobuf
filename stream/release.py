# coding=utf-8

"""Include release information of the 'pystream-protobuf' package."""

# CONSTANTS ####################################################################
# Development statuses:
DS_PLANNING = 1
DS_PREALPHA = 2
DS_ALPHA = 3
DS_BETA = 4
DS_STABLE = 5
DS_MATURE = 6
DS_INACTIVE = 7
DS_STRING = {
    DS_PLANNING: "Development Status :: 1 - Planning",
    DS_PREALPHA: "Development Status :: 2 - Pre-Alpha",
    DS_ALPHA: "Development Status :: 3 - Alpha",
    DS_BETA: "Development Status :: 4 - Beta",
    DS_STABLE: "Development Status :: 5 - Production/Stable",
    DS_MATURE: "Development Status :: 6 - Mature",
    DS_INACTIVE: "Development Status :: 7 - Inactive"
}
################################################################################

# Package release information.
__title__ = "stream"
__description__ = "Python implementation of stream library"
__author__ = "Ali Ghaffaari"
__email__ = "ali.ghaffaari@mpi-inf.mpg.de"
__license__ = "MIT"

# Release
__version__ = "1.3.4"
__status__ = DS_BETA

# PyPI-related information
__keywords__ = ['protobuf', 'stream', 'protocol buffer']
__classifiers__ = [
    # Development status
    DS_STRING[__status__],

    # License
    'License :: OSI Approved :: MIT License',

    # Supported Python versions.
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',

    # Intended Audience and Topic
    'Intended Audience :: Developers',
]
__requires__ = ['protobuf>=3.0.0']
__tests_require__ = []
__extras_require__ = {
    'test': ['nose'],
}
