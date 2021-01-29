from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.backends import default_backend

from Crypto.Cipher import AES

import base64

header_length = 36

class SymmRatchet(object):
    def __init__(self, key):
        self.state = key

    def next(self, inp=b''):
        # turn the ratchet, changing the state and yielding a new key and IV
        output = hkdf(self.state + inp, 80)
        self.state = output[:32]
        outkey, iv = output[32:64], output[64:]
        return outkey, iv


def send_tcp(socket, person: object, message: str):
    #print("Sending:", message)
    (cipher_text, dh_ratchet_public_key) = encrypt_msg(person, message)
    header = create_header_tcp(cipher_text, dh_ratchet_public_key)
    socket.send(b''.join([header, cipher_text]))


def recv_tcp(socket, person: object) -> str:
    # received_message = conn.recv(buffer_size, 0x40)
    received_message = socket.recv(header_length)
    msg_length, DHratchet_public_key_alice = unpack_header_tcp(received_message)
    cipher_text_received = socket.recv(msg_length)
    received_message_text = decrypt_msg(person, cipher_text_received, DHratchet_public_key_alice)
    return received_message_text

def encrypt_msg(person: object, msg: str) -> (bytes, bytes):
    # Encrypts the message.
    # Returns the ciphertext and the next DHratchet public key.
    msg = msg.encode('utf-8')
    key, iv = person.send_ratchet.next()
    cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(msg))
    return cipher, serialize_public_key(person.DHratchet.public_key())

def decrypt_msg(person: object, cipher, alice_public_key) -> str:
    # receive Alice's new public key and use it to perform a DH
    person.dh_ratchet(alice_public_key)
    key, iv = person.recv_ratchet.next()
    # decrypt the message using the new recv ratchet
    msg = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(cipher))
    msg = msg.decode('utf-8')
    # print('[Bob]\tDecrypted message:', msg)
    return msg

def create_header_tcp(cipher_text, DHratchet_public_key) -> bytes:
    # header of message, defined by
    # length || DHratchet_public_key

    header = b''.join([len(cipher_text).to_bytes(length=4, byteorder='big'), DHratchet_public_key])
    assert(len(header) == header_length)
    return header

def unpack_header_tcp(header: bytes) -> (int, X25519PublicKey):
    # Returns:
    # - [int] message length
    # - [X25519PublicKey] DHratchet_public_key_alice
    msg_length = int.from_bytes(bytes=header[0:4], byteorder='big')
    pubkey_bytes = header[4:header_length]
    pubkey = deserialize_public_key(pubkey_bytes)
    return (msg_length, pubkey)


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