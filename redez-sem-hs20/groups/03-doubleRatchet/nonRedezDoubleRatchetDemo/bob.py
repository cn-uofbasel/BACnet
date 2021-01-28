from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

from Crypto.Cipher import AES

from helpers import SymmRatchet, pad, unpad, hkdf, b64
from helpers import serialize_public_key, deserialize_public_key
from helpers import serialize_private_key, deserialize_private_key

import os



class Bob(object):
    def __init__(self):
        # generate Bob's keys
        (self.IKb, self.SPKb, self.OPKb) = load_bob_keys()

        # initialize Bob's DH ratchet
        self.DHratchet = X25519PrivateKey.generate()

    def x3dh(self, alice):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.SPKb.exchange(alice.IKa.public_key())
        dh2 = self.IKb.exchange(alice.EKa.public_key())
        dh3 = self.SPKb.exchange(alice.EKa.public_key())
        dh4 = self.OPKb.exchange(alice.EKa.public_key())
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Bob]\tShared key:', b64(self.sk))

    def x3dh_with_keys(self, alice_IKa: X25519PublicKey, alice_EKa: X25519PublicKey):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.SPKb.exchange(alice_IKa)
        dh2 = self.IKb.exchange(alice_EKa)
        dh3 = self.SPKb.exchange(alice_EKa)
        dh4 = self.OPKb.exchange(alice_EKa)
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Bob]\tShared key:', b64(self.sk))

    def init_ratchets(self):
        # initialize the root chain with the shared key
        self.root_ratchet = SymmRatchet(self.sk)
        # initialize the sending and recving chains
        self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        # initialize Bob's DH ratchet (We do this in the initialization of Bob instead of here.)
        #self.DHratchet = X25519PrivateKey.generate()

    def dh_ratchet(self, alice_public: X25519PublicKey):
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

    def create_message_event(self):
        raise NotImplementedError

    def send(self, alice, msg):
        key, iv = self.send_ratchet.next()
        cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(msg))
        print('[Bob]\tSending ciphertext to Alice:', b64(cipher))
        # send ciphertext and current DH public key
        alice.recv(cipher, self.DHratchet.public_key())

    def recv(self, cipher, alice_public_key):
        # receive Alice's new public key and use it to perform a DH
        print("Warning: method Bob.recv() is deprecated. Use Bob.decrypt_msg() instead.")
        self.dh_ratchet(alice_public_key)
        key, iv = self.recv_ratchet.next()
        # decrypt the message using the new recv ratchet
        msg = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(cipher))
        print('[Bob]\tDecrypted message:', msg)

    def decrypt_msg(self, cipher, alice_public_key) -> str:
        # receive Alice's new public key and use it to perform a DH
        self.dh_ratchet(alice_public_key)
        key, iv = self.recv_ratchet.next()
        # decrypt the message using the new recv ratchet
        msg = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(cipher))
        print('[Bob]\tDecrypted message:', msg)
        return msg

path_keys_bob = os.getcwd() + '/keys_bob.key'
def load_bob_keys() -> (X25519PrivateKey, X25519PrivateKey, X25519PrivateKey):
    # If existing, load the saved keys for bob.
    # If they do not already exists, generate new keys and save them.
    # Generate OPKb once and do not save it.

    # Returns 3 keys:
    # IKb: X25519PrivateKey
    # SPKb: X25519PrivateKey
    # OPKb: X25519PrivateKey

    OPKb = X25519PrivateKey.generate()
    try:
        with open(path_keys_bob, 'rb') as f:
            lines = f.read()
            assert(len(lines) == 64)
            IKb_bytes = lines[:32]
            SPKb_bytes = lines[32:]
            IKb = deserialize_private_key(IKb_bytes)
            SPKb = deserialize_private_key(SPKb_bytes)
            print("Loaded saved keys.")
    except FileNotFoundError:
        print("No keys found. Creating new keys...")
        IKb = X25519PrivateKey.generate()
        SPKb = X25519PrivateKey.generate()
        with open(path_keys_bob, 'wb') as f:
            for key in [IKb, SPKb]:
                f.write(serialize_private_key(key))
            print("Keys saved.")
        pass
    return (IKb, SPKb, OPKb)