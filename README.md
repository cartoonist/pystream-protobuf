[![Build Status](https://img.shields.io/travis/cartoonist/pystream-protobuf.svg?style=flat-square)](https://travis-ci.org/cartoonist/pystream-protobuf)
[![PyPI Release](https://img.shields.io/pypi/v/pystream-protobuf.svg?style=flat-square)](https://pypi.python.org/pypi/pystream-protobuf)
[![PyPI Status](https://img.shields.io/pypi/status/pystream-protobuf.svg?style=flat-square)](https://pypi.python.org/pypi/pystream-protobuf)
[![Python](https://img.shields.io/pypi/pyversions/pystream-protobuf.svg?style=flat-square)](https://www.python.org/download/releases/3.0/)
[![License](https://img.shields.io/pypi/l/pystream-protobuf.svg?style=flat-square)](https://github.com/cartoonist/pystream-protobuf/blob/master/LICENSE)

# pyStream
Python implementation of [stream library](https://github.com/vgteam/stream). It
enables stream processing of protobuf messages; i.e. multiple protobuf messages
can be written (read) into (from) a stream by using this library.  It can be
used for parsing all files encoded by stream library and writing protobuf
instances into a file by the same encoding. Refer to the library
[GitHub page](https://github.com/vgteam/stream) for more information about
formatting.

## Installation
You can install pyStream using `pip`:

    pip install pystream-protobuf

## Usage

### Reading
Here is a sample code to read a file containing a set of protobuf messages (here
is a set of [VG](https://github.com/vgteam/vg)'s Alignment objects, so-called
GAM file, defined [here](https://github.com/vgteam/vg/blob/master/src/vg.proto)).
It yields the protobuf objects stored in the file:

```python
import stream
import vg_pb2

alns = [a for a in stream.parse('test.gam', vg_pb2.Alignment)]
```

Or the lower-level method `open` can be used in order to have more control over
opening the stream and reading data:

```python
import stream
import vg_pb2

alns_list = []
with stream.open('test.gam', 'rb') as istream:
    for data in istream:
        aln = vg_pb2.Alignment()
        aln.ParseFromString(data)
        alns_list.append(aln)
```

The stream can be closed by calling `close` method explicitly, in which case the
stream is opened without using `with` statement (see more examples in the test
package).

### Writing
Multiple protobuf objects can be written into a file (here a GAM file) by
calling `dump` function:

```python
import stream

stream.dump('test.gam', *objects_list, buffer_size=10)
```

Or using `open` method for lower-level control. This example *appends* a set of
messages to the output stream:

```python
import stream

with stream.open('test.gam', 'ab') as ostream:
    ostream.write(*objects_list)
    ostream.write(*another_objects_list)
```

Similar to reading, the stream can be closed by explicitly calling `close`;
particularly when the stream is opened without using `with` statement.

## More features

### Optional GZip Compression
The streams encoded by [Stream library](https://github.com/vgteam/stream) is
GZip compressed. The compression can be disabled by passing `gzip=False` when
opening an stream.

### Buffered write
By default, all protobuf message objects provided on each call are written in a
group of messages (see [Stream library](https://github.com/vgteam/stream) for
encoding details). The messages can be buffered and write to the stream in a
group of fixed size whenever possible. The size of the buffer can be set by
keyword argument `buffer_size` to `open`, `dump` methods or when Stream class is
constructed (default size is 0 --- means no buffer).

### Grouping message
Messages can be grouped in varied size when writing to a stream by setting
buffer size sufficiently large or infinity (-1) and calling `flush` method
of Stream class whenever desired.

### Group delimiter
Group of objects can be separated by a delimiter of the choice (or by default
`None`) when reading from a stream. Sometimes, it can help to identify the end
of a group which is hidden from the library user by default. This feature can be
enable by setting `group_delimiter` to `True` when constructing a Stream
instance or opening a stream. The delimiter class can also be specified by
`delimiter_cls`.

## Development
In case, you work with the source code and need to build the package:

    python setup.py build

The proto file in the test module required to be compiled before running test
cases. To do so, it is required to have Google protobuf compiler (>=3.0.2)
installed. After installing protobuf compiler, run:

    make init

to compile proto files required for test module. Then, use `nosetests` command
of the setup script to execute test cases:

    python setup.py nosetests

