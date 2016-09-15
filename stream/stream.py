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

import gzip
from google.protobuf.internal.decoder import _DecodeVarint as varintDecoder
from google.protobuf.internal.encoder import _EncodeVarint as varintEncoder


def open(fpath, mode='rb', buffer_size=-1):  # pylint: disable=redefined-builtin
    """Open an stream."""
    return Stream(fpath, mode, buffer_size)


class Stream(object):
    """Stream class.

    Read and write protocol buffer streams encoded by 'stream' library. Stream
    objects instantiated for reading by setting mode to 'rb' (input `Stream`s)
    are iterable. So, protobuf objects can be obtained by iterate over the
    Stream. Stream iterator yields protobuf encoded data, so it should be parsed
    by using proper methods in Google Protocol Buffer library (for example
    `ParseFromString()` method).

    In output `Stream`s (those are instantiated with 'w' mode), method `write()`
    groups the given list of protobuf objects and writes them into the stream in
    the same format which is readable by any other parsers (refer to the stream
    library documentation for further information).

    The stream should be closed after performing all stream operations. Streams
    can be also used by `with` statement just like files.

    Here's a sample code using the Stream class to read from a file (so-called
    GAM file) containing a set of VG's (https://github.com/vgteam/vg) Alignment
    objects (defined: https://github.com/vgteam/vg/blob/master/src/vg.proto). It
    yields the protobuf objects stored in the file:

        import stream
        import vg_pb2

        alns_list = []
        with stream.open("test.gam", "rb") as istream:
            for data in istream:
                aln = vg_pb2.Alignment()
                aln.ParseFromString(data)
                alns_list.append(aln)

    Or

        import stream
        import vg_pb2

        alns_list = []
        istream = stream.open("test.gam", "rb")
        for data in istream:
            aln = vg_pb2.Alignment()
            aln.ParseFromString(data)
            alns_list.append(aln)
        istream.close()

    And here is another sample code for writing multiple protobuf objects into a
    file (here a GAM file):

        with stream.open("test.gam", "wb") as ostream:
            ostream.write(*objects_list)
            ostream.write(*another_objects_list)

    Or

        ostream = stream.open("test.gam", "wb")
        ostream.write(*objects_list)
        ostream.write(*another_objects_list)
        ostream.close()
    """
    def __init__(self, fpath, mode='rb', buffer_size=-1):
        """Constructor for the Stream class.

        Args:
            fpath (string): Path of the working file.
            mode (string): The mode argument can be any of 'r', 'rb', 'a', 'ab',
                'w', or 'wb', depending on whether the file will be read or
                written. The default is 'rb'.
            buffer_size (int): Write buffer size. The objects will be buffered
                before writing. No buffering will be made if buffer_size is -1.
        """
        self._fd = gzip.open(fpath, mode)
        self._buffer_size = buffer_size
        self._write_buff = []

    def __enter__(self):
        """Enter the runtime context related to Stream class. It will be
        automatically run by `with` statement.
        """
        return self

    def __exit__(self, *args):
        """Exit the runtime context related to Stream class. It will be
        automatically run by `with` statement. It closes the stream.
        """
        self.close()

    def __iter__(self):
        """Return the iterator object of the stream."""
        return self._get_objs()

    def _read_varint(self):
        """Read a varint from file, parse it, and return the decoded integer."""
        buff = self._fd.read(1)
        if buff == b'':
            return 0

        while (buff[-1] & 0x80) >> 7 == 1:  # while the MSB is 1
            new_byte = self._fd.read(1)
            if new_byte == b'':
                raise EOFError('unexpected EOF.')
            buff += new_byte

        varint, _ = varintDecoder(buff, 0)

        return varint

    def _get_objs(self):
        """A generator yielding all protobuf object data in the file. It is the
        main parser of the stream encoding.
        """
        while True:
            count = self._read_varint()
            if count == 0:
                break
            # Read a group containing `count` number of objects.
            for _ in range(count):
                size = self._read_varint()
                if size == 0:
                    raise EOFError('unexpected EOF.')
                # Read an object from the object group.
                yield self._fd.read(size)

    def close(self):
        """Close the stream."""
        self.flush()
        self._fd.close()

    def write(self, *pb2_obj):
        """Write a group of one or more protobuf objects to the file. Multiple
        object groups can be written by calling this method several times before
        closing stream or exiting the runtime context.

        The input protobuf objects get buffered and will be written down when
        the number of buffered objects exceed the `self._buffer_size`.
        """
        count = len(self._write_buff)
        if count >= self._buffer_size:
            self.flush()

        for obj in pb2_obj:
            self._write_buff.append(obj)

    def flush(self):
        """Write down buffer to the file."""
        count = len(self._write_buff)
        if count == 0:
            return

        varintEncoder(self._fd.write, count)

        for obj in self._write_buff:
            obj_str = obj.SerializeToString()
            varintEncoder(self._fd.write, len(obj_str))
            self._fd.write(obj_str)

        self._write_buff = []
