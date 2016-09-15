# coding=utf-8

"""Generate a 'requirements.txt' file based on the release information defined
in `stream.release` module. It particularly reads `install_requires` and
`tests_require` fields.
"""

import os


def get_release_globals():
    """Read release module and extract `__requires__` and `__tests_require__`.

    This script is executed when required packages are not installed. So, the
    package cannot be imported. This function reads the release.py in stream
    package and extract `__requires__` and `__tests_require__` global variables
    from the script.

    Return:
        tuple(__requires__, __tests_require__)
    """
    with open(os.path.join('stream', 'release.py')) as release_file:
        exec(release_file.read(), globals())         # pylint: disable=exec-used
        return (__requires__,          # noqa pylint: disable=undefined-variable
                __tests_require__)     # noqa pylint: disable=undefined-variable


def write_reqfile():
    """Read release information and generate requirements file."""
    with open('requirements.txt', 'wt') as reqfile:
        requires, tests_require = get_release_globals()
        # Write install requirements.
        for req in requires:
            reqfile.write(req)
            reqfile.write('\n')

        # Write tests requirements.
        for treq in tests_require:
            reqfile.write(treq)
            reqfile.write('\n')


if __name__ == '__main__':
    write_reqfile()
