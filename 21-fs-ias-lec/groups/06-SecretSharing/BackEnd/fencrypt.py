"""Script to encrypt and decrypt files."""

import argparse
import bcrypt
import sys
import os
from BackEnd import core, settings

FILES = ["preferences", "shareBuffer", "secrets", "contacts"]
ENCODING = core.ENCODING


def setup_logging():
    # Todo move to main()
    import logging
    log_formatter = logging.Formatter('%(msecs)dms %(funcName)s %(lineno)d %(message)s')
    log_filename = os.path.join(settings.DATA_DIR, "secret_sharing.log")
    log_filemode = "w"
    log_level = logging.DEBUG

    fh = logging.FileHandler(filename=log_filename, mode=log_filemode)
    fh.setFormatter(log_formatter)
    sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(log_formatter)

    logger = logging.getLogger()
    logger.addHandler(fh)
    logger.addHandler(sh)
    logger.setLevel(log_level)


def main(password: str) -> None:
    # setup_logging()
    pwd_gate = settings.State("pwd_gate", settings.DATA_DIR, {"encrypted": False, "pwd": None})

    if not pwd_gate.get("pwd"):
        print("No password has been set in the application.")
        exit(0)

    if not bcrypt.checkpw(password.encode(ENCODING), pwd_gate.get("pwd").encode(ENCODING)):
        print("Password incorrect.")
        exit(0)

    else:

        if pwd_gate.get("encrypted"):
            answer = input("State is currently encrypted, do you want to decrypt? (y/n) \n >>")
            if answer == "n":
                print("Ok.")
                exit(0)
            elif answer == "y":
                core.decrypt_files(password, settings.DATA_DIR, FILES)
                pwd_gate["encrypted"] = False
                pwd_gate.save()
                print("Decrypted.")
                exit(0)
            else:
                print("Excuse me?")
                main(password)

        else:
            answer = input("State is currently decrypted, do you want to encrypt? (y/n) \n >>")
            if answer == "n":
                print("Ok.")
                exit(0)
            elif answer == "y":
                core.encrypt_files(password, settings.DATA_DIR, FILES)
                pwd_gate["encrypted"] = True
                pwd_gate.save()
                print("Encrypted.")
                exit(0)
            else:
                print("Excuse me?")
                main(password)




if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='File Encryption/Decryption')
    parser.add_argument('-pw', '--password', help='Input password.', required=True)
    main(parser.parse_args()[0])