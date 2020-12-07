# README.md (some demo code for a quick start)

## Decent FS - Mockup

The Python script `dfs_mockup.py` defines a file system API and shows
how to implement it using a UNIX environemnt.

The goal of the project `01-decentFS` is to implement the same API and
behavior using two append-only logs: one for the file content, the
other for the file names (including directories) and other metadata.

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


## Suggested directory structure for storing the two logs of a DFS drive

```
/Users/tschudin/bacnet/0xAALLIICCEE/dfs/0xDDFFSS11/
                                           `-- 0x123456.pcap # content
                                           `-- 0x876543.pcap # meta
                                           `-- keys.json     # secret keys if owner
                                   /0xMYLOG.pcap
                                   /...

/Users/tschudin/bacnet/0xBOBBOBBOBB/dfs/0xDDFFSS45/
                                           `-- ...
                                 
```

For a new drive (that you own), create two keypairs and respective
logs.  The first message in each log should contain information about
the use of the log for the DFS drive (is it a DFS content or a meta
log?). For debugging purposes, store the secret keys of the two logs in
a file `keys.json' in the same drive directory.


## Copy of the BACnet1 library for append-only log functionality

see the local directory `bacnet1` in this folder, and the
[instructions](https://github.com/cn-uofbasel/BACnet/tree/master/src/demo)
in the old BACnet1 directory for:
- creating a keypair
- creating a feed (= append-only log)
- appending to it.

---
