# pyStream
Python implementation of [stream library](https://github.com/vgteam/stream)
parsing all files encoded by stream and writing protobuf message instances into
the file by the same encoding.

Here's a sample code using the Stream class to read from a file containing a
set of alignments. It yields the protobuf objects stored in the file:

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

And here is a sample code for writing multiple protobuf objects into a file:

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
