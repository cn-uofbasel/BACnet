from database.ByteArrayHandler import ByteArrayHandler
import pytest


def test_init_handler():
    bh = ByteArrayHandler()
    try:
        with open('byteArrayDatabase.db') as f:
            pass
    except IOError:
        assert False
    assert bh.is_init()

def test_insert_byte_array_():
    str = ''


def main():
    pass


if __name__ == '__main__':
    main()