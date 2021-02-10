from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.backends import default_backend


""" Uncomment these dependencies in case of need
workingDirectory = os.path.abspath(os.path.dirname(__file__))
eventCreationToolPath = os.path.join(workingDirectory, '../../../../groups/04-logMerge/eventCreationTool')
sys.path.append(eventCreationToolPath)
DBsrcPath = os.path.join(workingDirectory, '../../../../groups/07-14-logCtrl/src')
sys.path.append(DBsrcPath)
"""

import cbor2
from logStore.funcs.EventCreationTool import EventFactory


from Crypto.Cipher import AES

import base64

header_length = 44

class SymmRatchet(object):
    def __init__(self, key):
        self.state = key

    def next(self, inp=b''):
        # turn the ratchet, changing the state and yielding a new key and IV
        output = hkdf(self.state + inp, 80)
        self.state = output[:32]
        outkey, iv = output[32:64], output[64:]
        return outkey, iv


def encapsulate_message_tcp(person: object, message: str) -> bytes:
    #print("Sending:", message)
    (cipher_text, dh_ratchet_public_key) = encrypt_msg(person, message)
    header = create_header_tcp(cipher_text, person.Ns, person.PNs, dh_ratchet_public_key)
    return b''.join([header, cipher_text])


def expose_message_tcp(message, person: object) -> str:
    # received_message = conn.recv(buffer_size, 0x40)
    #received_message = socket.recv(header_length)
    header_bytes = message[:header_length]
    msg_length, N, PN, DHratchet_public_key_alice = unpack_header_tcp(header_bytes)
    #print("N:", N)
    #print("PN:", PN)
    #cipher_text_received = socket.recv(msg_length)
    cipher_text_received = message[header_length:header_length+msg_length]
    received_message_text = decrypt_msg(person, cipher_text_received, DHratchet_public_key_alice)
    assert len(message) == header_length + msg_length
    return received_message_text

def encrypt_msg(person: object, msg: str) -> (bytes, bytes):
    # Encrypts the message.
    # Returns the ciphertext and the next DHratchet public key.
    msg = msg.encode('utf-8')
    key, iv = person.send_ratchet.next()
    #print("send ratchet N was:", person.Ns)
    person.Ns += 1
    #print("send ratchet N is:", person.Ns)
    cipher = AES.new(key, AES.MODE_CBC, iv).encrypt(pad(msg))
    save_status(person)
    return cipher, serialize_public_key(person.DHratchet.public_key())

prev_pubkey = None

def create_msg_event(person: object, msg: str) -> (bytes):
    return NotImplementedError


def send_BACnet():
    return NotImplementedError

prev_pubkey = None

def decrypt_msg(person: object, cipher: bytes, public_key) -> str:
    global prev_pubkey

    # receive Alice's new public key and use it to perform a DH
    #person.Nr += 1
    #print("recv N:", person.Nr)
    #print("recv PN:", person.PNr)
    #print("send N:", person.Ns)
    #print("send PN:", person.PNs)
    if prev_pubkey != serialize_public_key(public_key):
        dh_ratchet(person, public_key)
    prev_pubkey = serialize_public_key(public_key)
    key, iv = person.recv_ratchet.next()
    # decrypt the message using the new recv ratchet
    msg = unpad(AES.new(key, AES.MODE_CBC, iv).decrypt(cipher))
    msg = msg.decode('utf-8')
    # print('[Bob]\tDecrypted message:', msg)
    return msg

def dh_ratchet(person, public_key):
    # perform a DH ratchet rotation using received public key
    if person.DHratchet is not None:
        # the first time we don't have a DH ratchet yet
        dh_recv = person.DHratchet.exchange(public_key)
        shared_recv = person.root_ratchet.next(dh_recv)[0]
        # use Bob's public and our old private key
        # to get a new recv ratchet
        person.recv_ratchet = SymmRatchet(shared_recv)
        # print('[Alice]\tRecv ratchet seed:', b64(shared_recv))
    # generate a new key pair and send ratchet
    # our new public key will be sent with the next message to Bob
    person.DHratchet = X25519PrivateKey.generate()
    dh_send = person.DHratchet.exchange(public_key)
    shared_send = person.root_ratchet.next(dh_send)[0]
    person.send_ratchet = SymmRatchet(shared_send)
    person.PNs = person.Ns
    person.Ns = 0
    # print('[Alice]\tSend ratchet seed:', b64(shared_send))

def create_header_tcp(cipher_text, N, PN, DHratchet_public_key) -> bytes:
    # header of message, defined by
    # length || PN || N || DHratchet_public_key
    # 4 bytes || 4 bytes || 4 bytes || 32 bytes

    header = b''.join([len(cipher_text).to_bytes(length=4, byteorder='big'),
                       N.to_bytes(length=4, byteorder='big'),
                       PN.to_bytes(length=4, byteorder='big'),
                       DHratchet_public_key])
    assert(len(header) == header_length)
    #print(f"Created header: [{len(cipher_text)}, {N}, {PN}, {b64(DHratchet_public_key)}]")
    return header

def unpack_header_tcp(header: bytes) -> (int, X25519PublicKey):
    # Returns:
    # - [int] message length
    # - [int] N (message number)
    # - [int] PN (messages in last chain)
    # - [X25519PublicKey] DHratchet_public_key_alice
    msg_length = int.from_bytes(bytes=header[0:4], byteorder='big')
    N = int.from_bytes(bytes=header[4:8], byteorder='big')
    PN = int.from_bytes(bytes=header[8:12], byteorder='big')
    pubkey_bytes = header[12:header_length]
    pubkey = deserialize_public_key(pubkey_bytes)
    #print(f"Unpacked header: [{msg_length}, {N}, {PN}, {b64(pubkey_bytes)}]")
    return (msg_length, N, PN, pubkey)


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

def save_status(person):
    # 1. Find occurence and delete it
    try:
        with open(person.backup_path, 'rb') as f:
            all = f.read()
        k = 0
        all_updated = None
        while True:
            identifier_length = int.from_bytes(all[k:k + 4], 'big')
            if all[k + 4:k + 4 + identifier_length] == bytes(person.identifier_other, 'utf-8'):
                all_updated = all[:k] + all[k + 4 + identifier_length + 692:]
                break
            elif all[k + 4:k + 4 + identifier_length] == b'':
                break

            k += 4 + identifier_length + 692

        if all_updated != None:
            with open(person.backup_path, 'wb') as f:
                f.write(all_updated)
    except FileNotFoundError:
        pass

    # 2. Save state
    print("save status.")
    bytes_to_save = b''.join(
        [len(bytes(person.identifier_other, encoding='utf-8')).to_bytes(4, 'big'),  # 4
         bytes(person.identifier_other, encoding='utf-8'),  # ?
         person.Ns.to_bytes(4, 'big'),  # 4
         person.Nr.to_bytes(4, 'big'),  # 4
         person.PNs.to_bytes(4, 'big'),  # 4
         person.PNr.to_bytes(4, 'big'),  # 4
         serialize_private_key(person.DHratchet),  # 290
         serialize_private_key(person.IK),  # 290
         person.send_ratchet.state,  # 32
         person.recv_ratchet.state,  # 32
         person.root_ratchet.state]  # 32
    )
    with open(person.backup_path, 'ab') as f:
        f.write(bytes_to_save)
    pass


def load_status(person, path):
    with open(path, 'rb') as f:
        all = f.read()
    k = 0
    keys = None
    while True:
        identifier_length = int.from_bytes(all[k:k + 4], 'big')
        if all[k + 4:k + 4 + identifier_length] == bytes(person.identifier_other, 'utf-8'):
            keys = all[k + 4 + identifier_length:k + 4 + identifier_length + 692]
            break
        elif all[k + 4:k + 4 + identifier_length] == b'':
            print("Something went wrong. Cannot find saved keys for this person. Shutting down...")
            exit()

        k += 4 + identifier_length + 692

    person.Ns = int.from_bytes(keys[0:4], 'big')
    person.Nr = int.from_bytes(keys[4:8], 'big')
    person.PNs = int.from_bytes(keys[8:12], 'big')
    person.PNr = int.from_bytes(keys[12:16], 'big')
    person.DHratchet = deserialize_private_key(keys[16:16 + 290])
    person.IK = deserialize_private_key(keys[16 + 290:16 + 2 * 290])
    person.send_ratchet = SymmRatchet(keys[596:596 + 32])
    person.recv_ratchet = SymmRatchet(keys[596 + 32:596 + 2 * 32])
    person.root_ratchet = SymmRatchet(keys[596 + 2 * 32:596 + 3 * 32])

def serialize_public_key(public_key: X25519PublicKey) -> bytes:
    return public_key.public_bytes(encoding=serialization.Encoding.Raw,
                                   format=serialization.PublicFormat.Raw)
def deserialize_public_key(public_bytes) -> X25519PublicKey:
    return X25519PublicKey.from_public_bytes(public_bytes)


def serialize_private_key_raw(private_key: X25519PrivateKey) -> bytes:
    return private_key.private_bytes(encoding=serialization.Encoding.Raw,
                                     format=serialization.PrivateFormat.Raw,
                                     encryption_algorithm=serialization.NoEncryption())

def serialize_private_key(private_key: X25519PrivateKey) -> bytes:
    # Takes a X25519PrivateKey object and returns a bytestring representing this key.
    return private_key.private_bytes(encoding=serialization.Encoding.PEM,
                                     format=serialization.PrivateFormat.PKCS8,
                                     encryption_algorithm=serialization.BestAvailableEncryption(b'pw'))

def deserialize_private_key(private_bytes) -> X25519PrivateKey:
    return X25519PrivateKey.from_private_bytes(private_bytes)

    # Takes a bytestring and returns the corresponding X25519PrivateKey object.
    loaded_key = serialization.load_pem_private_key(data=private_bytes,
                                                    password=b'pw',
                                                    backend=default_backend())
    return loaded_key


