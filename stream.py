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

"""Python implementation of stream library (https://github.com/vgteam/stream)
parsing all files encoded by stream and writing protobuf message instances into
the file by the same encoding.
"""

# TODO: Implement other methods of stream library such as `write_buffered()` or
#    `for_each_parallel()`.

import gzip
from google.protobuf.internal.decoder import _DecodeVarint as varintDecoder
from google.protobuf.internal.encoder import _EncodeVarint as varintEncoder


class Stream(object):
    """Stream class.

    This class behaves like a file-object by providing `open()` and `close()`
    methods. It also implements context manager methods `__enter__()` and
    `__exit__()`, so that it can be used in `with` statement.

    Here's a sample code using the Stream class to read from a file containing a
    set of alignments. It yields the protobuf objects stored in the file:

        alns_list = []
        with Stream.open("test.gam", "rb") as stream:
            for aln_data in stream:
                aln = Alignment()
                aln.ParseFromString(aln_data)
                alns_list.append(aln)

    Or

        alns_list = []
        stream = Stream.open("test.gam", "rb")
        for aln_data in stream:
            aln = Alignment()
            aln.ParseFromString(aln_data)
            alns_list.append(aln)
        stream.close()

    And here is a sample code for writing multiple protobuf objects into a file:

        with Stream.open("test.gam", "wb") as stream:
            stream.write(*objects_list)
            stream.write(*another_objects_list)

    Or

        stream = Stream.open("test.gam", "wb")
        stream.write(*objects_list)
        stream.write(*another_objects_list)
        stream.close()
    """
    def __init__(self, fpath=None, mode='rb'):
        """Constructor for the Stream class.

        Args:
            fpath (string): Path of the working file.
            mode (string): The mode argument can be any of 'r', 'rb', 'a', 'ab',
                'w', or 'wb', depending on whether the file will be read or
                written. The default is 'rb'.
        """
        self.fpath = fpath
        self.mode = mode
        self._fd = None

    @classmethod
    def open(cls, fpath, mode='rb'):
        """Mock function to mimic `open` method from file-like classes."""
        return cls(fpath, mode)

    def __enter__(self):
        """Opens the file. It should be run before doing any operation on the
        file. It will automatically run by `with` statement.
        """
        self._fd = gzip.open(self.fpath, self.mode)
        return self

    def __exit__(self, *args):
        """Closes the file. It should be run after all operation on the file. It
        will automatically run by `with` statement.
        """
        if self._fd is not None:
            self._fd.close()

    def __iter__(self):
        """Returns the iterator object."""
        return self._create_iterator()

    def _create_iterator(self):
        """Yields all protobuf object data in the file."""
        if self._fd is None:
            self.__enter__()

        buff = self._fd.read()
        pos = 0
        while pos != len(buff):
            assert pos < len(buff)
            count, pos = varintDecoder(buff, pos)
            for idx in range(count):
                size, pos = varintDecoder(buff, pos)
                yield buff[pos:pos+size]
                pos += size

    def close(self):
        """Same as `__exit__()` to close the file handler manually (without
        using `with` statement).
        """
        self.__exit__()

    def write(self, *pb2_obj):
        """Writes one or more  protobuf objects to the file. A list of protobuf
        objects can be written by calling this method sevral times before
        calling `close()` or `__exit__()` methods.
        """
        count = len(pb2_obj)
        varintEncoder(self._fd.write, count)

        for obj in pb2_obj:
            s = obj.SerializeToString()
            varintEncoder(self._fd.write, len(s))
            self._fd.write(s)
