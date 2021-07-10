#!/usr/bin/env python3

import binascii
import lopy4_hmac as hmac

def test(digestmod, key, data, digest):
    try:
        a = getattr(hmac._hashlib, digestmod)
    except:
        print("this platform does not support", digestmod)
        return
    h = hmac.HMAC(key, data, digestmod=digestmod).digest()
    assert h == binascii.unhexlify(digest)

test_vectors = [
    lambda : test('md5',
    b"\x0b" * 16,
    b"Hi There",
    "9294727A3638BB1C13F48EF8158BFC9D"),

    lambda : test('md5',
     b"Jefe",
     b"what do ya want for nothing?",
     "750c783e6ab0b503eaa86e310a5db738"),

    lambda : test('md5',
     b"\xaa" * 16,
     b"\xdd" * 50,
     "56be34521d144c88dbb8c733f0e8b3f6"),

    lambda : test('sha1',
     b"\x0b" * 20,
     b"Hi There",
     "b617318655057264e28bc0b6fb378c8ef146be00"),

    lambda : test('sha1',
     b"Jefe",
     b"what do ya want for nothing?",
     "effcdf6ae5eb2fa2d27416d5f184df9c259a7c79"),

    lambda : test('sha1',
     b"\xAA" * 20,
     b"\xDD" * 50,
     "125d7342b9ac11cd91a39af48aa17b4f63f175d3"),

    lambda : test('sha256',
     b'\x0b'*20,
     b'Hi There',
     'b0344c61d8db38535ca8afceaf0bf12b881dc200c9833da726e9376c2e32cff7'),

    lambda : test('sha256',
     b'Jefe',
     b'what do ya want for nothing?',
    '5bdcc146bf60754e6a042426089575c75a003f089d2739839dec58b964ec3843'),

    lambda : test('sha256',
     b'\xaa'*20,
     b'\xdd'*50,
     '773ea91e36800e46854db8ebd09181a72959098b3ef8c122d9635514ced565fe')
]

def doit():
    cnt = 0
    for x in test_vectors:
        print(cnt)
        x()
        cnt += 1

# ---------------------------------------------------------------------------

if __name__ == '__main__':

    print("Testing HMAC for three hash algorithms...")
    doit()

# eof
