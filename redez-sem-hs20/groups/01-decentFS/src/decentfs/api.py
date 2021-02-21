import bacnet.crypto
import bacnet.feed
import bacnet.pcap
import os
from hashlib import blake2b
import cbor2
from hmac import compare_digest
import logging
import time

class DecentFs:
    VERSION = '0.0.0-dev'
    _DEFAULT_BLOB = 'blob.pcap'
    _DEFAULT_META = 'meta.pcap'
    _DEFAULT_STORAGE = './.decentfs'
    BUF_SIZE = 65536  # 64KB

    discoveryKey = ''
    keyfile = None
    peers = ''
    version = ''
    writable = True
    storage = ''
    stream = None
    blobfeed = None
    metafeed = None


    """ create or open filesystem """
    def __init__(self, keyfile, storage=None, opt=''):
        assert os.path.isfile(keyfile) and os.access(keyfile, os.R_OK), \
                "Keyfile {} not accessible".format(keyfile)
        logging.info('Using keyfile %s', keyfile)
        self.keyfile = keyfile
        createNew = False
        if storage is None:
            logging.info('Creating new storage %s', storage)
            createNew = True
            storage = self._DEFAULT_STORAGE
            self.version = self.VERSION
            os.makedirs(storage)
        assert os.path.isdir(storage) and os.access(storage, os.R_OK), \
                "Storage {} not accessible".format(storage)
        logging.info('Using storage %s', storage)
        self.storage = storage

        logging.info('Loading keyfile %s', keyfile)
        fid, signer, digestmod = self._load_keyfile()
        logging.info('Using blobfeed %s', self._DEFAULT_BLOB)
        blobpcap = os.path.join(self.storage, self._DEFAULT_BLOB)
        self.blobfeed = bacnet.feed.FEED(blobpcap, fid, signer, createNew, digestmod=digestmod)
        logging.info('Using metafeed %s', self._DEFAULT_META)
        metapcap = os.path.join(self.storage, self._DEFAULT_META)
        self.metafeed = bacnet.feed.FEED(metapcap, fid, signer, createNew, digestmod=digestmod)

        if createNew:
            logging.info('Initializing new feeds')
            self.metafeed.write(cbor2.dumps(["VERSION", self.version]))
            self.blobfeed.write(cbor2.dumps(["VERSION", self.version]))
        logging.info('Loading feeds')
        if self._fsck() > 0:
            raise Exception('Integrity check failed')


    """ close gracefully and cleanup """
    def __del__(self):
        logging.debug('Shutdown DecentFs')
        return


    """ handle multiple key flavors """
    def _load_keyfile(self):
        with open(self.keyfile, 'r') as f:
            key = eval(f.read())
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


    """
    Quick integrity check
    TODO: check consistency between meta and blob
    return: 0 or amount of failures
    """
    def _fsck(self) -> int:
        logging.debug('Checking feeds')
        logging.debug('Feed version %s', self._version())
        err = 0
        for f in [self.blobfeed, self.metafeed]:
            f.seq = 0
            f.hprev = None
            for e in f:
                if not f.is_valid_extension(e):
                    logging.debug('Error found at %i', f.seq)
                    err += 1
                f.seq += 1
                f.hprev = e.get_ref()
        logging.debug('Feed version %s', self._version())
        return err


    def _version(self) -> str:
        logging.debug('Checking feeds')
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


    """ Dump pcap content """
    def dump(self):
        logging.debug('Invoke pcap dump')
        bacnet.pcap.dump(os.path.join(self.storage, self._DEFAULT_META))
        return


    """ Create write stream """
    def createWriteStream(self, path) -> stream:
        self.stream = open(path, 'rb')
        return self.stream


    """ Write to DecentFs """
    def writeFile(self, path, buf=None, flags='') -> int:
        logging.info('Append file %s', path)
        if buf is None:
            self.stream = self.createWriteStream(path)
            buf = self.stream
        slices = []
        size = 0
        writeops = 0
        while (block := buf.read(self.BUF_SIZE)):
            blockid = blake2b(block).digest()
            slices.append(blockid)
            size += len(block)
            if not self._findDuplicate(blockid):
                writeops += 1
                logging.info('Writeing new block %s', blockid.hex())
                self.blobfeed.write(cbor2.dumps([blockid, block]))
        self.metafeed.write(cbor2.dumps([path.__str__(), flags, time.time_ns(), size, slices]))
        logging.info('Append metadata for %s', path)
        logging.info('%i of %i blocks deduplicated', len(slices) - writeops, len(slices))
        logging.debug('containing flags %s, bytes: %i and %i slices: %s', flags, size, len(slices), ','.join(map(bytes.hex, slices)))
        return 0


    """
    Finds duplicates of blocks
    return: True if block is already stored
    """
    def _findDuplicate(self, blockid) -> bool:
        duplicate = False
        for entry in self.blobfeed:
            existingid, _ = cbor2.loads(entry.content())
            if existingid == "VERSION":
                logging.debug('Skipping special block %s', existingid)
                continue
            if compare_digest(existingid, blockid):
                duplicate = True
                logging.debug('Deduplicating block %s', blockid.hex())
                break
        return duplicate
