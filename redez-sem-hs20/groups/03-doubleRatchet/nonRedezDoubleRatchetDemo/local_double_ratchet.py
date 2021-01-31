### I USED 'pip install pycryptodome', instead of 'pip3 install cryptography==2.8 pycrypto',
### because pycrypto didn't work to install.
### This is a fork, so it might have security bugs.
### Got the tip from https://stackoverflow.com/a/54142469

# All of the following is copied from:
# https://nfil.dev/coding/encryption/python/double-ratchet-example/

# Requirements:
# apt install python3 python3-pip
# pip3 install cryptography==2.8 pycrypto

import base64

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import \
        Ed25519PublicKey, Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend

from Crypto.Cipher import AES

import os

from Crypto.Hash import SHA256

def b64(msg):
    # base64 encoding helper function
    return base64.encodebytes(msg).decode('utf-8').strip()

def hkdf(inp, length):
    # use HKDF on an input to derive a key
    hkdf = HKDF(algorithm=hashes.SHA256(), length=length, salt=b'',
                info=b'', backend=default_backend())
    return hkdf.derive(inp)

def pad(msg):
    # pkcs7 padding
    num = 16 - (len(msg) % 16)
    return msg + bytes([num] * num)

def unpad(msg):
    # remove pkcs7 padding
    return msg[:-msg[-1]]

def serialize_public_key(public_key: X25519PublicKey) -> bytes:
    return public_key.public_bytes(encoding=serialization.Encoding.Raw, format=serialization.PublicFormat.Raw)
def deserialize_public_key(public_bytes) -> X25519PublicKey:
    return X25519PublicKey.from_public_bytes(public_bytes)

def serialize_private_key(private_key: X25519PrivateKey) -> bytes:
    return private_key.private_bytes(encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw,
                                     encryption_algorithm=serialization.NoEncryption())
def deserialize_private_key(private_bytes) -> X25519PrivateKey:
    return X25519PrivateKey.from_private_bytes(private_bytes)

class SymmRatchet(object):
    def __init__(self, key):
        self.state = key

    def next(self, inp=b''):
        # turn the ratchet, changing the state and yielding a new key and IV
        output = hkdf(self.state + inp, 80)
        self.state = output[:32]
        outkey, iv = output[32:64], output[64:]
        return outkey, iv

#######################################################################
path_keys_alice = os.getcwd() + '/keys_alice.txt'
def load_alice_keys() -> (X25519PrivateKey, X25519PrivateKey):
    # If existing, load the saved keys for alice.
    # If they do not already exists, generate new keys and save them.
    # Returns 2 keys:
    # IKa: X25519PrivateKey
    # EKa: X25519PrivateKey
    try:
        with open(path_keys_alice, 'rb') as f:
            lines = f.read()
            assert(len(lines) == 64)
            IKa_bytes = lines[:32]
            EKa_bytes = lines[32:]
            IKa = deserialize_private_key(IKa_bytes)
            EKa = deserialize_private_key(EKa_bytes)
            print("Loaded saved keys.")
    except FileNotFoundError:
        print("No keys found. Creating new keys...")
        IKa = X25519PrivateKey.generate()
        EKa = X25519PrivateKey.generate()
        with open(path_keys_alice, 'wb') as f:
            for key in [IKa, EKa]:
                f.write(serialize_private_key(key))
            print("Keys saved.")
        pass
    return (IKa, EKa)

path_keys_bob = os.getcwd() + '/keys_bob.txt'
def load_bob_keys():
    # If existing, load the saved keys for bob.
    # If they do not already exists, generate new keys and save them.
    # Returns 3 keys:
    # IKb: X25519PrivateKey
    # SPKb: X25519PrivateKey
    # OPKb: X25519PrivateKey
    try:
        with open(path_keys_bob, 'rb') as f:
            lines = f.read()
            assert(len(lines) == 96)
            IKb_bytes = lines[:32]
            SPKb_bytes = lines[32:64]
            OPKb_bytes = lines[64:]
            IKb = deserialize_private_key(IKb_bytes)
            SPKb = deserialize_private_key(SPKb_bytes)
            OPKb = deserialize_private_key(OPKb_bytes)
            print("Loaded saved keys.")
    except FileNotFoundError:
        print("No keys found. Creating new keys...")
        IKb = X25519PrivateKey.generate()
        SPKb = X25519PrivateKey.generate()
        OPKb = X25519PrivateKey.generate()
        with open(path_keys_bob, 'wb') as f:
            for key in [IKb, SPKb, OPKb]:
                f.write(serialize_private_key(key))
            print("Keys saved.")
        pass
    return (IKb, SPKb, OPKb)

'''
    
    self.IKb.private_bytes(encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw,
                           encryption_algorithm=serialization.NoEncryption())
    private_bytes = b'\x90\xc9\xdc\xa4\x99O\x9c\xfd&\x90\x8d\xce+\xb5\xf7_\xa6\x93\xeds\xe0\xc7/\xdc\x9eG%\xcf\xf3\xfa\x84q'
    IKb_copy = X25519PrivateKey.from_private_bytes(private_bytes)
    IKb_copy.private_bytes(encoding=serialization.Encoding.Raw, format=serialization.PrivateFormat.Raw,
                           encryption_algorithm=serialization.NoEncryption())
    load_bob_keys()

'''
#######################################################################

class Bob(object):
    def __init__(self):
        # generate Bob's keys
        (self.IKb, self.SPKb, self.OPKb) = load_bob_keys()


    def x3dh(self, alice):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.SPKb.exchange(alice.IKa.public_key())
        dh2 = self.IKb.exchange(alice.EKa.public_key())
        dh3 = self.SPKb.exchange(alice.EKa.public_key())
        dh4 = self.OPKb.exchange(alice.EKa.public_key())
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Bob]\tShared key:', b64(self.sk))

    def init_ratchets(self):
        # initialise the root chain with the shared key
        self.root_ratchet = SymmRatchet(self.sk)
        # initialise the sending and recving chains
        self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        # initialise Bob's DH ratchet
        self.DHratchet = X25519PrivateKey.generate()

    def dh_ratchet(self, alice_public):
        # perform a DH ratchet rotation using Alice's public key
        dh_recv = self.DHratchet.exchange(alice_public)
        shared_recv = self.root_ratchet.next(dh_recv)[0]
        # use Alice's public and our old private key
        # to get a new recv ratchet
        self.recv_ratchet = SymmRatchet(shared_recv)
        print('[Bob]\tRecv ratchet seed:', b64(shared_recv))
        # generate a new key pair and send ratchet
        # our new public key will be sent with the next message to Alice
        self.DHratchet = X25519PrivateKey.generate()
        dh_send = self.DHratchet.exchange(alice_public)
        shared_send = self.root_ratchet.next(dh_send)[0]
        self.send_ratchet = SymmRatchet(shared_send)
        print('[Bob]\tSend ratchet seed:', b64(shared_send))

    def send(self, alice, msg):
        key, iv = self.send_ratchet.next()
        cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(msg))
        print('[Bob]\tSending ciphertext to Alice:', b64(cipher))
        # send ciphertext and current DH public key
        alice.recv(cipher, self.DHratchet.public_key())

    def recv(self, cipher, alice_public_key):
        # receive Alice's new public key and use it to perform a DH
        self.dh_ratchet(alice_public_key)
        key, iv = self.recv_ratchet.next()
        # decrypt the message using the new recv ratchet
        msg = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(cipher))
        print('[Bob]\tDecrypted message:', msg)

class Alice(object):
    def __init__(self):
        # generate Alice's keys
        (self.IKa, self.EKa) = load_alice_keys()

    def x3dh(self, bob):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.IKa.exchange(bob.SPKb.public_key())
        dh2 = self.EKa.exchange(bob.IKb.public_key())
        dh3 = self.EKa.exchange(bob.SPKb.public_key())
        dh4 = self.EKa.exchange(bob.OPKb.public_key())
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Alice]\tShared key:', b64(self.sk))

    def init_ratchets(self):
        # initialise the root chain with the shared key
        self.root_ratchet = SymmRatchet(self.sk)
        # initialise the sending and recving chains
        self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        # Alice's DH ratchet starts out uninitialised
        self.DHratchet = None

    def dh_ratchet(self, bob_public):
        # perform a DH ratchet rotation using Bob's public key
        if self.DHratchet is not None:
            # the first time we don't have a DH ratchet yet
            dh_recv = self.DHratchet.exchange(bob_public)
            shared_recv = self.root_ratchet.next(dh_recv)[0]
            # use Bob's public and our old private key
            # to get a new recv ratchet
            self.recv_ratchet = SymmRatchet(shared_recv)
            print('[Alice]\tRecv ratchet seed:', b64(shared_recv))
        # generate a new key pair and send ratchet
        # our new public key will be sent with the next message to Bob
        self.DHratchet = X25519PrivateKey.generate()
        dh_send = self.DHratchet.exchange(bob_public)
        shared_send = self.root_ratchet.next(dh_send)[0]
        self.send_ratchet = SymmRatchet(shared_send)
        print('[Alice]\tSend ratchet seed:', b64(shared_send))

    def send(self, bob, msg):
        key, iv = self.send_ratchet.next()
        cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(msg))
        print('[Alice]\tSending ciphertext to Bob:', b64(cipher))
        # send ciphertext and current DH public key
        bob.recv(cipher, self.DHratchet.public_key())

    def recv(self, cipher, bob_public_key):
        # receive Bob's new public key and use it to perform a DH
        self.dh_ratchet(bob_public_key)
        key, iv = self.recv_ratchet.next()
        # decrypt the message using the new recv ratchet
        msg = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(cipher))
        print('[Alice]\tDecrypted message:', msg)



alice = Alice()
bob = Bob()

# Alice performs an X3DH while Bob is offline, using his uploaded keys
alice.x3dh(bob)

# Bob comes online and performs an X3DH using Alice's public keys
bob.x3dh(alice)

# Initialize their symmetric ratchets
alice.init_ratchets()
bob.init_ratchets()

# Initialise Alice's sending ratchet with Bob's public key
alice.dh_ratchet(bob.DHratchet.public_key())

# Alice sends Bob a message and her new DH ratchet public key
alice.send(bob, b'Hello Bob!')

# Bob uses that information to sync with Alice and send her a message
bob.send(alice, b'Hello to you too, Alice!')