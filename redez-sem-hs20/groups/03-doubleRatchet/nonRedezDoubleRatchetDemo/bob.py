from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

from Crypto.Cipher import AES

from helpers import SymmRatchet, pad, unpad, hkdf, b64
from helpers import serialize_public_key, deserialize_public_key
from helpers import serialize_private_key, deserialize_private_key
from helpers import save_status, load_status

from signing import xeddsa_sign

import os


path_bob_x3dh_outstanding = os.getcwd() + '/bob_outstanding_x3dh_contacts.key'
path_bob_x3dh_established = os.getcwd() + '/bob_established_x3dh_contacts.key'
path_bob_identity_key = os.getcwd() + '/bob_identity_key.key'

path_bob_keys = os.getcwd() + '/bob_x3dh_keys.key'
path_bob_backup = os.getcwd() + '/bob_backup.key'

def get_x3dh_status(identifier_other: str):
    # Returns:
    # 0 - Not initialized
    # 1 - Initialized, waiting for response x3dh prekey bundle from alice
    # 2 - x3dh completed

    # Create files if they do not exist.
    try:
        with open(path_bob_x3dh_established, 'x') as f:
            print("Created file:", path_bob_x3dh_established)
    except OSError:
        pass
    try:
        with open(path_bob_x3dh_outstanding, 'x') as f:
            print("Created file:", path_bob_x3dh_outstanding)
    except OSError:
        pass

    # Check files for identifier_other

    with open(path_bob_x3dh_established, 'rt') as f:
        lines = [line.rsplit()[0] for line in f.readlines()]
        if identifier_other in lines:
            return 2
    with open(path_bob_x3dh_outstanding, 'rt') as f:
        lines = [line.rsplit()[0] for line in f.readlines()]
        if identifier_other in lines:
            return 1
    return 0


class Bob(object):
    def __init__(self, identifier_other):

        self.identifier_other = identifier_other
        self.x3dh_status = get_x3dh_status(identifier_other)
        self.backup_path = path_bob_backup
        print("status is:", self.x3dh_status)
        if self.x3dh_status == 0:  # Not initialized
            # generate Bob's keys
            (self.IK, self.SPKb, self.OPKb) = load_bob_keys()
            self.Ns = 0
            self.Nr = 1
            self.PNs = 0
            self.PNr = 1

            # initialize Bob's DH ratchet
            self.DHratchet = X25519PrivateKey.generate()
            self.save_keys()

            with open(path_bob_x3dh_outstanding, 'ab') as f:
                f.write(bytes(identifier_other + os.linesep, 'utf-8'))

        elif self.x3dh_status == 1:  # Initialized, waiting for response x3dh prekey bundle from alice
            self.load_keys()

            pass
        elif self.x3dh_status == 2:  # x3dh completed
            # TODO: implement this
            load_status(self, path_bob_backup)
            pass

    def save_keys(self):
        print("saving keys...")
        text_to_save = b''.join(
            [len(bytes(self.identifier_other, encoding='utf-8')).to_bytes(4, 'big'),    # 4
             bytes(self.identifier_other, encoding='utf-8'),                            # ?
             self.Ns.to_bytes(4, 'big'),                                                # 4
             self.Nr.to_bytes(4, 'big'),                                                # 4
             self.PNs.to_bytes(4, 'big'),                                               # 4
             self.PNr.to_bytes(4, 'big'),                                               # 4
             serialize_private_key(self.DHratchet),                                     # 290
             serialize_private_key(self.IK),                                           # 290
             serialize_private_key(self.SPKb),                                          # 290
             serialize_private_key(self.OPKb)]                                          # 290
        )
        with open(path_bob_keys, 'ab') as f:
            f.write(text_to_save)
        pass

    def load_keys(self):
        print("loading keys...")
        all = None
        with open(path_bob_keys, 'rb') as f:
            all = f.read()
        pass

        k = 0
        while True:
            identifier_length = int.from_bytes(all[k:k+4], 'big')
            if all[k+4:k+4+identifier_length] == bytes(self.identifier_other, 'utf-8'):
                keys = all[k+4+identifier_length:k+4+identifier_length+1176]
                all_updated = all[:k] + all[k+4+identifier_length+1176:]
                break
            elif all[k+4:k+4+identifier_length] == b'':
                print("Something went wrong. Cannot find saved keys for this person. Shutting down...")
                exit()

            k += 4 + identifier_length + 1176
        self.Ns = int.from_bytes(keys[0:4], 'big')
        self.Nr = int.from_bytes(keys[4:8], 'big')
        self.PNs = int.from_bytes(keys[8:12], 'big')
        self.PNr = int.from_bytes(keys[12:16], 'big')
        DHratchet_bytes = keys[16:16+290]
        IK_bytes = keys[16+290:16+2*290]
        SPKb_bytes = keys[16+2*290:16+3*290]
        OPKb_bytes = keys[16+3*290:16+4*290]
        self.DHratchet = deserialize_private_key(DHratchet_bytes)
        self.IK = deserialize_private_key(IK_bytes)
        print("SPKb_bytes:", SPKb_bytes)
        self.SPKb = deserialize_private_key(SPKb_bytes)
        self.OPKb = deserialize_private_key(OPKb_bytes)

        with open(path_bob_keys, 'wb') as f:
            f.write(all_updated)

    def x3dh(self, alice):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.SPKb.exchange(alice.IK.public_key())
        dh2 = self.IK.exchange(alice.EKa.public_key())
        dh3 = self.SPKb.exchange(alice.EKa.public_key())
        dh4 = self.OPKb.exchange(alice.EKa.public_key())
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        print('[Bob]\tShared key:', b64(self.sk))

    def x3dh_with_keys(self, alice_IK: X25519PublicKey, alice_EKa: X25519PublicKey):
        # perform the 4 Diffie Hellman exchanges (X3DH)
        dh1 = self.SPKb.exchange(alice_IK)
        dh2 = self.IK.exchange(alice_EKa)
        dh3 = self.SPKb.exchange(alice_EKa)
        dh4 = self.OPKb.exchange(alice_EKa)
        # the shared key is KDF(DH1||DH2||DH3||DH4)
        self.sk = hkdf(dh1 + dh2 + dh3 + dh4, 32)
        #print('[Bob]\tShared key:', b64(self.sk))

    def bob_x3dh_over_tcp(self, socket) -> None:
        ###### START X3DH #######
        print("Start X3DH")
        # IK, SPKb, OPKb
        IK_bytes = serialize_public_key(self.IK.public_key())
        SPKb_bytes = serialize_public_key(self.SPKb.public_key())
        OPKb_bytes = serialize_public_key(self.OPKb.public_key())
        DH_ratchet_initial_bytes = serialize_public_key(self.DHratchet.public_key())
        # print("self's Public key of IK:", IK_bytes)
        # print("self's Public key of SPKb:", SPKb_bytes)
        # print("self's Public key of OPKb:", OPKb_bytes)
        keys_to_send = b''.join([IK_bytes, SPKb_bytes, OPKb_bytes, DH_ratchet_initial_bytes])
        socket.send(keys_to_send)

        msg = socket.recv(64)
        IK_bytes = msg[:32]
        EKa_bytes = msg[32:]
        # print("msg received:", msg)
        # print("IK_bytes", IK_bytes)
        # print("EKa_bytes", EKa_bytes)
        IK = deserialize_public_key(IK_bytes)
        EKa = deserialize_public_key(EKa_bytes)
        self.x3dh_with_keys(alice_IK=IK, alice_EKa=EKa)
        self.init_ratchets()
        print("Shared Key:", b64(self.sk))
        print("Finished X3DH")
        ######  END X3DH  #######

    def x3dh_1_create_prekey_bundle(self) -> bytes:
        # Initial key packet contains:
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
        #
        # signature_pubkey and signature are generated by calling xed_sign(keys).
        #   signature_pubkey, signature = signing.xed_sign(keys),
        # where keys is the composition of the 3 keys: DH_ratchet_pubkey, IK, OPKb.
        # After that we send 224 bytes: keys || signature_pubkey || signature

        ###### START X3DH #######
        print("Start X3DH")
        # IK, SPKb, OPKb
        IK_bytes = serialize_public_key(self.IK.public_key())
        SPKb_bytes = serialize_public_key(self.SPKb.public_key())
        OPKb_bytes = serialize_public_key(self.OPKb.public_key())
        DH_ratchet_initial_bytes = serialize_public_key(self.DHratchet.public_key())
        # print("self's Public key of IK:", IK_bytes)
        # print("self's Public key of SPKb:", SPKb_bytes)
        # print("self's Public key of OPKb:", OPKb_bytes)
        keys = b''.join([DH_ratchet_initial_bytes, IK_bytes, SPKb_bytes, OPKb_bytes])
        signature_pubkey, signature = xeddsa_sign(keys)
        keys_to_send = b''.join([keys, signature_pubkey, signature])

        return keys_to_send


    def x3dh_2_complete_transaction_with_alice_keys(self, msg: bytes):
        assert(len(msg) == 64)
        IK_bytes = msg[:32]
        EKa_bytes = msg[32:]
        # print("msg received:", msg)
        # print("IK_bytes", IK_bytes)
        # print("EKa_bytes", EKa_bytes)
        IK = deserialize_public_key(IK_bytes)
        EKa = deserialize_public_key(EKa_bytes)
        self.x3dh_with_keys(alice_IK=IK, alice_EKa=EKa)
        self.init_ratchets()
        print("Shared Key:", b64(self.sk))
        print("Finished X3DH")
        ######  END X3DH  #######
        save_status(self)

        with open(path_bob_x3dh_outstanding, 'rb') as f:
            lines = f.read()
        lines = lines.replace(bytes(self.identifier_other + os.linesep, 'utf-8'), b'')
        with open(path_bob_x3dh_outstanding, 'wb') as f:
            f.write(lines)

        with open(path_bob_x3dh_established, 'ab') as f:
            f.write(bytes(self.identifier_other + os.linesep, 'utf-8'))

        pass


    def init_ratchets(self):
        # initialize the root chain with the shared key
        self.root_ratchet = SymmRatchet(self.sk)
        # initialize the sending and recving chains
        self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        # initialize Bob's DH ratchet (We do this in the initialization of Bob instead of here.)
        #self.DHratchet = X25519PrivateKey.generate()

    def create_message_event(self):
        raise NotImplementedError


key_length = 290
path_keys_bob = os.getcwd() + '/keys_bob.key'
def load_bob_keys() -> (X25519PrivateKey, X25519PrivateKey, X25519PrivateKey):
    # If existing, load the saved keys for bob.
    # If they do not already exists, generate new keys and save them.
    # Generate OPKb once and do not save it.

    # Returns 3 keys:
    # IK: X25519PrivateKey
    # SPKb: X25519PrivateKey
    # OPKb: X25519PrivateKey

    OPKb = X25519PrivateKey.generate()
    try:
        with open(path_keys_bob, 'rb') as f:
            lines = f.read()
            assert(len(lines) == 2*key_length)
            IK_bytes = lines[:key_length]
            SPKb_bytes = lines[key_length:]
            IK = deserialize_private_key(IK_bytes)
            SPKb = deserialize_private_key(SPKb_bytes)
            print("Loaded saved keys.")
    except FileNotFoundError:
        print("No keys found. Creating new keys...")
        IK = X25519PrivateKey.generate()
        SPKb = X25519PrivateKey.generate()
        with open(path_keys_bob, 'wb') as f:
            for key in [IK, SPKb]:
                f.write(serialize_private_key(key))
            print("Keys saved.")
        pass
    return (IK, SPKb, OPKb)