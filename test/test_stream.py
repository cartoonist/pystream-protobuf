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


def read_alns1(fpath, gzip=True):
    """Read protobuf objects from a file by using `with` statement.

    Here, as an example, the file is a GAM file containing Alignment messages
    defined in vg_pb2.

    Args:
        fpath (string): path of the file to be read.
    """
    with stream.open(fpath, 'rb', gzip=gzip) as istream:
        for data in istream:
            aln = vg_pb2.Alignment()
            aln.ParseFromString(data)
            yield aln


def read_alns2(fpath, gzip=True):
    """Read protobuf objects from a file without using `with` statement.

    Here, as an example, the file is a GAM file containing Alignment messages
    defined in vg_pb2.

    NOTE: Do the same as `read_alns1`.

    Args:
        fpath (string): path of the file to be read.
    """
    nof_groups = 0
    istream = stream.open(fpath, 'rb', group_delimiter=True, gzip=gzip)
    for data in istream:
        if data is None:
            nof_groups += 1
            continue
        aln = vg_pb2.Alignment()
        aln.ParseFromString(data)
        yield aln
    istream.close()

    assert nof_groups == 2


def write_objs1(fpath, *objs_list, **kwargs):
    """Write protobuf message objects into the file by using `with` statement.

    It writes half of them in one group, and then the other half in another one.

    Args:
        fpath (string): path of the file to be written.
        objs_list (*protobuf.message.Message): list of objects to be written.
    """
    with stream.open(fpath, 'wb', gzip=kwargs.get('gzip', True)) as ostream:
        length = len(objs_list)
        ostream.write(*objs_list[:length//2])
        ostream.write(*objs_list[length//2:])


def write_objs2(fpath, *objs_list, **kwargs):
    """Write protobuf message objects into the file w/o using `with` statement.

    It writes half of them in one group, and then the other half in another one
    by setting buffer size to half of the object list size.

    NOTE: Do the same as `write_objs1`.

    Args:
        fpath (string): path of the file to be written.
        objs_list (*protobuf.message.Message): list of objects to be written.
    """
    ostream = stream.open(fpath, 'wb', buffer_size=(len(objs_list)//2),
                          gzip=kwargs.get('gzip', True))
    ostream.write(*objs_list)
    ostream.close()


def test_low(gzip=True):
    """Run low-level methods tests."""
    # Files
    testdir = os.path.dirname(os.path.realpath(__file__))
    gamfile = os.path.join(testdir, 'sample_reads.gam')
    gamfile_nof_alns = 12
    rw1_gamfile = os.path.join(testdir, 'rw1_sample_reads.gam')
    rw2_gamfile = os.path.join(testdir, 'rw2_sample_reads.gam')

    # Read a sample file.
    alns = [a for a in read_alns1(gamfile)]
    assert len(alns) == gamfile_nof_alns
    # Rewrite it into a new file in two groups of 6 objects.
    write_objs1(rw1_gamfile, *alns, gzip=gzip)
    # Read the rewritten file.
    re_alns = [a for a in read_alns2(rw1_gamfile, gzip=gzip)]
    # Check the length of the objects storing in both files.
    assert len(alns) == len(re_alns)
    # Rewrite again the read data.
    write_objs2(rw2_gamfile, *re_alns, gzip=gzip)
    # Check whether the two generated files have the same the content.
    assert compare(rw1_gamfile, rw2_gamfile, gzip=gzip)
    # Remove the generated files.
    os.remove(rw1_gamfile)
    os.remove(rw2_gamfile)


def test_high(gzip=True):
    """Run high-level methods tests."""
    # Files
    testdir = os.path.dirname(os.path.realpath(__file__))
    gamfile = os.path.join(testdir, 'sample_reads.gam')
    gamfile_nof_alns = 12
    rw1_gamfile = os.path.join(testdir, 'rw1_sample_reads.gam')
    rw2_gamfile = os.path.join(testdir, 'rw2_sample_reads.gam')

    # Read a sample file.
    alns = [a for a in stream.parse(gamfile, vg_pb2.Alignment)]
    assert len(alns) == gamfile_nof_alns
    # Rewrite it into a new file in two groups of 6 objects.
    stream.dump(rw1_gamfile, *alns, buffer_size=len(alns)//2, gzip=gzip)
    # Read the rewritten file.
    re_alns = [a for a in read_alns2(rw1_gamfile, gzip=gzip)]
    # Check the length of the objects storing in both files.
    assert len(alns) == len(re_alns)
    # Rewrite again the read data.
    write_objs2(rw2_gamfile, *re_alns, gzip=gzip)
    # Check whether the two generated files have the same the content.
    assert compare(rw1_gamfile, rw2_gamfile, gzip=gzip)
    # Remove the generated files.
    os.remove(rw1_gamfile)
    os.remove(rw2_gamfile)


def test_low_no_gzip():
    return test_low(gzip=False)


def test_high_no_gzip():
    return test_high(gzip=False)


def compare_gzipped(first, second):
    """Compare two stream files.

    Since the stream files are gzipped and the file name is included in the
    compressed file, they need to be decompressed first before comparing their
    contents.

    Args:
        first (string): path to the first stream file.
        second (string): path to the second stream file.
    """
    ungz_first = '.ungz'.join(os.path.splitext(first))
    ungz_second = '.ungz'.join(os.path.splitext(second))

    # Unzip first file.
    with gzip.open(first, 'rb') as gfp, open(ungz_first, 'wb') as ufp:
        ufp.write(gfp.read())
    # Unzip second file.
    with gzip.open(second, 'rb') as gfp, open(ungz_second, 'wb') as ufp:
        ufp.write(gfp.read())
    # Compare two unzipped files.
    result = filecmp.cmp(ungz_first, ungz_second)
    # Remove decompressed files.
    os.remove(ungz_first)
    os.remove(ungz_second)

    return result


def compare(first, second, gzip=True):

    if gzip:
        return compare_gzipped(first, second)
    else:
        return filecmp.cmp(first, second)


if __name__ == '__main__':
    test_low(gzip=True)
    test_low(gzip=False)
    test_high(gzip=True)
    test_high(gzip=False)
