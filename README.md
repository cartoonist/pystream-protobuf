# pyStream
Python implementation of [stream library](https://github.com/vgteam/stream)
for parsing all files encoded by stream and writing protobuf instances into the
file by using the same encoding.

You can install pyStream using `pip`:

    pip install pystream-protobuf

## Examples
Here's a sample code using the Stream class to read a file (so-called GAM file)
containing a set of [VG](https://github.com/vgteam/vg)'s Alignment objects
(defined [here](https://github.com/vgteam/vg/blob/master/src/vg.proto)). It
yields the protobuf objects stored in the file:

```python
alns_list = []
with Stream.open("test.gam", "rb") as stream:
    for aln_data in stream:
        aln = Alignment()
        aln.ParseFromString(aln_data)
        alns_list.append(aln)
```

Or

```python
alns_list = []
stream = Stream.open("test.gam", "rb")
for aln_data in stream:
    aln = Alignment()
    aln.ParseFromString(aln_data)
    alns_list.append(aln)
stream.close()
```

And here is a sample code for writing multiple protobuf objects into a file
(here a GAM file):

```python
with Stream.open("test.gam", "wb") as stream:
    stream.write(*objects_list)
    stream.write(*another_objects_list)
```

Or

```python
stream = Stream.open("test.gam", "wb")
stream.write(*objects_list)
stream.write(*another_objects_list)
stream.close()
```
