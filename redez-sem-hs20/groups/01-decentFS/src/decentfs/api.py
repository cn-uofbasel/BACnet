import bacnet.crypto
import bacnet.feed
import bacnet.pcap
import cbor2
import logging
import os
import pathlib
import time
from ast import literal_eval
from typing import BinaryIO, Union, Optional
from hashlib import blake2b
from hmac import compare_digest


class DecentFsException(Exception):
    """DecentFs generic exception

    err: error messange
    """

    def __init__(self, err: str):
        self.err = err


class DecentFsFileExistsError(DecentFsException):
    """DecentFs prevent overwriting a path"""


class DecentFsFileNotFound(DecentFsException):
    """DecentFs path not found"""


class DecentFsIsADirectoryError(DecentFsException):
    """DecentFs directory operation on a file"""


class DecentFsNotADirectoryError(DecentFsException):
    """DecentFs file operation on a directory"""


class DecentFs:
    VERSION = '0.0.0-dev'
    _DEFAULT_BLOB = 'blob.pcap'
    _DEFAULT_META = 'meta.pcap'
    _DEFAULT_STORAGE = './.decentfs'
    BUF_SIZE = 65536  # 64KB

    keyfile = None
    version = ''
    writeable: bool = True
    storage = ''
    stream = None
    blobfeed = None
    metafeed = None


    def __init__(self, keyfile: Union[str, bytes, os.PathLike], storage: Optional[Union[str, bytes, os.PathLike]]=None, opt: str='', createNew=False) -> None:
        """Create or open file system

        :param keyfile: file holding the key
        :param storage: path to DecentFs
        :param opt: file system options
        """

        # load keyfile
        assert os.path.isfile(keyfile) and os.access(keyfile, os.R_OK), \
                "Keyfile {} not accessible".format(keyfile)
        logging.info('Using keyfile %s', keyfile)
        self.keyfile = keyfile
        fid, signer, digestmod = self._load_keyfile()

        # create and define storage
        if createNew:
            logging.info('Creating new storage %s', storage)
            if storage is None:
                storage = self._DEFAULT_STORAGE
            self.version = self.VERSION
            os.makedirs(storage)
        logging.info('Using storage %s', storage)
        self.storage = storage
        assert os.path.isdir(storage) and os.access(storage, os.R_OK), \
                "Storage {} not accessible".format(storage)

        # load blobfeed
        blobpcap = os.path.join(self.storage, self._DEFAULT_BLOB)
        logging.info('Using blobfeed %s', blobpcap)
        self.blobfeed = bacnet.feed.FEED(blobpcap, fid, signer, createNew, digestmod=digestmod)
        assert os.path.isfile(blobpcap) and os.access(blobpcap, os.R_OK), \
                "Blobfeed {} not accessible".format(blobpcap)

        # load metafeed
        metapcap = os.path.join(self.storage, self._DEFAULT_META)
        logging.info('Using metafeed %s', metapcap)
        self.metafeed = bacnet.feed.FEED(metapcap, fid, signer, createNew, digestmod=digestmod)
        assert os.path.isfile(metapcap) and os.access(metapcap, os.R_OK), \
                "Metafeed {} not accessible".format(metapcap)

        # read-only mode
        logging.debug('Reading options: %s', opt)
        if 'ro' in opt:
            logging.info('Operating in read-only mode')
            self.writeable = False
        elif not (os.access(storage, os.W_OK) and os.access(blobpcap, os.W_OK) and os.access(metapcap, os.W_OK)):
            logging.warn('Write permission not granted on all files, forcing read-only mode')
            self.writeable = False

        # initializing file system
        if createNew:
            assert self.writeable, "Read-only file system"
            logging.info('Initializing new feeds')
            self.metafeed.write(cbor2.dumps(["VERSION", self.version]))
            self.blobfeed.write(cbor2.dumps(["VERSION", self.version]))

        # load and check file system
        logging.info('Loading feeds')
        if self._fsck() > 0:
            raise DecentFsException('Integrity check failed')


    def __del__(self) -> None:
        """Close gracefully and cleanup"""

        logging.debug('Shutdown DecentFs')


    def _load_keyfile(self) -> list:
        """Handle multiple key flavors"""

        with open(self.keyfile, 'r') as f:
            key = literal_eval(f.read())
        if key['type'] == 'ed25519':
            logging.debug('Using ED25519 key flavor')
            fid = bytes.fromhex(key['public'])
            signer = bacnet.crypto.ED25519(bytes.fromhex(key['private']))
            digestmod = 'sha256'
        elif key['type'] in ['hmac_sha256', 'hmac_sha1', 'hmac_md5']:
            logging.debug('Using hmac key flavor')
            fid = bytes.fromhex(key['feed_id'])
            digestmod = key['type'][5:]
            signer = bacnet.crypto.HMAC(digestmod, bytes.fromhex(key['private']))
        else:
            Exception('Unknown keytype')
        return fid, signer, digestmod


    def _feedck(self) -> int:
        """Quick integrity check

        Check integrity of feeds.

        :returns: 0 or amount of failures
        """

        logging.debug('Checking feed version %s', self._version())
        err = 0
        for f in [self.blobfeed, self.metafeed]:
            f.seq = 0
            f.hprev = None
            for e in f:
                if not f.is_valid_extension(e):
                    logging.warn('Error found at %i', f.seq)
                    err += 1
                if not e.chk_content:
                    logging.warn('Content check failed at %i', f.seq)
                    err += 1
                f.seq += 1
                f.hprev = e.get_ref()
        logging.debug('Length of feeds: blob: %i meta %i', len(self.blobfeed), len(self.metafeed))
        return err


    def _fsck(self) -> int:
        """Quick file system check

        :return: 0 or amount of failures
        """

        allblocks = set()
        allblobs = []
        blob = self.blobfeed
        meta = self.metafeed
        timer = time.process_time_ns()
        err = self._feedck()
        seq = 0
        for entry in meta:
            # skip special block
            if seq == 0:
                seq += 1
                continue
            _, _, _, _, blocks = cbor2.loads(entry.content())
            allblocks.update(blocks)
            seq += 1
        logging.debug('Found %i unique referenced blocks in %i files', len(allblocks), seq)

        for entry in blob:
            blockid, _ = cbor2.loads(entry.content())
            if blockid == "VERSION":
                # skip special block
                continue
            allblobs.append(blockid)

        allblobset = set(allblobs)
        if len(allblobs) != len(allblobset):
            logging.warn('Duplicated block found')
            err += 1
        if allblocks != allblobset:
            logging.warn('Block reference error: %s', allblocks.symmetric_difference(allblobset))
            err += 1
        timer = time.process_time_ns() - timer
        logging.debug('Finish checking within %i ms', timer/1000000)
        return err


    def _version(self) -> str:
        """Fetches file system version

        :return: version string
        """

        version = ''
        for feed in [self.blobfeed, self.metafeed]:
            entry = next(iter(feed))
            ver, num = cbor2.loads(entry.content())
            if ver == "VERSION":
                logging.debug('Found version %s', num)
                version = num
            else:
                logging.error('Expecting VERSION, but found %s', version)
        return version


    def dump(self) -> None:
        """Dump pcap content"""

        logging.debug('Invoke pcap dump')
        bacnet.pcap.dump(os.path.join(self.storage, self._DEFAULT_META))


    def createWriteStream(self, path: Union[str, bytes, os.PathLike]) -> BinaryIO:
        """Create write stream

        Opens a stream to read the content to write from.

        :returns: open readable binary stream
        """

        assert self.writeable, "Read-only file system"

        self.stream = open(path, 'rb')
        return self.stream


    def writeFile(self, path: Union[os.PathLike], buf: Optional[BinaryIO]=None, flags: str='') -> None:
        """Write to DecentFs

        :param path: input path
        :param buf: input stream
        :param flags: file flags
        """

        assert self.writeable, "Read-only file system"
        assert pathlib.PurePosixPath(path).is_absolute(), "{} is not an absolute path".format(path)

        logging.info('Append file %s', path)
        if buf is None:
            self.stream = self.createWriteStream(path)
            buf = self.stream
        slices = []
        size = 0
        writeops = 0
        timer = time.process_time_ns()
        while (block := buf.read(self.BUF_SIZE)):
            blockid = blake2b(block).digest()
            slices.append(blockid)
            size += len(block)
            if not self._findDuplicate(blockid):
                writeops += 1
                logging.info('Writing new block %s', blockid.hex())
                self.blobfeed.write(cbor2.dumps([blockid, block]))
        self.metafeed.write(cbor2.dumps([path.__str__(), flags, time.time_ns(), size, slices]))
        logging.info('Append metadata for %s', path)
        logging.info('%i of %i blocks deduplicated', len(slices) - writeops, len(slices))
        logging.debug('containing flags: %s, bytes: %i and %i slices: %s', flags, size, len(slices), ','.join(map(bytes.hex, slices)))
        timer = time.process_time_ns() - timer
        logging.debug('Finish writing within %i ms', timer/1000000)


    def _findDuplicate(self, blockid: str) -> bool:
        """Finds duplicates of blocks

        returns: True if block is already stored
        """

        seq = 0
        timer = time.process_time_ns()
        for entry in self.metafeed:
            # skip special block
            if seq == 0:
                seq += 1
                continue
            _, _, _, _, blocks = cbor2.loads(entry.content())
            for b in blocks:
                if compare_digest(b, blockid):
                    logging.debug('Deduplicating block %s', blockid.hex())
                    timer = time.process_time_ns() - timer
                    logging.debug('Scanned blocks for duplicates within %i ms', timer/1000000)
                    return True
            seq += 1
        return False


    def _find(self, path: Union[str, os.PathLike]) -> list:
        """Raw meta data of a single file

        :returns: raw metafeed entry
        :throws: DecentFsFileNotFound if not found
        """

        logging.debug('Searching for %s', path)
        seq = 0
        timer = time.process_time_ns()
        found = None
        for entry in self.metafeed:
            # skip special block
            if seq == 0:
                seq += 1
                continue
            findpath, flags, _, _, _ = cbor2.loads(entry.content())
            logging.debug('Found %s with flags %s', findpath, flags)
            if findpath == path.__str__():
                timer = time.process_time_ns() - timer
                logging.debug('Found path at %i with flags %s within %i ms', seq, flags, timer/1000000)
                if flags == 'R':
                    found = None
                else:
                    found = cbor2.loads(entry.content())
            seq += 1
        if found is None:
            raise DecentFsFileNotFound('File {} not found'.format(path.__str__()))
        return found


    def _glob(self, glob: Union[str, os.PathLike]) -> list:
        """List files matich a glob pattern

        :returns: list of matching paths
        :throws: DecentFsFileNotFound if not found
        """

        logging.debug('Searching for %s', glob)
        seq = 0
        timer = time.process_time_ns()
        matchs = set()
        for entry in self.metafeed:
            # skip special block
            if seq == 0:
                seq += 1
                continue
            findpath, flags, _, _, _ = cbor2.loads(entry.content())
            logging.debug('Found %s with flags %s', findpath, flags)
            if pathlib.PurePosixPath(findpath).match(glob.__str__()):
                timer = time.process_time_ns() - timer
                logging.debug('Got a match at %i with flags %s within %i ms', seq, flags, timer/1000000)
                if flags == 'R':
                    matchs.remove(findpath)
                else:
                    matchs.add(findpath)
            seq += 1
        if len(matchs) == 0:
            raise DecentFsFileNotFound('File {} not found'.format(glob.__str__()))
        return matchs


    def stat(self, path: Union[str, os.PathLike]) -> dict:
        """Stat of a file

        Return structured, readable metadata of a DecentFs entry

        The entry contains:
        path: full path of the file
        flags: flags of the file (can be empty)
        timestamp: timestamp of the entry in nanoseconds
        bytes: size of the whole file in bytes
        blocks: comma separated list of block ids

        :param: path: full path of the file
        :throws: DecentFsFileNotFound if not found
        """

        findpath, flags, timestamp, size, blocks = self._find(path)
        stat: dict = {
            'path': findpath,
            'flags': flags,
            'timestamp': timestamp,
            'bytes': size,
            'blocks': ','.join(map(bytes.hex, blocks)),
        }
        return stat


    def createReadStream(self, path: Union[str, bytes, os.PathLike]) -> BinaryIO:
        """Create read stream

        Opens a stream to write the read content to.

        :param path: path for output
        :returns: Open writeable binary stream
        """
        self.stream = open(path, 'wb')
        return self.stream


    def readFile(self, path: Union[str, os.PathLike], buf: Optional[BinaryIO]=None) -> None:
        """Read file from DecentFs

        :param path: path of file to read from
        :param buf: output stream
        :throws: DecentFsFileNotFound if not found
        """

        logging.info('Read file %s', path)
        if buf is None:
            self.stream = self.createReadStream(path)
            buf = self.stream
        findpath, flags, timestamp, size, blocks = self._find(path)
        logging.debug('containing flags: %s, bytes: %i and %i slices: %s', flags, size, len(blocks), ','.join(map(bytes.hex, blocks)))
        readops = 0
        blobcursor = iter(self.blobfeed)
        timer = time.process_time_ns()
        for block in blocks:
            for _ in range(len(self.blobfeed)):
                try:
                    # try to continue from last found blob (sequential reads)
                    entry = next(blobcursor)
                except StopIteration:
                    logging.debug('Reset cursor')
                    blobcursor = iter(self.blobfeed)
                blockid, _ = cbor2.loads(entry.content())
                if blockid == "VERSION":
                    # skip special block
                    continue
                if compare_digest(blockid, block):
                    blockid, blob = cbor2.loads(entry.content())
                    readops += 1
                    logging.debug('Found block %i of %i: %s', readops, len(blocks), blockid.hex())
                    buf.write(blob)
                    break
        timer = time.process_time_ns() - timer
        logging.debug('Finish reading within %i ms', timer/1000000)
        assert readops == len(blocks), 'Found %i of %i blocks, but they should be equal'.format(readops, len(blocks))


    def copy(self, source: Union[str, os.PathLike], target: Union[str, os.PathLike]) -> None:
        """Copy path in DecentFs

        TODO: recursively scan for other paths in the directory's path

        :param source: path to copy from
        :param target: path to copy to
        :throws: DecentFsFileNotFound if not found
        """

        assert self.writeable, "Read-only file system"
        assert pathlib.PurePosixPath(target).is_absolute(), "{} is not an absolute path".format(target)

        findpath, flags, _, size, blocks = self._find(source)
        self.metafeed.write(cbor2.dumps([target.__str__(), flags, time.time_ns(), size, blocks]))
        logging.debug('Finish copying %s to %s', findpath, target)


    def unlink(self, path: Union[str, os.PathLike]) -> None:
        """Flag a path in DecentFs

        :param path: path to unlink
        :throws: DecentFsFileNotFound if not found
        :throws: DecentFsIsADirectoryError if path has directory flag
        """

        assert self.writeable, "Read-only file system"
        assert pathlib.PurePosixPath(path).is_absolute(), "{} is not an absolute path".format(path)

        findpath, flags, _, _, _ = self._find(path)
        if 'D' in flags:
            raise DecentFsIsADirectoryError('Path {} is a directory'.format(findpath))
        self.metafeed.write(cbor2.dumps([path.__str__(), 'R', time.time_ns(), 0, []]))
        logging.debug('Finish unlinking %s', findpath)


    def move(self, source: Union[str, os.PathLike], target: Union[str, os.PathLike]) -> None:
        """Move file in DecentFs

        TODO: recursively scan for other paths in the directory's path

        :param source: path to move
        :param target: new path
        :throws: DecentFsFileNotFound if not found
        """

        assert self.writeable, "Read-only file system"
        assert pathlib.PurePosixPath(target).is_absolute(), "{} is not an absolute path".format(target)

        self.copy(source, target)
        _, flags, _, _, _ = self._find(source)
        if 'D' in flags:
            self.rmdir(source)
        else:
            self.unlink(source)
        logging.debug('Finish moving %s to %s', source, target)


    def mkdir(self, path: Union[str, os.PathLike]) -> None:
        """Create a path in DecentFs flagged as directory

        :param path: path to directory
        :throws: DecentFsFileExistsError if path already exists
        """

        assert self.writeable, "Read-only file system"
        assert pathlib.PurePosixPath(path).is_absolute(), "{} is not an absolute path".format(path)

        try:
            findpath, flags, _, _, _ = self._find(path)
        except DecentFsFileNotFound:
            self.metafeed.write(cbor2.dumps([path.__str__(), 'D', time.time_ns(), 0, []]))
            logging.debug('Finish mkdir %s', path)
        else:
            raise DecentFsFileExistsError('File {} already exists with flags: {}'.format(findpath.__str__(), flags))


    def rmdir(self, path: Union[str, os.PathLike]) -> None:
        """Flag a path in DecentFs

        TODO: recursively scan for other paths in the directory's path

        :param path: path to unlink
        :throws: DecentFsFileNotFound if not found
        :throws: DecentFsNotADirectoryError if not a directory path
        """

        assert self.writeable, "Read-only file system"
        assert pathlib.PurePosixPath(path).is_absolute(), "{} is not an absolute path".format(path)

        findpath, flags, _, _, _ = self._find(path)
        if 'D' not in flags:
            raise DecentFsNotADirectoryError('Path {} is not a directory'.format(findpath))
        self.metafeed.write(cbor2.dumps([path.__str__(), 'R', time.time_ns(), 0, []]))
        logging.debug('Finish removing directory %s', findpath)


    def ls(self, path: Union[str, os.PathLike], details: bool=False) -> list:
        """List files in path

        :param path: a path in DecentFS
        :throws: DecentFsFileNotFound if not found
        """

        assert pathlib.PurePosixPath(path).is_absolute(), "{} is not an absolute path".format(path)

        return self._glob(path)
