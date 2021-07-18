"""Very bootleg tests to see that the .core keeps working."""

import unittest
import sys
import logging
import json
from inspect import currentframe

from BackEnd import core

ENCODING = 'ISO-8859-1'
UNIT_TEST_START = "\n\n{}: START\n".format(currentframe().f_code.co_name)
UNIT_TEST_END = "\n{}: END\n\n".format(currentframe().f_code.co_name)

formatter = logging.Formatter('%(msecs)dms line %(lineno)d %(funcName)s %(message)s')
logger = logging.getLogger()
logger.level = logging.DEBUG
stream_handler = logging.StreamHandler(sys.stdout)
stream_handler.setFormatter(formatter)
logger.addHandler(stream_handler)


class Test_Core_Methods(unittest.TestCase):
    def test_password_encryption_and_decryption_correct_pwd(self):
        """Tests core.pwd_encrypt and core.pwd_decrypt"""
        logger.info(UNIT_TEST_START)
        plaintext = b'\xb3FI\xda\xf2\xa93Rd\xe2\x91w\x7fB\xa9\\'
        pwd = "m24#@Panda*"
        ciphertext = core.pwd_encrypt(pwd, plaintext)
        plaintext2 = core.pwd_decrypt(pwd, ciphertext)
        logger.debug("\n" + json.dumps(
                {
                    "Original Plaintext": plaintext.decode(ENCODING),
                    "Password": pwd,
                    "Ciphertext": ciphertext.decode(ENCODING),
                    "Plaintext Decrypted": plaintext2.decode(ENCODING),
                },
                indent=4
        ))
        logger.info(UNIT_TEST_END)
        assert plaintext == plaintext2

    def test_password_encryption_and_decryption_incorrect_pwd(self):
        """Tests core.pwd_encrypt and core.pwd_decrypt"""
        logger.info(UNIT_TEST_START)
        plaintext = b'\xb3FI\xda\xf2\xa93Rd\xe2\x91w\x7fB\xa9\\'
        pwd = "m24#@Panda*"
        pwd2 = "m24#@panda*"
        ciphertext = core.pwd_encrypt(pwd, plaintext)
        plaintext2 = core.pwd_decrypt(pwd2, ciphertext)
        logger.debug("\n" +
            json.dumps(
                {
                    "Original Plaintext": plaintext.decode(ENCODING),
                    "Password": pwd,
                    "Inc. Password": pwd2,
                    "Ciphertext": ciphertext.decode(ENCODING),
                    "Plaintext Decrypted": plaintext2.decode(ENCODING),
                },
                indent=4
            )
        )
        logger.info(UNIT_TEST_END)
        assert plaintext != plaintext2
        
    def test_sub_event_creation_and_decryption_share_event(self):
        """Tests create_sub_event and core.decrypt_sub_event"""
        logger.info(UNIT_TEST_START)
        logger.info("This test always fails if test_password_encryption_and_decryption fails.")
        ska = b'\xcc\xf1\xb4U\x0cM\xce\xbb\xf0HG\x10F~\xcd!\x7f\x81K\xb3n\xb9z\xc9\x1c\xd8`\x0e\xda\x89\x1b\xac'
        pka = b'\xfc\xcbr\x96t[\xe7\\p\xb8Z\xf0\xb6|E2\x98>\x00\xe5\x02$\x8c\x04;\x15\xd3+@\xbf\x0e\xb2'
        skb = b'\xfa4\xa0\x9dZ\xd5\x8e\xab@\xaf\xcb]\xff\x99@M\x90\xd5p\xe5_cM\xe0)\xf6{O\x10t"\xf9'
        pkb = b'\xfd\xe4&\x00}`\xb4T\x02\xe0\x03t\xed\xea\x98\x03b\x8a\x0b\x83\xc4\xca\xa0\xb3\xf5|\xe7\xf9\x03\x96B\xe0'
        pwda = "m24#@Panda*"
        pwdb = "f35@#Tiger$"  # unused here
        share = b'\xb3FI\xda\xf2\xa93Rd\xe2\x91w\x7fB\xa9\\'
        name = "MySecret"  # name of secret

        sub_event = core.create_sub_event(core.E_TYPE.SHARE, ska, pkb, password=pwda, shard=share, name=name)
        logger.debug("\n" + json.dumps(json.loads(sub_event), indent=4))
        sub_event_tpl = core.decrypt_sub_event(sub_event, skb, pka, pwdb)
        logger.debug("\n" + str(sub_event_tpl))

        t, share2, name2 = sub_event_tpl
        share2 = core.pwd_decrypt(pwda, share2)
        name2 = core.pwd_decrypt_name(pwda, name2)

        logger.info(UNIT_TEST_END)
        assert share == share2 and name == name2 and t == core.E_TYPE.SHARE

    def test_sub_event_creation_and_decryption_request_event(self):
        """Tests create_sub_event and core.decrypt_sub_event"""
        logger.info(UNIT_TEST_START)
        logger.info("This test always fails if test_password_encryption_and_decryption fails.")
        ska = b'\xcc\xf1\xb4U\x0cM\xce\xbb\xf0HG\x10F~\xcd!\x7f\x81K\xb3n\xb9z\xc9\x1c\xd8`\x0e\xda\x89\x1b\xac'
        pka = b'\xfc\xcbr\x96t[\xe7\\p\xb8Z\xf0\xb6|E2\x98>\x00\xe5\x02$\x8c\x04;\x15\xd3+@\xbf\x0e\xb2'
        skb = b'\xfa4\xa0\x9dZ\xd5\x8e\xab@\xaf\xcb]\xff\x99@M\x90\xd5p\xe5_cM\xe0)\xf6{O\x10t"\xf9'
        pkb = b'\xfd\xe4&\x00}`\xb4T\x02\xe0\x03t\xed\xea\x98\x03b\x8a\x0b\x83\xc4\xca\xa0\xb3\xf5|\xe7\xf9\x03\x96B\xe0'
        pwda = "m24#@Panda*"
        pwdb = "f35@#Tiger$"  # unused here
        name = "MySecret"  # name of secret

        sub_event = core.create_sub_event(core.E_TYPE.REQUEST, ska, pkb, password=pwda, name=name)
        logger.debug("\n" + json.dumps(json.loads(sub_event), indent=4))
        sub_event_tpl = core.decrypt_sub_event(sub_event, skb, pka, pwdb)
        logger.debug("\n" + str(sub_event_tpl))

        t, _, name2 = sub_event_tpl
        name2 = core.pwd_decrypt_name(pwda, name2)

        logger.info(UNIT_TEST_END)
        assert name == name2 and t == core.E_TYPE.REQUEST

    def test_sub_event_creation_and_decryption_reply_event(self):
        """Tests create_sub_event and core.decrypt_sub_event"""
        logger.info(UNIT_TEST_START)
        logger.info("This test always fails if test_password_encryption_and_decryption fails.")
        ska = b'\xcc\xf1\xb4U\x0cM\xce\xbb\xf0HG\x10F~\xcd!\x7f\x81K\xb3n\xb9z\xc9\x1c\xd8`\x0e\xda\x89\x1b\xac'
        pka = b'\xfc\xcbr\x96t[\xe7\\p\xb8Z\xf0\xb6|E2\x98>\x00\xe5\x02$\x8c\x04;\x15\xd3+@\xbf\x0e\xb2'
        skb = b'\xfa4\xa0\x9dZ\xd5\x8e\xab@\xaf\xcb]\xff\x99@M\x90\xd5p\xe5_cM\xe0)\xf6{O\x10t"\xf9'
        pkb = b'\xfd\xe4&\x00}`\xb4T\x02\xe0\x03t\xed\xea\x98\x03b\x8a\x0b\x83\xc4\xca\xa0\xb3\xf5|\xe7\xf9\x03\x96B\xe0'
        pwda = "m24#@Panda*"
        share = b'\x9a\x8f\xe5;\xc2\xfd-xG\x9e\xb3\xe7\xd8h\xf9%\xa4\xea\x01\xe2\xa52?\x99f\x92.~\xd5\x8b\xfb\x0f\xb5\xc1{\x02\xb9Y\x92\xd3\x83\x9fnN#\x1d\xd9/'
        name = 'Ç,@,óM38Ylä'

        sub_event = core.create_sub_event(core.E_TYPE.REPLY, ska, pkb, shard=share, name=name)
        logger.debug("\n" + json.dumps(json.loads(sub_event), indent=4))
        sub_event_tpl = core.decrypt_sub_event(sub_event, skb, pka, pwda)
        logger.debug("\n" + str(sub_event_tpl))

        t, share2, name2 = sub_event_tpl

        logger.info(UNIT_TEST_END)
        assert b'\xb3FI\xda\xf2\xa93Rd\xe2\x91w\x7fB\xa9\\' == share2 and "MySecret" == name2 and t == core.E_TYPE.REPLY

    def test_shamir_small(self):
        """tests core.split_small_secret_into_share_packages and core.recover_normal_secret"""
        logger.info(UNIT_TEST_START)
        s = b'\xb3FI\xda\xf2\xa93Rd\xe2\x91w\\'
        pck = core.split_small_secret_into_share_packages(s, 3, 5)
        pck.reverse()
        s2 = core.unpad(core.recover_normal_secret(pck[0:3]))
        logger.info(UNIT_TEST_END)
        assert s == s2
        logger.info(UNIT_TEST_END)

    def test_shamir_normal(self):
        """tests core.split_normal_secret_into_share_packages and core.recover_normal_secret"""
        logger.info(UNIT_TEST_START)
        s = b'\xb3FI\xda\xf2\xa93Rd\xe2\x91w\x7fB\xa9\\'
        pck = core.split_normal_secret_into_share_packages(s, 3, 5)
        pck.reverse()
        s2 = core.recover_normal_secret(pck[0:3])
        logger.info(UNIT_TEST_END)
        assert s == s2

    def test_shamir_large(self):
        """tests core.split_large_secret_into_share_packages and core.recover_large_secret"""
        logger.info(UNIT_TEST_START)
        s = b'\xb3FI\xda\xf2\xa93Rd\xe2\x91w\x7fB\xa9\x7fB\xa9\\'
        pck = core.split_large_secret_into_share_packages(s, 3, 5)
        pck.reverse()
        s2 = core.recover_large_secret(pck[0:3])
        logger.debug("\n" + str(s) + "\n" + str(s2) + "\n")
        assert s == s2
        logger.info(UNIT_TEST_END)


if __name__ == '__main__':
    suite = unittest.suite.TestSuite([Test_Core_Methods()])
    results = unittest.TextTestRunner(verbosity=2).run(suite)