# README.md

## Decent FS -- Mockup

This defines a file system API and shows how to implement it using
a UNIX environemnt.

The goal of this project is to implement the same API and behavior
using two append-only logs: one for the file content, the other for
the file names (including directories) and other metadata.

API demo (of the UNIX mockup version):

```
% rm -rf 112233.dfs
% ./dfs_mockup.py 112233
Content of drive 0x112233:/
    12    Mon Dec  7 09:41:03 2020  abc.txt
          Mon Dec  7 09:41:03 2020  sub/
     9    Mon Dec  7 09:41:03 2020  xyz.txt

Content of drive 0x112233:/sub
    10    Mon Dec  7 09:41:03 2020  some.txt
          Mon Dec  7 09:41:03 2020  subsub/
```
