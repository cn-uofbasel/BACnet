from database.ByteArrayHandler import ByteArrayHandler
import pytest
from cbor2 import dumps, loads
import os
import hashlib


def test_init_handler():
    try:
        bh = ByteArrayHandler()
        try:
            with open('byteArrayDatabase.db') as f:
                pass
        except IOError:
            assert False
        assert bh.is_init()
    finally:
        if os.path.exists('byteArrayDatabase.db'):
            os.remove('byteArrayDatabase.db')
        else:
            assert False


def test_insert_byte_array_():
    try:
        bh = ByteArrayHandler()
        input = 'Hello World!'
        data = dumps([input])
        e = loads(data)
        hrefTrue = hashlib.sha256(e[0].encode()).hexdigest()
        if not bh.insert_byte_array(data):
            assert False
        res = bh.retrieve_byte_array(hrefTrue)
        e = loads(res[0][1])
        href = hashlib.sha256(e[0].encode()).hexdigest()
        assert href == hrefTrue
        text = e[0]
        assert text == input
    finally:
        if os.path.exists('byteArrayDatabase.db'):
            os.remove('byteArrayDatabase.db')
        else:
            assert False
