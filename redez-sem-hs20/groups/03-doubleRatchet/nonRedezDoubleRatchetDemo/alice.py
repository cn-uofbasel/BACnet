from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

from helpers import SymmRatchet, dh_ratchet, pad, unpad, hkdf, b64
from helpers import serialize_public_key, deserialize_public_key
from helpers import serialize_private_key, deserialize_private_key
from helpers import save_status, load_status

from signing import xeddsa_verify

import os

path_alice_keys = os.getcwd() + '/alice_backup.key'
alice_x3dh_established_contacts = os.getcwd() + '/alice_established_x3dh_contacts.key'

path_alice_prev_pubkey = os.getcwd() + '/prev_pubkey_alice.key'

def get_x3dh_status(identifier_other: str):
    # Returns:
    # 0 - Not initialized
    # 2 - x3dh completed

    # Create files if they do not exist.
    try:
        with open(alice_x3dh_established_contacts, 'x') as f:
            print("Created file:", alice_x3dh_established_contacts)
    except OSError:
        pass

    # Check files for identifier_other

    with open(alice_x3dh_established_contacts, 'rt') as f:
        lines = [line.rsplit()[0] for line in f.readlines()]
        if identifier_other in lines:
            return 2
    return 0


class Alice(object):
    def __init__(self, identifier_other):
        # generate Alice's keys
        self.identifier_other = identifier_other
        self.x3dh_status = get_x3dh_status(identifier_other)
        self.backup_path = path_alice_keys
        self.path_prev_pubkey = path_alice_prev_pubkey

        if self.x3dh_status == 0:
            (self.IK, self.EKa) = load_alice_keys()

            self.Ns = 0
            self.Nr = 1
            self.PNs = 0
            self.PNr = 1

        elif self.x3dh_status == 2:
            (self.IK, _) = load_alice_keys()

            load_status(self)
            pass


    def x3dh(self, bob):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.IK.exchange(bob.SPKb.public_key())
        dh2 = self.EKa.exchange(bob.IK.public_key())
        dh3 = self.EKa.exchange(bob.SPKb.public_key())
        dh4 = self.EKa.exchange(bob.OPKb.public_key())
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Alice]\tShared key:', b64(self.sk))

    def x3dh_with_keys(self, bob_SPKb: X25519PublicKey, bob_IK: X25519PublicKey, bob_OPKb: X25519PublicKey):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.IK.exchange(bob_SPKb)
        dh2 = self.EKa.exchange(bob_IK)
        dh3 = self.EKa.exchange(bob_SPKb)
        dh4 = self.EKa.exchange(bob_OPKb)
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        #print('[Alice]\tShared key:', b64(self.sk))

    def alice_x3dh_over_tcp(self, socket):
        print("Start X3DH")
        #print("Initialized alice. Identity key IK:", self.IK)
        received_keys = socket.recv(128)
        IK_bytes_received = received_keys[:32]
        SPKb_bytes_received = received_keys[32:64]
        OPKb_bytes_received = received_keys[64:96]
        DH_ratchet_publickey_bob_received = received_keys[96:128]
        # print("received IK:", IK_bytes_received)
        # print("received SPKb:", SPKb_bytes_received)
        # print("received OPKb:", OPKb_bytes_received)
        IK = deserialize_public_key(IK_bytes_received)
        SPKb = deserialize_public_key(SPKb_bytes_received)
        OPKb = deserialize_public_key(OPKb_bytes_received)
        DH_ratchet_publickey_bob = deserialize_public_key(DH_ratchet_publickey_bob_received)
        self.x3dh_with_keys(bob_IK=IK, bob_SPKb=SPKb, bob_OPKb=OPKb)

        self.init_ratchets()
        dh_ratchet(self, DH_ratchet_publickey_bob)

        IK_bytes = serialize_public_key(self.IK.public_key())
        EKa_bytes = serialize_public_key(self.EKa.public_key())
        msg_to_send = b''.join([IK_bytes, EKa_bytes])
        socket.send(msg_to_send)
        print("Shared key:", b64(self.sk))
        print("Finished X3DH")


    def x3dh_create_key_bundle_from_received_key_bundle(self, received_prekey_bundle: bytes) -> bytes:
        # Received initial key packet contains:
        # - [32] DH_ratchet_public_key: DH_ratchet_initial_bytes
        # - [32] Bob's identity key: IK
        # - [32] Bob's signed prekey: SPKb
        # - [32] One one-time prekey: OPKb
        # - [32] Public key of the signature: signature_pubkey
        # - [64] Bob's prekey signature Sig(Encode(IK), Encode(SPKb)): signature
        #
        # DH_ratchet_public_key || IK || SPKb || OPKb || signature_pubkey || signature
        #        32             || 32  ||  32  ||  32  ||        32        ||    64
        # Total length: 224 bytes

        print("Start X3DH")
        assert(len(received_prekey_bundle) == 224)
        # print("Initialized alice. Identity key IK:", self.IK)
        DH_ratchet_publickey_bob_received = received_prekey_bundle[:32]
        IK_bytes_received = received_prekey_bundle[32:64]
        SPKb_bytes_received = received_prekey_bundle[64:96]
        OPKb_bytes_received = received_prekey_bundle[96:128]
        signature_pubkey = received_prekey_bundle[128:160]
        signature = received_prekey_bundle[160:224]
        keys = received_prekey_bundle[:128]

        if xeddsa_verify(pubkey=signature_pubkey, data=keys, signature=signature):
            print('Verification successful!')
        else:
            print('Verification failed!')
            exit()

        IK = deserialize_public_key(IK_bytes_received)
        SPKb = deserialize_public_key(SPKb_bytes_received)
        OPKb = deserialize_public_key(OPKb_bytes_received)
        DH_ratchet_publickey_bob = deserialize_public_key(DH_ratchet_publickey_bob_received)
        self.x3dh_with_keys(bob_IK=IK, bob_SPKb=SPKb, bob_OPKb=OPKb)

        self.init_ratchets()
        dh_ratchet(self, DH_ratchet_publickey_bob)

        IK_bytes = serialize_public_key(self.IK.public_key())
        EKa_bytes = serialize_public_key(self.EKa.public_key())
        msg_to_send = b''.join([IK_bytes, EKa_bytes])
        print("Shared key:", b64(self.sk))
        print("Finished X3DH")

        with open(alice_x3dh_established_contacts, 'ab') as f:
            f.write(bytes(self.identifier_other + os.linesep, 'utf-8'))
            pass

        save_status(self)

        return msg_to_send

    def init_ratchets(self):
        # initialize the root chain with the shared key
        self.root_ratchet = SymmRatchet(self.sk)
        # initialize the sending and recving chains
        self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        # Alice's DH ratchet starts out uninitialized
        self.DHratchet = None

    def create_message_event(self):
        raise NotImplementedError

    def load_prev_pubkey(self) -> bytes:
        try:
            with open(self.path_prev_pubkey, 'rb') as f:
                key_bytes = f.read()
                return key_bytes
        except FileNotFoundError:
            return None

    def save_prev_pubkey(self, serialized_key: bytes):
        with open(self.path_prev_pubkey, 'wb') as f:
            f.write(serialized_key)


path_keys_alice = os.getcwd() + '/keys_alice.key'
def load_alice_keys() -> (X25519PrivateKey, X25519PrivateKey):
    # If existing, load the saved identity key IK.
    # If not existing, generate new key, and save it.
    # Generate ephemeral key and do not save it.

    # Returns 2 keys:
    # Identity key from alice   IK: X25519PrivateKey
    # Ephemeral key             EKa: X25519PrivateKey
    EKa = X25519PrivateKey.generate()
    try:
        with open(path_keys_alice, 'rb') as f:
            IK_bytes = f.read()
            IK = deserialize_private_key(IK_bytes)
            print("Loaded saved keys.")
    except FileNotFoundError:
        print("No keys found. Creating new keys...")
        IK = X25519PrivateKey.generate()
        with open(path_keys_alice, 'wb') as f:
            for key in [IK]:
                f.write(serialize_private_key(key))
            print("Keys saved.")
        pass
    return (IK, EKa)