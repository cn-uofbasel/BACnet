# DecentFS

## API

This draft is inspired by Hyperdrive.

### `VERSION`

API version
Might be used to check compatibility with the filesystem version

### `def __init__(self, myDecentFs, key, opt="")`
open existing filesystem

option: read-only

### `def __init__(self, key, opt="")`
create new filesystem

option: read-only

### `def __del__(self)`
close gracefully and cleanup

### `def open(name, opt="")`
open and return file descriptor

option: read-only

### `def read(fd, buffer, offset, length, position)`
read from file descriptor and return content

### `def write(fd, buffer, offset, length, position)`
write to file descriptor

### `def close(fd)`
close file descriptor

### `def symlink(target, name)`
create symlink

### `def unlink(name)`
remove file or symlink

### `def mkdir(name, opt="")`
create directory

option: recursively

### `def rmdir(name, opt="")`
remove directory

option: recursively

### `def readdir(name, opt="")`
list files in directory

option: recursively

### `def stat(name, opt="")`
get various information about a file or directory
