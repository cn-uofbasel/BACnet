import bacnet.crypto
import bacnet.feed
import os

class DecentFs:
    VERSION = '0.0.0-dev'
    _DEFAULT_BLOB = 'blob.pcap'
    _DEFAULT_META = 'meta.pcap'
    _DEFAULT_STORAGE = './.decentfs'

    discoveryKey = ''
    keyfile = None
    peers = ''
    version = ''
    writable = True
    storage = ''
    blobfeed = None
    metafeed = None


    """ create or open filesystem """
    def __init__(self, keyfile, storage=None, opt=''):
        self.keyfile = keyfile
        createNew = False
        if storage is None:
            createNew = True
            self.storage = self._DEFAULT_STORAGE
            self.version = self.VERSION
            os.makedirs(self.storage)
        else:
            self.storage = storage

        fid, signer, digestmod = self._load_keyfile()
        blobpcap = os.path.join(self.storage, self._DEFAULT_BLOB)
        metapcap = os.path.join(self.storage, self._DEFAULT_META)
        self.blobfeed = bacnet.feed.FEED(blobpcap, fid, signer, createNew, digestmod=digestmod)
        self.metafeed = bacnet.feed.FEED(metapcap, fid, signer, createNew, digestmod=digestmod)

        if createNew:
            self.metafeed.write("VERSION " + self.version)
            self.blobfeed.write("VERSION " + self.version)
        if self._fsck() > 0:
            raise Exception('Integrity check failed')


    """ close gracefully and cleanup """
    def __del__(self):
        return


    """ handle multiple key flavors """
    def _load_keyfile(self):
        with open(self.keyfile, 'r') as f:
            key = eval(f.read())
        if key['type'] == 'ed25519':
            fid = bytes.fromhex(key['public'])
            signer = bacnet.crypto.ED25519(bytes.fromhex(key['private']))
            digestmod = 'sha256'
        elif key['type'] in ['hmac_sha256', 'hmac_sha1', 'hmac_md5']:
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
        err = 0
        for f in [self.blobfeed, self.metafeed]:
            f.seq = 0
            f.hprev = None
            for e in f:
                if not f.is_valid_extension(e):
                    err += 1
                f.seq += 1
                f.hprev = e.get_ref()
        return err
