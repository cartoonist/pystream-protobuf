#!/usr/bin/env python3
# coding=utf-8

# Python implementation of stream library
# https://github.com/vgteam/stream
#
# The MIT License (MIT)
#
# Copyright (c) 2016 Ali Ghaffaari
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""Test stream module."""

import os
import gzip
import filecmp
from context import stream
import vg_pb2


def read_alns1(fpath):
    """Read Alignment objects from a (GAM) file by using `with` statement.

    Args:
        fpath (string): path of the file to be read.
    """
    alns_list = []
    with stream.open(fpath, "rb") as istream:
        for data in istream:
            aln = vg_pb2.Alignment()
            aln.ParseFromString(data)
            alns_list.append(aln)
    return alns_list


def read_alns2(fpath):
    """Read Alignment objects from a (GAM) file without using `with` statement.

    Args:
        fpath (string): path of the file to be read.
    """
    alns_list = []
    istream = stream.open(fpath, "rb")
    for data in istream:
        aln = vg_pb2.Alignment()
        aln.ParseFromString(data)
        alns_list.append(aln)
    istream.close()
    return alns_list


def write_alns1(fpath, *objs_list):
    """Write 'Alignment' objects into the file by using `with` statement. It
    writes half of them in one group, and then the other half in another group.

    Args:
        fpath (string): path of the file to be written.
        objs_list (tuple: protobuf objects): list of objects to be written.
    """
    with stream.open(fpath, "wb") as ostream:
        length = len(objs_list)
        ostream.write(*objs_list[:length//2])
        ostream.write(*objs_list[length//2:])


def write_alns2(fpath, *objs_list):
    """Write 'Alignment' objects into the file without using `with` statement.
    It writes half of them in one group, and the other half in another group.

    Args:
        fpath (string): path of the file to be written.
        objs_list (tuple: protobuf objects): list of objects to be written.
    """
    ostream = stream.open(fpath, "wb", buffer_size=6)
    length = len(objs_list)
    ostream.write(*objs_list[:length//2])
    ostream.write(*objs_list[length//2:])
    ostream.close()


def test_all():
    """Run all test cases."""
    # Files
    testdir = os.path.dirname(os.path.realpath(__file__))
    gamfile = os.path.join(testdir, "sample_reads.gam")
    gamfile_nof_alns = 12
    rw1_gamfile = os.path.join(testdir, "rw1_sample_reads.gam")
    rw2_gamfile = os.path.join(testdir, "rw2_sample_reads.gam")
    # GUM file == Unzipped GAM file
    rw1_gumfile = os.path.join(testdir, "rw1_sample_reads.gum")
    rw2_gumfile = os.path.join(testdir, "rw2_sample_reads.gum")

    # Read a sample file.
    alns = read_alns1(gamfile)
    assert len(alns) == gamfile_nof_alns
    # Rewrite it into a new file in two groups of 6 objects.
    write_alns1(rw1_gamfile, *alns)
    # Read the rewritted file.
    re_alns = read_alns2(rw1_gamfile)
    # Check the length of the objects storing in both files.
    assert len(alns) == len(re_alns)
    # Rewrite again the read data.
    write_alns2(rw2_gamfile, *re_alns)
    # Unzip two generated files.
    with gzip.open(rw1_gamfile, "rb") as gfp, \
            open(rw1_gumfile, "wb") as ufp:
        ufp.write(gfp.read())
    with gzip.open(rw2_gamfile, "rb") as gfp, \
            open(rw2_gumfile, "wb") as ufp:
        ufp.write(gfp.read())
    # Check whether the two generated files have the same the content.
    assert filecmp.cmp(rw1_gumfile, rw2_gumfile)
    # Delete the generated files.
    os.remove(rw1_gamfile)
    os.remove(rw1_gumfile)
    os.remove(rw2_gamfile)
    os.remove(rw2_gumfile)

if __name__ == "__main__":
    test_all()
