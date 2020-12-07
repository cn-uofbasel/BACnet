#!/usr/bin/env python3

# dfs_mockup.py

# distributed file system mockup (=mapped to a UNIX directory)
# Dec 2020 <christian.tschudin@unibas.ch>

import os

class DFS_MOCKUP: # decentralized file system, UNIX-based

    # the commands are aligned with FTP's commands (rfc 959)
    # also compare with API of Hyperdrive:
    #   https://github.com/hypercore-protocol/hyperdrive

    # getwd()
    # chdir()
    # store()     whole file
    # retrieve()  whole file
    # rename()
    # move()      ?
    # unlink()
    # mkdir()
    # rmdir()
    # listdir()
    # exists()
    # isfile()
    # isdir()

    '''
File structure for the UNIX mockup implementation:

/Users/tschudin/bacnet/0xAALLIICCEE/dfs/0xFFSS11/
                                           `-- 0x12345.pcap # content
                                           `-- 0x87654.pcap # meta
                                   /0xMYLOG.pcap
                                   /...
    '''

    def __init__(self, pk, unix_dir_name=None):
        self.pk = pk
        self.dname = pk.hex() + '.dfs' if unix_dir_name==None else unix_dir_name
        if not os.path.isdir(self.dname):
            os.mkdir(self.dname)
        self.path = [] # store path as list of names

    def _path2unix(self, path):
        if path == None:
            path = self.path
        return self.dname + os.sep + os.sep.join(path)

    def getID(self):
        return self.pk

    def getwd(self): # PWD - print working directory
        return self.path

    def chdir(self, path): # CWD - change working directory
        if path[0] in ['.', '..']:
            path = self.path + path
        new = []
        for n in path:
            if n == '.':
                continue
            if n == '..':
                if len(new) == 0:
                    raise Exception("cannot go beyond root")
                new = new[:-1]
            else:
                new.append(n)
        self.path = new

    def store(self, path, blob): # STOR - create/replace a new file
        with open(self._path2unix(path), 'wb') as f:
            f.write(blob)

    def retrieve(self, path): # RETR - retrieve a file
        with open(self._path2unix(path), 'rb') as f:
            return f.read()

    def unlink(self, path): # DELE - remove a file
        os.unlink(self._path2unix(path))

    def mkdir(self, path): # MKD - make a directory
        os.mkdir(self._path2unix(path))

    def rmdir(self, path): # RMD - remove a directory
        os.rmdir(self._path2unix(path))

    def listdir(self, path=None): # LIST - list dir, returns seq of tuples
        lst = []
        for fn in os.listdir(self._path2unix(path)):
            lst.append( (fn,os.stat(self._path2unix(path)+os.sep+fn)) )
        return lst

    def exists(self, path):
        return os.path.exists(self._path2unix(path))

    def isdir(self, path):
        return os.path.isdir(self._path2unix(path))

    def isfile(self, path):
        return os.path.isfile(self._path2unix(path))

    pass


# ---------------------------------------------------------------------------

def my_ls(dfs):
    import time

    print(f"Content of drive 0x{dfs.getID().hex()}:/{'/'.join(dfs.getwd())}")
    for f in sorted(dfs.listdir(),key=lambda e:e[0]):
        if dfs.isdir(dfs.getwd() + [f[0]]):
            print(f"          {time.ctime(f[1].st_ctime)}  {f[0]}/")
        else:
            print("%6d  " % f[1].st_size + \
                  f"  {time.ctime(f[1].st_ctime)}  {f[0]}")

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    import sys

    # usage: ./dfs_mockup.py 11223344   # or any other hex string

    pk = bytes.fromhex(sys.argv[1])
    dfs = DFS_MOCKUP(pk)

    # fill the demo file system with content
    dfs.store(['.', 'abc.txt'], "hello world\n".encode('utf8'))
    dfs.store(['.', 'xyz.txt'], "good bye\n".encode('utf8'))
    sub = ['.', 'sub']
    dfs.mkdir(sub)
    dfs.store(sub + ['some.txt'], "some text\n".encode('utf8'))
    dfs.mkdir(sub + ['subsub'])

    # list the content
    my_ls(dfs)
    print()
    dfs.chdir(['.', 'sub']) # test ['.', 'sub', 'subsub', '..', '..', '..'])
    my_ls(dfs)

# eof
