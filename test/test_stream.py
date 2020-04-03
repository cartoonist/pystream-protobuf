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
import unittest
import filecmp

from .context import stream
from . import vg_pb2


class TestStream(unittest.TestCase):
    testdir = os.path.dirname(os.path.realpath(__file__))
    files = [{'file': os.path.join(testdir, 'sample.gam'),
              'class': vg_pb2.Alignment,
              'size': 12,
              'nof_groups': 6,
              'gzip': True},
             {'file': os.path.join(testdir, 'sample.ugm'),  # unzipped GAM
              'class': vg_pb2.Alignment,
              'size': 12,
              'nof_groups': 6,
              'gzip': False}]
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

    def sync_integration_low(self, sample, **kwargs):
        """Parse/write the sample file using two versions of read/write
        functions based on low-level API and compare the output.
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

    def test_sync_integration(self, **kwargs):
        """Integration test for sync parsing/writing."""
        for sample in TestStream.files:
            self.sync_integration_low(sample, gzip=sample['gzip'])
            self.sync_integration_high(sample, gzip=sample['gzip'])

    def tearDown(self):
        """Tear down function."""
        # Removing temporary files.
        if os.path.exists(TestStream.tmpfile1):
            os.remove(TestStream.tmpfile1)
        if os.path.exists(TestStream.tmpfile2):
            os.remove(TestStream.tmpfile2)
