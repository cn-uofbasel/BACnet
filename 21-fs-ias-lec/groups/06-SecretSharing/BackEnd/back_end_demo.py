import json

from BackEnd import keys
from BackEnd import settings
from os import urandom

if __name__ == '__main__':

    # HEY please don't push files this generates just delete them afterwards thanks :3
    # all files will be in the SecretSharing/data folder
    # If any imports don't work try marking 06-SS as a source-root folder.

    # key generation:

    # RSA key pairs

    ky = keys.RSA_Keys("example")
    # we should have created a new folder "example" in the keys directory with a key pair
    # because example doesn't exist yet.

    ky2 = keys.RSA_Keys("example_password_protected", passphrase="python")
    # this set of keys is password protected

    # ky3 = keys.RSA_Keys("key_from_victoria", public_key=key_from_victoria)
    # here we imported a public key from a friend and saved it to our files unprotected
    # key must be RSA format. Afterwards the key will be in the pubkey member field.

    # Use the following scheme to encrypt and decrypt:
    #   ky.pubkey.encrypt(#)
    #   ky.privateKey.encrypt(#)

    print(ky.as_string())
    print(ky2.as_string())

    del ky
    del ky2

    # key loading

    ky = keys.RSA_Keys("example")
    ky2 = keys.RSA_Keys("example_password_protected", passphrase="python")

    print(ky.as_string())
    print(ky2.as_string())

    # ED25519 Key Paris

    del ky
    del ky2

    ky = keys.ED25519("example2", new=True)

    print(ky.as_string(hsk=True))

    del ky

    ky = keys.ED25519("example2")

    print(ky.as_string(hsk=True))

    # Contacts

    contacts = settings.Contacts()  # generating
    try:
        contacts.load()  # loading current data
    except json.JSONDecodeError:
        print("No information found.")
    contacts["Victoria"] = {}
    contacts["Victor"] = {}
    contacts.save()  # overriding

    # shares





