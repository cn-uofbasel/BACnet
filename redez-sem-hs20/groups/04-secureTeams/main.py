# create an identity    ./lib/crypto.py > alice-secret.key
# create a feed         ./lib/feed.py --keyfile alice-secret.key alice.pcap create
# append to feed        ./lib/feed.py --keyfile alice-secret.key alice.pcap append
# check feed            ./lib/feed.py --keyfile alice-secret.key alice.pcap check
# dump content          ./lib/pcap.py mixed.pcap

from nacl.public import PrivateKey, PublicKey, Box
from nacl.encoding import Base64Encoder
import nacl.utils

from feed import FEED
import crypto

def loadUser(user):
    if user != None:
        key_dir = 'keys/'
        user_key_path = key_dir+user+'.key'
        user_ppk_path = key_dir+user+'.ppk'
        
        if not os.path.isfile(user_key_path):
            print("User keys not accessible. Creating new identity...")
            if not os.path.exists(key_dir):
                try:
                    os.mkdir(key_dir)
                except OSError as error:
                    print(error)
                    sys.exit()
            with open(user_key_path, "w") as f:
                key_pair = crypto.ED25519()
                key_pair.create()
                f.write('{\n  '+(',\n '.join(key_pair.as_string().split(','))[1:-1])+'\n}\n')
                print('new ED25519 key pair has been generated')
        
        if not os.path.exists(user_ppk_path):
            secretkey = PrivateKey.generate()
            publickey = secretkey.public_key

            publickey64 = publickey.encode(Base64Encoder).decode("utf8")
            secretkey64 = secretkey.encode(Base64Encoder).decode("utf8")

            with open(user_ppk_path, "w") as myfile:
                myfile.write(publickey64)
                myfile.write("\n")
                myfile.write(secretkey64)
                myfile.write("\n")
                print('new ppk pair generated')
        else:
            with open(user_ppk_path, "r") as myfile:
                publickey64 = myfile.readline()
                secretkey64 = myfile.readline()

        publickey = PublicKey(publickey64, Base64Encoder)
        secretkey = PrivateKey(secretkey64, Base64Encoder)
        
        with open(user_key_path, 'r') as f:
            key = eval(f.read())
            if key['type'] == 'ed25519':
                fid = bytes.fromhex(key['public'])
                signer = crypto.ED25519(bytes.fromhex(key['private']))
                digestmod = 'sha256'
            return fid, signer, digestmod, secretkey, publickey
    else:
        print('No user provided.')
        sys.exit()
    return None

def writeEvent(user, event, content):
    key = loadUser(user)
    if key != None:
        fid, signer, digestmod, secretkey, publickey = key
        feed = FEED(user+'.pcap', fid, signer, True, digestmod=digestmod)
        if feed.pcap != None:
            feed.write(eval('[\''+event+'\',\''+content+'\']'))
        else:
            print('pcap error')
            sys.exit()
    else:
        print('error while parsing keyfile')
        sys.exit()

def invite(user, pk_joining, content):
    key = loadUser(user)
    if key != None:
        fid, signer, digestmod, secretkey, publickey = key

        e2ee_box =  Box(secretkey, PublicKey(pk_joining, Base64Encoder))
        message = bytes(content.encode('utf-8'))
        encrypted = e2ee_box.encrypt(message, encoder=Base64Encoder)

        feed = FEED(user+'.pcap', fid, signer, True, digestmod=digestmod)
        if feed.pcap != None:
            print('writing boxed event...')
            print(encrypted)
            feed.write(encrypted)
        else:
            print('pcap error')
            sys.exit()
    else:
        print('error while parsing keyfile')
        sys.exit()

def decrypt(user, pk_sender, cypher):
    key = loadUser(user)
    if key != None:
        fid, signer, digestmod, secretkey, publickey = key
        e2ee_box = Box(secretkey, PublicKey(pk_sender, Base64Encoder))
        try:
            plaintext = e2ee_box.decrypt(cypher, encoder=Base64Encoder)
            print('DECRYPTED TEXT: '+plaintext.decode('utf-8'))
        except nacl.exceptions.CryptoError as e:
            print(e)
            sys.exit()
    else:
        print('error while parsing keyfile')
        sys.exit()

if __name__ == '__main__':
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser(description='Secure Team Chat')
    parser.add_argument('--chat', required=True)
    parser.add_argument('--user', default='default')
    parser.add_argument('CMD', choices=['create','invite','message','decrypt'])
    
    args = parser.parse_args()

    if args.CMD == 'message':
        print('write your message and press enter...')
        writeEvent(args.user, 'chat/message', sys.stdin.readline().splitlines()[0])
    elif args.CMD == 'invite':
        print('type someone\'s id and press enter...')
        invite(args.user, sys.stdin.readline().splitlines()[0], 'you have been invited')
    elif args.CMD == 'create':
        print('creating a new secure team chat...')
        writeEvent(args.user, 'chat/create', 'new chat '+args.chat)
    elif args.CMD == 'decrypt':
        print('write the sender\'s public key, press enter, type cypher and enter...')
        decrypt(args.user, sys.stdin.readline().splitlines()[0], sys.stdin.readline().splitlines()[0])
