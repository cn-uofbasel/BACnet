
import os.path
import sys
from binascii import hexlify, unhexlify
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Protocol.SecretSharing import Shamir
from Crypto.Util import Padding

#dirname = os.path.abspath(os.path.dirname(__file__))
#folderG4 = os.path.join(dirname, '../../../20-fs-ias-lec/groups/04-logMerge/eventCreationTool')
#print(folderG4)
#sys.path.append(folderG4)

#import EventCreationTool
#from logStore.appconn.chat_connection import Function

#ecf = EventCreationTool.EventFactory()

#chat_function = Function()
#public_key = ecf.get_feed_id()

key = bytes.fromhex('fc553b9c8c538019ac6de37e793286ec')



#padded_key = Padding.pad(key, 16);
#print(padded_key)
shares = Shamir.split(2, 5, key)
share_container = []
for idx, share in shares:
    print(share)
    share_container.append((idx, hexlify(share)))
    print("Index #%d: %s" % (idx, hexlify(share)))

with open("clear.txt", "rb") as fi, open("enc.txt", "wb") as fo:
    cipher = AES.new(key, AES.MODE_EAX)
    ct, tag = cipher.encrypt(fi.read()), cipher.digest()
    fo.write(cipher.nonce + tag + ct)


shares_recover = []
for x in range(2):
    idx = input("Enter index of share you want to use:\n")

    #idx, share = [s.strip() for s in in_str.split(",")]
    #idx, share = [strip(s) for s in in_str.split(",")]
    #shares.append((idx, unhexlify(share)))
    i, curr_share = share_container[int(idx)-1]
    shares_recover.append((i, unhexlify(curr_share)))
#for s in shares_recover:
    #print(s)
recovered_key = Shamir.combine(shares_recover)

#recovered_key = Padding.unpad(padded_recovered_key, 8)

with open("enc.txt", "rb") as fi:
    nonce, tag = [fi.read(16) for x in range(2)]
    print("recoverd key: ", recovered_key)
    print("hexed recovered key", hexlify(recovered_key))
    cipher = AES.new(recovered_key, AES.MODE_EAX, nonce)
    try:
        result = cipher.decrypt(fi.read())
        print("decrypting worked")
        cipher.verify(tag)
        print("verification worked")
        with open("clear2.txt", "wb") as fo:
            fo.write(result)
    except ValueError:
        print("The shares were incorrect")