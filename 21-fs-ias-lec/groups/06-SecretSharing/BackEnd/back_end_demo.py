import json

from BackEnd import keys
from BackEnd import settings

if __name__ == '__main__':

    # HEY please don't push files this generates just delete them afterwards thanks :3
    # all files will be in the SecretSharing/data folder
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

    hmac_keys.get_keys("key_ed25519", files)  # wont work, returns null

    print("ED25519: Generated secret: {}, Generated pubkey: {}".format(
        ed.get_private_key(), ed.get_public_key()
    ))

    print("HMAC: Generated secret: {}, Generated feed: {}".format(
        hmac.get_private_key(), hmac.get_feed_id()
    ))

    # Contacts

    contacts = settings.Contacts()  # generating
    try:
        contacts.load()  # loading current data
    except json.JSONDecodeError:
        print("No information found.")
    contacts["Victoria"] = {"public": ed.get_public_key().hex(), "feed": hmac.get_feed_id().hex()}
    contacts["Victor"] = {"public": ed.get_public_key().hex(), "feed": hmac.get_feed_id().hex()}
    contacts.save()  # overriding
