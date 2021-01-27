# coding=utf-8

"""
    test.test_stream
    ~~~~~~~~~~~~~~~~

    Test stream.stream module.

    :copyright: (c) 2016 by Ali Ghaffaari.
    :license: MIT, see LICENSE for more details.
"""

import os
import sys
import gzip
import unittest
import asyncio
import socket
import filecmp

from .context import stream
from . import vg_pb2


class TestStream(unittest.TestCase):
    testdir = os.path.dirname(os.path.realpath(__file__))
    files = [{'file': os.path.join(testdir, 'sample.gam'),
              'class': vg_pb2.Alignment,
              'size': 12,
              'nof_groups': 6,
              'gzip': True,
              'header': ''},
             {'file': os.path.join(testdir, 'sample.ugm'),  # unzipped GAM
              'class': vg_pb2.Alignment,
              'size': 12,
              'nof_groups': 6,
              'gzip': False,
              'header': ''},
             {'file': os.path.join(testdir, 'sample_with_header.gam'),
              'class': vg_pb2.Alignment,
              'size': 2,
              'nof_groups': 1,
              'gzip': True,
              'header': b'GAM'}]
    tmpfile1 = os.path.join(testdir, '.tmpfile1')
    tmpfile2 = os.path.join(testdir, '.tmpfile2')

    @staticmethod
    def read_by_name(fpath, pb_cls, **kwargs):
        """Read protobuf messages in a file by passing the file NAME to
        `Stream` class using context manager.

        Args:
            fpath (string): path of the file to be read.
            pb_cls (protobuf.message.Message.__class__): class object of the
                protobuf message type encoded in the input stream.
            kwargs: All keyworded arguments will be passed to `Stream` class.
        """
        with stream.open(fpath, 'rb', **kwargs) as istream:
            for data in istream:
                if isinstance(data, istream.delimiter_class()):
                    yield data
                else:
                    msg = pb_cls()
                    msg.ParseFromString(data)
                    yield msg

    @staticmethod
    def read_by_file(fpath, pb_cls, **kwargs):
        """Read protobuf messages in a file by passing the file OBJECT to
        `Stream` class using context manager.

        NOTE: Does the same as `read_by_name`.

        Args:
            fpath (string): path of the file to be read.
            pb_cls (protobuf.message.Message.__class__): class object of the
                protobuf message type encoded in the input stream.
            kwargs: All keyworded arguments will be passed to `Stream` class.
        """
        mode = 'rb'
        if kwargs.get('gzip', True):
            ifs = gzip.open(fpath, mode)
        else:
            ifs = open(fpath, mode)
        with stream.open(fileobj=ifs, mode=mode, **kwargs) as istream:
            for data in istream:
                if isinstance(data, istream.delimiter_class()):
                    yield data
                else:
                    msg = pb_cls()
                    msg.ParseFromString(data)
                    yield msg
        ifs.close()

    @staticmethod
    def write_by_name(fpath, *objs_list, **kwargs):
        """Write protobuf messages into a file by passing the file NAME to
        `Stream` class using context manager.

        It writes objects in `objs_list` into groups of size `group_size`.

        Args:
            fpath (string): path of the file to be written.
            objs_list (*protobuf.message.Message): list of objects to be
                written.

        Keyword args:
            group_size (int): each group has this many objects.

        All other keyworded arguments will be passed to `Stream` class.
        """
        length = len(objs_list)
        group_size = kwargs.pop('group_size', length)
        with stream.open(fpath, 'wb', **kwargs) as ostream:
            cursor = 0
            while cursor < length:
                ostream.write(*objs_list[cursor:cursor+group_size])
                cursor += group_size

    @staticmethod
    def write_by_file(fpath, *objs_list, **kwargs):
        """Write protobuf messages into a file by passing the file OBJECT to
        `Stream` class using context manager.

        It writes objects in `objs_list` into groups of size `group_size` by
        setting buffer size to this size.

        NOTE: Does the same as `write_by_name` with this difference that it
        groups objects by setting buffer size.

        Args:
            fpath (string): path of the file to be written.
            objs_list (*protobuf.message.Message): list of objects to be
                written.

        Keyword args:
            group_size (int): each group has this many objects.

        All other keyworded arguments will be passed to `Stream` class.
        """
        group_size = kwargs.pop('group_size', len(objs_list))
        mode = 'wb'
        if kwargs.get('gzip', True):
            ofs = gzip.open(fpath, mode)
        else:
            ofs = open(fpath, mode)
        with stream.open(fileobj=ofs, mode=mode, buffer_size=group_size,
                         **kwargs) as ostream:
            ostream.write(*objs_list)
        ofs.close()

    def gzip_cmp(self, first, second):
        """Compare two gzipped files.

        Since the file name is included in the gzipped compressed files, they
        need to be decompressed first before comparing their contents.

        Args:
            first (string): path to the first file.
            second (string): path to the second file.
        """
        ungz_first = ''.join(os.path.splitext(first)[:-1]) + '.ugz'
        ungz_second = ''.join(os.path.splitext(second)[:-1]) + '.ugz'
        # Unzip the first file.
        with gzip.open(first, 'rb') as gfp, open(ungz_first, 'wb') as ufp:
            ufp.write(gfp.read())
        # Unzip the second file.
        with gzip.open(second, 'rb') as gfp, open(ungz_second, 'wb') as ufp:
            ufp.write(gfp.read())
        # Compare two unzipped files.
        result = filecmp.cmp(ungz_first, ungz_second)
        # Removing generated files.
        os.remove(ungz_first)
        os.remove(ungz_second)
        return result

    def cmp(self, first, second, **kwargs):
        """Compare two files whether gzip compressed or regular file.

        The stream can be gzipped or not which are specified by `gzipped`
        keyword argument.

        Args:
            first (string): path to the first file.
            second (string): path to the second file.
        """
        if kwargs.get('gzip', True):
            return self.gzip_cmp(first, second)
        return filecmp.cmp(first, second)

    def single_pass(self, sample, reader, ifile, writer, ofile, **kwargs):
        """Read the `ifile` with the given `reader` function, and write it back
        to `ofile` using the given `writer` function.

        Args:
            sample (dict): sample dictionary.
            reader (function): stream reader function.
            ifile (string): path to the input file.
            writer (function): stream writer function.
            ofile (string): path to the output file.

        Keyword args:
            nof_groups (int): number of groups of messages in `ifile`.

        All other keyworded arguments will be passed to `reader` and `writer`.
        """
        # Parse the sample file.
        nof_groups = kwargs.pop('nof_groups', 1)
        counted_groups = 1
        msgs = list()
        for elem in reader(ifile, sample['class'], **kwargs):
            if isinstance(elem, sample['class']):
                msgs.append(elem)
            else:
                self.assertTrue((kwargs.get('delimiter_cls', None) is None and
                                 elem is None) or
                                 isinstance(elem, kwargs['delimiter_cls']))
                counted_groups += 1
        # Check the number of retrieved messages.
        self.assertEqual(len(msgs), sample['size'])
        # Check the number of groups.
        self.assertEqual(counted_groups, nof_groups)
        # Rewrite them into a new file in two groups.
        writer(ofile, *msgs, **kwargs)

    def sync_integration_mid(self, sample, **kwargs):
        """Parse/write the sample file using two versions of read/write
        functions based on mid-level API and compare the output.

        Args:
            sample (dict): sample dictionary.

        All keyworded arguments will be passed to `Stream` class except for
        `group_delimiter` and `delimiter_cls` which are modified inside
        function.
        """
        # Do a single phase using read/write functions getting file name.
        tmpfile1 = TestStream.tmpfile1
        tmpfile2 = TestStream.tmpfile2
        kwargs['group_delimiter'] = True
        self.single_pass(sample, self.read_by_name, sample['file'],
                         self.write_by_name, tmpfile1,
                         nof_groups=sample['nof_groups'],
                         group_size=sample['size']//2, **kwargs)
        kwargs['delimiter_cls'] = int
        self.single_pass(sample, self.read_by_file, tmpfile1,
                         self.write_by_file, tmpfile2, nof_groups=2,
                         group_size=sample['size']//2, **kwargs)
        # Compare two generated files to be identical.
        self.assertTrue(self.cmp(tmpfile1, tmpfile2, **kwargs))

    def sync_integration_high(self, sample, **kwargs):
        """Parse/write the sample file using two versions of read/write
        functions based on high-level API and compare the output.

        Args:
            sample (dict): sample dictionary.

        All keyworded arguments will be passed to `Stream` class except for
        `group_delimiter` and `delimiter_cls` which are modified inside
        function.
        """
        tmpfile1 = TestStream.tmpfile1
        tmpfile2 = TestStream.tmpfile2
        kwargs['group_delimiter'] = True
        self.single_pass(sample, stream.parse, sample['file'], stream.dump,
                         tmpfile1, nof_groups=sample['nof_groups'],
                         buffer_size=sample['size']//2, **kwargs)
        kwargs['delimiter_cls'] = str
        self.single_pass(sample, self.read_by_file, tmpfile1,
                         self.write_by_file, tmpfile2, nof_groups=2,
                         group_size=sample['size']//2, **kwargs)
        # Compare two generated files to be identical.
        self.assertTrue(self.cmp(tmpfile1, tmpfile2, **kwargs))

    def sync_integration_low(self, **kwargs):
        """Write some known messages to a stream file and retrieve them by
        using low-level API without using context manager.
        """
        tmpfile1 = TestStream.tmpfile1

        expected_message = vg_pb2.Mapping()
        expected_message.position.node_id = 7599
        expected_message.position.offset = 472
        expected_message.position.is_reverse = True
        expected_message.position.name = "expected_message"
        edit = expected_message.edit.add()
        edit.from_length = 4
        edit.to_length = 5
        edit.sequence = "A"
        edit = expected_message.edit.add()
        edit.from_length = 45
        edit.to_length = 45
        edit.sequence = "CATCCGCTAGCTA"
        expected_message.rank = 3

        ostream = stream.Stream(tmpfile1, 'wb', **kwargs)
        ostream.write(expected_message, **kwargs)
        ostream.write(expected_message, **kwargs)
        ostream.close()

        self.assertEqual(expected_message.position.node_id, 7599)
        self.assertEqual(expected_message.position.offset, 472)
        self.assertEqual(expected_message.position.is_reverse, True)
        self.assertEqual(expected_message.position.name, "expected_message")
        self.assertEqual(expected_message.edit[0].from_length, 4)
        self.assertEqual(expected_message.edit[0].to_length, 5)
        self.assertEqual(expected_message.edit[0].sequence, "A")
        self.assertEqual(expected_message.edit[1].from_length, 45)
        self.assertEqual(expected_message.edit[1].to_length, 45)
        self.assertEqual(expected_message.edit[1].sequence, "CATCCGCTAGCTA")
        self.assertEqual(expected_message.rank, 3)

        istream = stream.Stream(tmpfile1, 'rb', **kwargs)
        for data in istream:
            message = vg_pb2.Mapping()
            message.ParseFromString(data)
            self.assertEqual(message.position.node_id,
                             expected_message.position.node_id)
            self.assertEqual(message.position.offset,
                             expected_message.position.offset)
            self.assertEqual(message.position.is_reverse,
                             expected_message.position.is_reverse)
            self.assertEqual(message.position.name,
                             expected_message.position.name)
            self.assertEqual(len(message.edit),
                             len(expected_message.edit))
            self.assertEqual(message.edit[0].from_length,
                             expected_message.edit[0].from_length)
            self.assertEqual(message.edit[0].to_length,
                             expected_message.edit[0].to_length)
            self.assertEqual(message.edit[0].sequence,
                             expected_message.edit[0].sequence)
            self.assertEqual(message.edit[1].from_length,
                             expected_message.edit[1].from_length)
            self.assertEqual(message.edit[1].to_length,
                             expected_message.edit[1].to_length)
            self.assertEqual(message.edit[1].sequence,
                             expected_message.edit[1].sequence)
            self.assertEqual(message.rank, expected_message.rank)
        istream.close()

    def sync_integration_byte(self, **kwargs):
        """Write some bytes to a stream instead of protobuf messages and
        retrieve them.
        """
        tmpfile1 = TestStream.tmpfile1
        objects = list()

        objects.append(b'hello')
        expected_message = vg_pb2.Mapping()
        expected_message.position.node_id = 7599
        expected_message.position.offset = 472
        expected_message.position.is_reverse = True
        expected_message.position.name = "expected_message"
        edit = expected_message.edit.add()
        edit.from_length = 4
        edit.to_length = 5
        edit.sequence = "A"
        edit = expected_message.edit.add()
        edit.from_length = 45
        edit.to_length = 45
        edit.sequence = "CATCCGCTAGCTA"
        expected_message.rank = 3
        objects.append(expected_message.SerializeToString())
        objects.append(b'world!')

        ost = stream.open(tmpfile1, mode='wb', serialize=lambda x:x, **kwargs)
        ost.write(*objects)
        ost.close()

        self.assertEqual(objects[0], b'hello')
        self.assertEqual(objects[2], b'world!')
        self.assertEqual(expected_message.position.node_id, 7599)
        self.assertEqual(expected_message.position.offset, 472)
        self.assertEqual(expected_message.position.is_reverse, True)
        self.assertEqual(expected_message.position.name, "expected_message")
        self.assertEqual(expected_message.edit[0].from_length, 4)
        self.assertEqual(expected_message.edit[0].to_length, 5)
        self.assertEqual(expected_message.edit[0].sequence, "A")
        self.assertEqual(expected_message.edit[1].from_length, 45)
        self.assertEqual(expected_message.edit[1].to_length, 45)
        self.assertEqual(expected_message.edit[1].sequence, "CATCCGCTAGCTA")
        self.assertEqual(expected_message.rank, 3)

        istream = stream.open(tmpfile1, 'rb', **kwargs)
        data = next(istream)
        self.assertEqual(data, objects[0])
        data = next(istream)
        message = vg_pb2.Mapping()
        message.ParseFromString(data)
        self.assertEqual(message.position.node_id,
                         expected_message.position.node_id)
        self.assertEqual(message.position.offset,
                         expected_message.position.offset)
        self.assertEqual(message.position.is_reverse,
                         expected_message.position.is_reverse)
        self.assertEqual(message.position.name,
                         expected_message.position.name)
        self.assertEqual(len(message.edit),
                         len(expected_message.edit))
        self.assertEqual(message.edit[0].from_length,
                         expected_message.edit[0].from_length)
        self.assertEqual(message.edit[0].to_length,
                         expected_message.edit[0].to_length)
        self.assertEqual(message.edit[0].sequence,
                         expected_message.edit[0].sequence)
        self.assertEqual(message.edit[1].from_length,
                         expected_message.edit[1].from_length)
        self.assertEqual(message.edit[1].to_length,
                         expected_message.edit[1].to_length)
        self.assertEqual(message.edit[1].sequence,
                         expected_message.edit[1].sequence)
        self.assertEqual(message.rank, expected_message.rank)
        data = next(istream)
        self.assertEqual(data, objects[2])
        istream.close()

    def test_sync_integration(self):
        """Integration test for sync parsing/writing."""
        self.sync_integration_low()
        self.sync_integration_byte()
        self.sync_integration_byte(header=b'BYTES')
        for sample in TestStream.files:
            self.sync_integration_mid(sample, gzip=sample['gzip'],
                                      header=sample['header'])
            self.sync_integration_high(sample, gzip=sample['gzip'],
                                       header=sample['header'])

    async def async_integration(self):
        """Write some known messages to an async stream and retrieve them back.
        """
        a_sock, b_sock = socket.socketpair()
        a_reader, a_writer = await asyncio.open_connection(sock=a_sock)
        b_reader, b_writer = await asyncio.open_connection(sock=b_sock)

        msgs = list()
        msgs.append(vg_pb2.Position())
        msgs[-1].node_id = 8584
        msgs[-1].offset = 66
        msgs.append(vg_pb2.Position())
        msgs[-1].node_id = 73649
        msgs[-1].offset = 12092

        stream.dump(a_writer, msgs[0], header=b'Pos')
        stream.dump(a_writer, msgs[1])

        self.assertEqual(msgs[0].node_id, 8584)
        self.assertEqual(msgs[0].offset, 66)
        self.assertEqual(msgs[1].node_id, 73649)
        self.assertEqual(msgs[1].offset, 12092)

        async def assertion(nof_groups):
            messages_asserted = 0
            counted_groups = 1
            async for message in stream.async_parse(b_reader, vg_pb2.Position,
                                                    group_delimiter=True,
                                                    header=b'Pos'):
                if not isinstance(message, vg_pb2.Position):
                    counted_groups += 1
                    continue
                expected_message = msgs.pop(0)
                self.assertEqual(message.node_id, expected_message.node_id)
                self.assertEqual(message.offset, expected_message.offset)
                messages_asserted += 1
                if messages_asserted == 2:
                    break
            self.assertEqual(counted_groups, nof_groups)

        await asyncio.wait_for(assertion(2), 1.0)

    def test_async_integration(self):
        """Integration test for async parsing/writing."""
        if sys.version_info >= (3, 7):
            asyncio.run(self.async_integration())
        else:
            # Emulate asyncio.run() on older versions
            # https://stackoverflow.com/a/55595696/357257
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                loop.run_until_complete(self.async_integration())
            finally:
                loop.close()
                asyncio.set_event_loop(None)

    def tearDown(self):
        """Tear down function."""
        # Removing temporary files.
        if os.path.exists(TestStream.tmpfile1):
            os.remove(TestStream.tmpfile1)
        if os.path.exists(TestStream.tmpfile2):
            os.remove(TestStream.tmpfile2)
