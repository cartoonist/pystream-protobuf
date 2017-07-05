# coding=utf-8

"""
    test.test_stream
    ~~~~~~~~~~~~~~~~

    Test stream.stream module.

    :copyright: (c) 2016 by Ali Ghaffaari.
    :license: MIT, see LICENSE for more details.
"""

import os
import gzip
import filecmp

from .context import stream
from . import vg_pb2


def read_alns1(fpath):
    """Read protobuf objects from a file by using `with` statement.

    Here, as an example, the file is a GAM file containing Alignment messages
    defined in vg_pb2.

    Args:
        fpath (string): path of the file to be read.
    """
    with stream.open(fpath, 'rb') as istream:
        for data in istream:
            aln = vg_pb2.Alignment()
            aln.ParseFromString(data)
            yield aln


def read_alns2(fpath):
    """Read protobuf objects from a file without using `with` statement.

    Here, as an example, the file is a GAM file containing Alignment messages
    defined in vg_pb2.

    NOTE: Do the same as `read_alns1`.

    Args:
        fpath (string): path of the file to be read.
    """
    nof_groups = 0
    istream = stream.open(fpath, 'rb', group_delimiter=True)
    for data in istream:
        if data is None:
            nof_groups += 1
            continue
        aln = vg_pb2.Alignment()
        aln.ParseFromString(data)
        yield aln
    istream.close()

    assert nof_groups == 2


def write_objs1(fpath, *objs_list):
    """Write protobuf message objects into the file by using `with` statement.

    It writes half of them in one group, and then the other half in another one.

    Args:
        fpath (string): path of the file to be written.
        objs_list (*protobuf.message.Message): list of objects to be written.
    """
    with stream.open(fpath, 'wb') as ostream:
        length = len(objs_list)
        ostream.write(*objs_list[:length//2])
        ostream.write(*objs_list[length//2:])


def write_objs2(fpath, *objs_list):
    """Write protobuf message objects into the file w/o using `with` statement.

    It writes half of them in one group, and then the other half in another one
    by setting buffer size to half of the object list size.

    NOTE: Do the same as `write_objs1`.

    Args:
        fpath (string): path of the file to be written.
        objs_list (*protobuf.message.Message): list of objects to be written.
    """
    ostream = stream.open(fpath, 'wb', buffer_size=(len(objs_list)//2))
    ostream.write(*objs_list)
    ostream.close()


def test_all():
    """Run all test cases."""
    # Files
    testdir = os.path.dirname(os.path.realpath(__file__))
    gamfile = os.path.join(testdir, 'sample_reads.gam')
    gamfile_nof_alns = 12
    rw1_gamfile = os.path.join(testdir, 'rw1_sample_reads.gam')
    rw2_gamfile = os.path.join(testdir, 'rw2_sample_reads.gam')
    # GUM file == Unzipped GAM file
    rw1_gumfile = os.path.join(testdir, 'rw1_sample_reads.gum')
    rw2_gumfile = os.path.join(testdir, 'rw2_sample_reads.gum')

    # Read a sample file.
    alns = [a for a in read_alns1(gamfile)]
    assert len(alns) == gamfile_nof_alns
    # Rewrite it into a new file in two groups of 6 objects.
    write_objs1(rw1_gamfile, *alns)
    # Read the rewritten file.
    re_alns = [a for a in read_alns2(rw1_gamfile)]
    # Check the length of the objects storing in both files.
    assert len(alns) == len(re_alns)
    # Rewrite again the read data.
    write_objs2(rw2_gamfile, *re_alns)
    # Unzip two generated files.
    with gzip.open(rw1_gamfile, 'rb') as gfp, \
            open(rw1_gumfile, 'wb') as ufp:
        ufp.write(gfp.read())
    with gzip.open(rw2_gamfile, 'rb') as gfp, \
            open(rw2_gumfile, 'wb') as ufp:
        ufp.write(gfp.read())
    # Check whether the two generated files have the same the content.
    assert filecmp.cmp(rw1_gumfile, rw2_gumfile)
    # Delete the generated files.
    os.remove(rw1_gamfile)
    os.remove(rw1_gumfile)
    os.remove(rw2_gamfile)
    os.remove(rw2_gumfile)


if __name__ == '__main__':
    test_all()
