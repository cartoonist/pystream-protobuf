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

    This class behaves like a file object. Once a stream is instantiated, it
    should be opened for reading or writing by calling `open()` method. The
    output would be an instance of Stream class which is iterable when it's
    opened for reading.
    In output streams (those are opened in 'w' mode), method `write()` gets a
    list of protobuf objects and writes them out into the file in the proper
    format compatible with stream library file format (refer to the stream
    library documentation for further information about the file format).

    The stream should be closed after performing all stream operations. Streams
    can be also used by `with` statement just like files.

    Here's a sample code using the Stream class to read from a file containing a
    set of vg's alignments (https://github.com/vgteam/vg). It yields the
    protobuf objects stored in the file:

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

    def _openfile(self):
        """Opens the file in the given mode."""
        assert self._fd is None
        self._fd = gzip.open(self.fpath, self.mode)

    def _closefile(self):
        """Closes the opened file."""
        self._fd.close()

    @classmethod
    def open(cls, fpath, mode='rb'):
        """Opens a stream."""
        instance = cls(fpath, mode)
        instance._openfile()
        return instance

    def __enter__(self):
        """Enters the runtime context related to Stream class. It will be
        automatically run by `with` statement. If the file related to the stream
        is not opened, it opens it.
        """
        if self._fd is None:
            self._openfile()
        return self

    def __exit__(self, *args):
        """Exits the runtime context related to Stream class. It will be
        automatically run by `with` statement. It closes the stream.
        """
        self.close()

    def __iter__(self):
        """Returns the iterator object of the stream."""
        return self._create_iterator()

    def _create_iterator(self):
        """A generator yielding all protobuf object data in the file. It is the
        main parser of the stream file format."""
        buff = self._fd.read()
        pos = 0
        while pos != len(buff):
            assert pos < len(buff)
            count, pos = varintDecoder(buff, pos)
            # Read a group containing `count` number of objects.
            for idx in range(count):
                size, pos = varintDecoder(buff, pos)
                # Read an object from the object group.
                yield buff[pos:pos+size]
                pos += size

    def close(self):
        """Closes the stream."""
        self._closefile()

    def write(self, *pb2_obj):
        """Writes a group of one or more  protobuf objects to the file. Multiple
        object groups can be written by calling this method sevral times before
        calling `close()` or exiting the runtime context.
        """
        count = len(pb2_obj)
        varintEncoder(self._fd.write, count)

        for obj in pb2_obj:
            s = obj.SerializeToString()
            varintEncoder(self._fd.write, len(s))
            self._fd.write(s)
