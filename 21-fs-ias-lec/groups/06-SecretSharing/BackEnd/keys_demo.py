from BackEnd import keys

if __name__ == '__main__':

    # HEY please don't push files this generates just delete them afterwards thanks :3
    # If any imports don't work try marking 06-SS as a source-root folder.

    # key generation:

    key_manager = keys.KeyManager()
    secret, pubkey = key_manager.generate_key_pair("keyfile")  # key is automatically stored as "standard_key"

    print("Generated secret: {}, Generated pubkey: {}".format(secret, pubkey))

    # key retrieval:

    # clear stack
    del secret
    del pubkey
    del key_manager

    key_manager = keys.KeyManager()

    files: dict = key_manager.get_key_files()  # to get the filenames & paths
    print("Available files: {}\n".format(files))

    secret, pubkey = keys.KeyManager.get_keys("keyfile", files)

    print("PubKey: {}\n".format(pubkey))

    del files
    del pubkey

    secret, pubkey = key_manager.generate_key_pair('keyfile', private_key=secret)

    print("PubKey: {}\n".format(pubkey))
