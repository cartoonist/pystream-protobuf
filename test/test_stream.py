#!/usr/bin/env python3

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

"""Tests stream class."""

import os
import sys
from vg_pb2 import Alignment

sys.path.insert(0, os.path.abspath('..'))

from stream import Stream  #noqa


def read_aln1(fpath):
    """Reads all 'Alignment' objects from a file.

    Args:
        fpath (string): path of the file to be read.
    """
    alns_list = []
    with Stream.open(fpath, "rb") as stream:
        for aln_data in stream:
            aln = Alignment()
            aln.ParseFromString(aln_data)
            alns_list.append(aln)
    return alns_list
#    with gzip.open(filename, 'rb') as fp:
#        buff = fp.read()
#        pos = 0
#        while pos != len(buff):
#            assert pos < len(buff)
#            count, pos = varintdecoder(buff, pos)
#            print("Reading an object group including %d object(s)..." % count)
#            for idx in range(count):
#                size, pos = varintdecoder(buff, pos)
#                print("Reading object %d with size %d bytes..." %
#                      (idx + 1, size))
#                instance = cl()
#                instance.ParseFromString(buff[pos:pos+size])
#                print(instance)
#                print("Adding to result list...")
#                result.append(instance)
#                pos += size


def write_aln1(fpath, *objs_list):
    """Write 'Alignment' objects into the file.

    Args:
        fpath (string): path of the file to be written.
        objs_list (tuple of protobuf objects): list of objects to be written.
    """
    with Stream.open(fpath, "wb") as stream:
        stream.write(*objs_list)


def test_all():
    """Runs all test cases."""
    alns = read_aln1("sample_reads.gam")
    write_aln1("re.sample_reads.gam", *alns)
    read_alns = read_aln1("re.sample_reads.gam")
    assert len(alns) == len(read_alns)
    write_aln1("re.re.sample_reads.gam", *read_alns)

if __name__ == "__main__":
    test_all()
