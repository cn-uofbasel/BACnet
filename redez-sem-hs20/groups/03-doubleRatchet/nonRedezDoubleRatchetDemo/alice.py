from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

from helpers import SymmRatchet, dh_ratchet, pad, unpad, hkdf, b64
from helpers import serialize_public_key, deserialize_public_key
from helpers import serialize_private_key, deserialize_private_key

import os

class Alice(object):
    def __init__(self):
        # generate Alice's keys
        (self.IKa, self.EKa) = load_alice_keys()
        self.Ns = 1
        self.Nr = 1
        self.PNs = 1
        self.PNr = 1

    def x3dh(self, bob):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.IKa.exchange(bob.SPKb.public_key())
        dh2 = self.EKa.exchange(bob.IKb.public_key())
        dh3 = self.EKa.exchange(bob.SPKb.public_key())
        dh4 = self.EKa.exchange(bob.OPKb.public_key())
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Alice]\tShared key:', b64(self.sk))

    def x3dh_with_keys(self, bob_SPKb: X25519PublicKey, bob_IKb: X25519PublicKey, bob_OPKb: X25519PublicKey):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.IKa.exchange(bob_SPKb)
        dh2 = self.EKa.exchange(bob_IKb)
        dh3 = self.EKa.exchange(bob_SPKb)
        dh4 = self.EKa.exchange(bob_OPKb)
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        #print('[Alice]\tShared key:', b64(self.sk))

    def alice_x3dh_over_tcp(self, socket):
        print("Start X3DH")
        #print("Initialized alice. Identity key IKa:", self.IKa)
        received_keys = socket.recv(128)
        IKb_bytes_received = received_keys[:32]
        SPKb_bytes_received = received_keys[32:64]
        OPKb_bytes_received = received_keys[64:96]
        DH_ratchet_publickey_bob_received = received_keys[96:128]
        # print("received IKb:", IKb_bytes_received)
        # print("received SPKb:", SPKb_bytes_received)
        # print("received OPKb:", OPKb_bytes_received)
        IKb = deserialize_public_key(IKb_bytes_received)
        SPKb = deserialize_public_key(SPKb_bytes_received)
        OPKb = deserialize_public_key(OPKb_bytes_received)
        DH_ratchet_publickey_bob = deserialize_public_key(DH_ratchet_publickey_bob_received)
        self.x3dh_with_keys(bob_IKb=IKb, bob_SPKb=SPKb, bob_OPKb=OPKb)

        self.init_ratchets()
        dh_ratchet(self, DH_ratchet_publickey_bob)

        IKa_bytes = serialize_public_key(self.IKa.public_key())
        EKa_bytes = serialize_public_key(self.EKa.public_key())
        msg_to_send = b''.join([IKa_bytes, EKa_bytes])
        socket.send(msg_to_send)
        print("Shared key:", b64(self.sk))
        print("Finished X3DH")

    def init_ratchets(self):
        # initialize the root chain with the shared key
        self.root_ratchet = SymmRatchet(self.sk)
        # initialize the sending and recving chains
        self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        # Alice's DH ratchet starts out uninitialized
        self.DHratchet = None

    '''
    def dh_ratchet(self, bob_public):
        # perform a DH ratchet rotation using Bob's public key
        if self.DHratchet is not None:
            # the first time we don't have a DH ratchet yet
            dh_recv = self.DHratchet.exchange(bob_public)
            shared_recv = self.root_ratchet.next(dh_recv)[0]
            self.PNr += 1
            # use Bob's public and our old private key
            # to get a new recv ratchet
            self.recv_ratchet = SymmRatchet(shared_recv)
            #print('[Alice]\tRecv ratchet seed:', b64(shared_recv))
        # generate a new key pair and send ratchet
        # our new public key will be sent with the next message to Bob
        self.DHratchet = X25519PrivateKey.generate()
        dh_send = self.DHratchet.exchange(bob_public)
        shared_send = self.root_ratchet.next(dh_send)[0]
        self.send_ratchet = SymmRatchet(shared_send)
        self.PNs += 1
        self.Ns = 1
        #print('[Alice]\tSend ratchet seed:', b64(shared_send))
    '''

    def create_message_event(self):
        raise NotImplementedError


path_keys_alice = os.getcwd() + '/keys_alice.key'
def load_alice_keys() -> (X25519PrivateKey, X25519PrivateKey):
    # If existing, load the saved identity key IKa.
    # If not existing, generate new key, and save it.
    # Generate ephemeral key and do not save it.

    # Returns 2 keys:
    # Identity key from alice   IKa: X25519PrivateKey
    # Ephemeral key             EKa: X25519PrivateKey
    EKa = X25519PrivateKey.generate()
    try:
        with open(path_keys_alice, 'rb') as f:
            lines = f.read()
            assert(len(lines) == 32)
            IKa_bytes = lines[:]
            IKa = deserialize_private_key(IKa_bytes)
            print("Loaded saved keys.")
    except FileNotFoundError:
        print("No keys found. Creating new keys...")
        IKa = X25519PrivateKey.generate()
        with open(path_keys_alice, 'wb') as f:
            for key in [IKa]:
                f.write(serialize_private_key(key))
            print("Keys saved.")
        pass
    return (IKa, EKa)