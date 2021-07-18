"""
Script to encrypt and decrypt files. Run with argument:

python3 fencrypt.py -pw <<password>>

It will not work if you have not set a password for the Secret Sharing application yet / first login.

"""

import argparse
import bcrypt
import sys
import os
from BackEnd import core, settings

FILES = ["preferences", "shareBuffer", "secrets", "contacts"]
ENCODING = core.ENCODING


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
    args = parser.parse_args()
    main(args.password)
