
from BackEnd import keys

if __name__ == '__main__':

    # HEY please don't push files this generates just delete them afterwards thanks :3
    # If any imports don't work try marking 06-SS as a source-root folder.

    # key generation:

    ed_keys = keys.ED25519Keys()
    ed = ed_keys.generate("key_ed25519")

    print("ED25519: Generated secret: {}, Generated pubkey: {}".format(
        ed.get_private_key(), ed.get_public_key()
    ))

    hmac_keys = keys.HMACKeys()
    hmac = hmac_keys.generate("key_hmac")

    print("HMAC: Generated secret: {}, Generated feed: {}".format(
        hmac.get_private_key(), hmac.get_feed_id()
    ))

    del ed_keys
    del ed

    del hmac_keys
    del hmac

    # key retrieval:

    ed_keys = keys.ED25519Keys()
    hmac_keys = keys.HMACKeys()

    files = ed_keys.get_files()

    print(files)

    ed = ed_keys.get_keys("key_ed25519", files)
    hmac = hmac_keys.get_keys("key_hmac", files)

    hmac_keys.get_keys("key_ed25519", files)  # wont work

    print("ED25519: Generated secret: {}, Generated pubkey: {}".format(
        ed.get_private_key(), ed.get_public_key()
    ))

    print("HMAC: Generated secret: {}, Generated feed: {}".format(
        hmac.get_private_key(), hmac.get_feed_id()
    ))
