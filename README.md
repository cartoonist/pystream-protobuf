[![Build Status](https://img.shields.io/travis/cartoonist/pystream-protobuf.svg?style=flat-square)](https://travis-ci.org/cartoonist/pystream-protobuf)
[![PyPI Release](https://img.shields.io/pypi/v/pystream-protobuf.svg?style=flat-square)](https://pypi.python.org/pypi/pystream-protobuf)
[![PyPI Status](https://img.shields.io/pypi/status/pystream-protobuf.svg?style=flat-square)](https://pypi.python.org/pypi/pystream-protobuf)
[![Python](https://img.shields.io/pypi/pyversions/pystream-protobuf.svg?style=flat-square)](https://www.python.org/download/releases/3.0/)
[![License](https://img.shields.io/pypi/l/pystream-protobuf.svg?style=flat-square)](https://github.com/cartoonist/pystream-protobuf/blob/master/LICENSE)

# pyStream
Python implementation of [stream library](https://github.com/vgteam/stream).

## Introduction
This library enables _stream processing_ of protobuf messages (or any serializable
objects since v1.6.3); i.e. multiple protobuf messages can be written/read into/from a
single stream or file.

It was originally developed to parse/write [vg](https://github.com/vgteam/vg)
file formats (`.vg`, `.gam`, etc). However, it can be used for any arbitrary
protocol buffer messages.

Refer to the C++ [stream library](https://github.com/vgteam/stream) for more
details.

---
**NOTE**

**@vg users:** The new version of stream library, now as a part of
[libvgio](https://github.com/vgteam/libvgio), writes a header at the start of
the stream depending on the output format. For example, headers like `b'GAM'`
or `b'VG'` can be found before the actual protobuf messages in GAM and VG files
repectively. In this case, you should provide the expected value using `header`
keyword argument; e.g.
`stream.parse('file.gam', vg_pb2.Alignment, header=b'GAM')`
for GAM files (since version v1.6.2).

---

## Encoding
The encoding is simple. Messages are written in groups of different sizes. Each
group starts with its size; i.e. the number of messages in that group. Then, the
size of each message is followed by the encoded message itself. Quoted from
[Google Protobuf Developer Guide](https://developers.google.com/protocol-buffers/docs/techniques#streaming):

> The Protocol Buffer wire format is not self-delimiting, so protocol buffer
> parsers cannot determine where a message ends on their own. The easiest way to
> solve this problem is to write the size of each message before you write the
> message itself. When you read the messages back in, you read the size, then
> read the bytes into a separate buffer, then parse from that buffer.

By default, the stream is considered compressed by GZip. However, uncompressed
stream processing is possible by passing `gzip=False` to any API calls.

## Installation
You can install pyStream using `pip`:

    pip install pystream-protobuf

## Usage
See [Wiki](https://github.com/cartoonist/pystream-protobuf/wiki) for usage documentation.

## Development
In case, you work with the source code and need to build the package:

    python setup.py build

The proto files in the test module required to be compiled before running test
cases. To do so, it is required to have Google protobuf compiler (>=3.0.2)
installed. After installing protobuf compiler, run:

    make init

to compile proto files required for test module and then:

    make test

to run tests.
