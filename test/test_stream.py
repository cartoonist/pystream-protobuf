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


def read_alns1(fpath, **kwargs):
    """Read protobuf objects from a file by using `with` statement.

    Here, as an example, the file is a GAM file containing Alignment messages
    defined in vg_pb2.

    Args:
        fpath (string): path of the file to be read.
    """
    with stream.open(fpath, 'rb', **kwargs) as istream:
        for data in istream:
            aln = vg_pb2.Alignment()
            aln.ParseFromString(data)
            yield aln


def read_alns2(fpath, **kwargs):
    """Read protobuf objects from a file without using `with` statement.

    Here, as an example, the file is a GAM file containing Alignment messages
    defined in vg_pb2.

    NOTE: Does the same as `read_alns1`.

    Args:
        fpath (string): path of the file to be read.
    """
    nof_groups = 0
    mode = 'rb'
    if kwargs.get('gzip', True):
        ifs = gzip.open(fpath, mode)
    else:
        ifs = open(fpath, mode)
    with ifs:
        istream = stream.open(fileobj=ifs, group_delimiter=True, **kwargs)
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

    It writes half of objects in one group, and then the other half in another
    one.

    Args:
        fpath (string): path of the file to be written.
        objs_list (*protobuf.message.Message): list of objects to be written.
    """
    with stream.open(fpath, 'wb', **kwargs) as ostream:
        length = len(objs_list)
        ostream.write(*objs_list[:length//2])
        ostream.write(*objs_list[length//2:])


def write_objs2(fpath, *objs_list, **kwargs):
    """Write protobuf message objects into the file w/o using `with` statement.

    It writes half of them in one group, and then the other half in another one
    by setting buffer size to half of the object list size.

    NOTE: Does the same as `write_objs1`.

    Args:
        fpath (string): path of the file to be written.
        objs_list (*protobuf.message.Message): list of objects to be written.
    """
    mode = 'wb'
    if kwargs.get('gzip', True):
        ofs = gzip.open(fpath, mode)
    else:
        ofs = open(fpath, mode)
    with ofs:
        ostream = stream.open(fileobj=ofs, mode='wb',
                              buffer_size=(len(objs_list)//2), **kwargs)
        ostream.write(*objs_list)
        ostream.close()


def test_low(**kwargs):
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
    write_objs1(rw1_gamfile, *alns, **kwargs)
    # Read the rewritten file.
    re_alns = [a for a in read_alns2(rw1_gamfile, **kwargs)]
    # Check the length of the objects storing in both files.
    assert len(alns) == len(re_alns)
    # Rewrite again the read data.
    write_objs2(rw2_gamfile, *re_alns, **kwargs)
    # Check whether the two generated files have the same the content.
    assert compare(rw1_gamfile, rw2_gamfile, **kwargs)
    # Remove the generated files.
    os.remove(rw1_gamfile)
    os.remove(rw2_gamfile)


def test_high(**kwargs):
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
    stream.dump(rw1_gamfile, *alns, buffer_size=len(alns)//2, **kwargs)
    # Read the rewritten file.
    re_alns = [a for a in read_alns2(rw1_gamfile, **kwargs)]
    # Check the length of the objects storing in both files.
    assert len(alns) == len(re_alns)
    # Rewrite again the read data.
    write_objs2(rw2_gamfile, *re_alns, **kwargs)
    # Check whether the two generated files have the same the content.
    assert compare(rw1_gamfile, rw2_gamfile, **kwargs)
    # Remove the generated files.
    os.remove(rw1_gamfile)
    os.remove(rw2_gamfile)


def test_low_no_gzip():
    """Run low-level methods tests with no compression."""
    return test_low(gzip=False)


def test_high_no_gzip():
    """Run high-level methods tests with no compression."""
    return test_high(gzip=False)


def compare_gzipped(first, second):
    """Compare two gzipped stream files.

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


def compare(first, second, **kwargs):
    """Compare two stream files.

    The stream can be gzipped or not specified by `gzipped` keyword argument.
    """
    if kwargs.get('gzip', True):
        return compare_gzipped(first, second)
    return filecmp.cmp(first, second)


if __name__ == '__main__':
    test_low()
    test_low_no_gzip()
    test_high()
    test_high_no_gzip()
