"""HMAC (Keyed-Hashing for Message Authentication) module.

Implements the HMAC algorithm as described by RFC 2104.

May 2020: <christian.tschudin@unibas.ch>
  copied from cpython, change to run in Micropython
"""

try:
    import warnings as _warnings
except:
    class _warnings:
        def warn(self, *args):
            pass
            # print(args)
    RuntimeWarning = None

import hashlib as _hashlib

trans_5C = bytes((x ^ 0x5C) for x in range(256))
trans_36 = bytes((x ^ 0x36) for x in range(256))

# The size of the digests returned by HMAC depends on the underlying
# hashing module used.  Use digest_size from the instance of HMAC instead.
# digest_size = None



class HMAC:
    """RFC 2104 HMAC class.  Also complies with RFC 4231.

    This supports the API for Cryptographic Hash Functions (PEP 247).
    """
    blocksize = 64  # 512-bit HMAC; can be changed in subclasses.

    def __init__(self, key, msg=None, digestmod=''):
        """Create a new HMAC object.

        key: bytes or buffer, key for the keyed hash object.
        msg: bytes or buffer, Initial input for the hash or None.
        digestmod: A hash name suitable for hashlib.new(). *OR*
                   A hashlib constructor returning a new hash object. *OR*
                   A module supporting PEP 247.

                   Required as of 3.8, despite its position after the optional
                   msg argument.  Passing it as a keyword argument is
                   recommended, though not required for legacy API reasons.
        """

        if not isinstance(key, (bytes, bytearray)):
            raise TypeError("key: expected bytes or bytearray, but got %r" % type(key).__name__)

        if not digestmod:
            raise TypeError("Missing required parameter 'digestmod'.")

        if callable(digestmod):
            self.digest_cons = digestmod
        elif isinstance(digestmod, str):
            self.digest_cons = lambda d=b'': getattr(_hashlib, digestmod)(d)
        else:
            self.digest_cons = lambda d=b'': digestmod.new(d)

        self.inner = self.digest_cons()
        if hasattr(self.inner, 'digest_size'):
            self.digest_size = self.inner.digest_size
        else:
            self.digest_size = {
                'sha256': 32,
                'sha1': 20,
                'md5': 16
            }[digestmod]

        if hasattr(self.inner, 'block_size'):
            blocksize = self.inner.block_size
            if blocksize < 16:
                _warnings.warn('block_size of %d seems too small; using our '
                               'default of %d.' % (blocksize, self.blocksize),
                               RuntimeWarning, 2)
                blocksize = self.blocksize
        else:
            _warnings.warn('No block_size attribute on given digest object; '
                           'Assuming %d.' % (self.blocksize),
                           RuntimeWarning, 2)
            blocksize = self.blocksize

        # self.blocksize is the default blocksize. self.block_size is
        # effective block size as well as the public API attribute.
        self.block_size = blocksize

        if len(key) > blocksize:
            key = self.digest_cons(key).digest()

        try:
            key = key.ljust(blocksize, b'\0')
            self.outer_key_translated = key.translate(trans_5C)
            self.inner.update(key.translate(trans_36))
        except:
            key = (key + b'\0' * blocksize)[:blocksize]
            self.outer_key_translated = bytes(trans_5C[i] for i in key)
            self.inner.update(bytes(trans_36[i] for i in key))
        if msg is not None:
            self.update(msg)

        self.finished = False
        self.digest_bytes = None


    @property
    def name(self):
        return "hmac-" + self.inner.name

    def update(self, msg):
        """Feed data from msg into this hashing object."""
        self.inner.update(msg)

    def digest(self):
        """Return the hash value of this hashing object.

        This returns the hmac value as bytes. You CANNOT continue
        updating the object after calling this function.
        """
        if not self.finished:
            inner_digest = self.inner.digest()
            del(self.inner)
            self.outer = self.digest_cons()
            self.outer.update(self.outer_key_translated + inner_digest)
            self.digest_bytes = self.outer.digest()
            del(self.outer)
            self.finished = True
        return self.digest_bytes

    def hexdigest(self):
        """Like digest(), but returns a string of hexadecimal digits instead.
        """
        return self.digest().hex()

def new(key, msg=None, digestmod=''):
    """Create a new hashing object and return it.

    key: bytes or buffer, The starting key for the hash.
    msg: bytes or buffer, Initial input for the hash, or None.
    digestmod: A hash name suitable for hashlib.new(). *OR*
               A hashlib constructor returning a new hash object. *OR*
               A module supporting PEP 247.

               Required as of 3.8, despite its position after the optional
               msg argument.  Passing it as a keyword argument is
               recommended, though not required for legacy API reasons.

    You can now feed arbitrary bytes into the object using its update()
    method, and can ask for the hash value at any time by calling its digest()
    or hexdigest() methods.
    """
    return HMAC(key, msg, digestmod)


def compare_digest(a,b):
    return a == b

# eof
