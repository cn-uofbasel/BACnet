import socket
import select
import sys
import base64

### I USED 'pip install pycryptodome', instead of 'pip3 install cryptography==2.8 pycrypto',
### because pycrypto didn't work to install.
### This is a fork, so it might have security bugs.
### Got the tip from https://stackoverflow.com/a/54142469

# Some of the following is copied from:
# https://nfil.dev/coding/encryption/python/double-ratchet-example/

# Requirements:
# apt install python3 python3-pip
# pip3 install cryptography==2.8 pycrypto

from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey
from cryptography.hazmat.primitives.asymmetric.ed25519 import \
        Ed25519PublicKey, Ed25519PrivateKey
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
from cryptography.hazmat.backends import default_backend
from Crypto.Cipher import AES

"""
In this program:
1. User chooses whether he wants to be Alice(1) or Bob(2)
2. If User is Alice, User creates:
    -Alice object
   If User is Bob,


- Alice performs x3dh:
    -> Bob.IK, Bob.SPKb, Bob.OBKb
    <- self.sk

- Bob performs x3dh:
    -> Alice.IKa, Alice.EKa
    <- self.sk


"""


buffer = 1024   # The max buffer size of one packet to be sent by the server.
ip_address = ''
port = 0

def main():
    local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Created the datagram socket
    try:
        local_sock.settimeout(1) # Sets the socket to timeout after 1 second of no activity
        local_sock.connect((ip_address, port)) #tries to connect with the parameters
        is_server = False                      #if it connects there is already a server and a client is started
    except socket.error:
        print('Could not connect, the other user is not yet here')
        is_server = True                    #if the connection fails, a server is started
        local_sock.close()
        try:
            start_server() #Bob is the server and has to start the program first
        except OSError:
            print('This port is already in use, try another one')
            return
    if not is_server:
        start_client(local_sock)  #Alice is the cleint and has to start the program first


def start_client(local_sock):
    inputs = [local_sock, sys.stdin]    # Array of all input select has to look for
    # (standard input and socket, does not work on windows)
    print('Successfully connected to other user.')  #message to the client that the connection worked

    running = True
    sentKeys = False
    while running:
        try:
            in_rec, out_rec, ex_rec = select.select(inputs, [], [])  # Let select save all the incoming input to in_rec
        except KeyboardInterrupt:       # Catch Interrupts which happen if one shuts down the program forcefully
            print('Closed the connection')
            local_sock.send('quit'.encode('UTF8')) #sends the message to the server that the client socket closes
            break
        for msgs in in_rec:  # Work up all the received messages saved in in_rec
            if msgs is local_sock:  # Case message is from socket
                try:
                    new_message = local_sock.recv(buffer)
                    if 'quit' == new_message.decode().rstrip():     #see if it is a quit message
                        print('Connection closed by other user')
                        running = False
                        return
                    print(new_message.decode().rstrip()) #outputs the message
                except socket.error:
                    print('Could not read from socket')
                    running = False
                    return
            if
            elif msgs is sys.stdin:     # case message is from standard input
                line = sys.stdin.readline()             #reads the messages from the client
                local_sock.send(line.encode('UTF-8'))   #sends the messages from the client
            else:
                break
    local_sock.close()   # Close the socket if while is left


def start_server():
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)         # Created the datagram socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)        #checks your own ip address
    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    port = 0
    server_sock.bind((ip_address, port))    # bind it to the wished ip and some port
    server_sock.listen(1)                   #connection to only one client
    print('server started with: ip {} port {}'.format(server_sock.getsockname()[0], server_sock.getsockname()[1]))
    #outputs the local ip and port
    try:
        conn, addr = server_sock.accept()   #Wait for a connection to the client
    except KeyboardInterrupt:
        return 1
    print('Other user arrived. Connection address:', addr)  #prints the ip and port of the clients

    inputs = [conn, sys.stdin]  # Array of all input select has to look for

    running = True
    receivedKeyPair = False
    while running:
        try:
            in_rec, out_rec, ex_rec = select.select(inputs, [], [])     # Try to receive input from the socket
            # and save it in in_rec
        except KeyboardInterrupt:       # Catch Interrupts which happen if one shuts down the program forcefully
            print('Closed the connection')
            conn.send('quit'.encode('UTF8'))
            break
        for msgs in in_rec:         # Work up all the received messages saved in in_rec
            if msgs is conn:
                try:
                    new_message = conn.recv(buffer)         #reads the incoming messages
                    if 'quit' == new_message.decode().rstrip():
                        print('Connection closed by other user')
                        running = False
                        return
                    print(new_message.decode().rstrip())    #prints the messages
                except socket.error:
                    print('Could not read from socket')
                    running = False
                    return
            elif msgs is sys.stdin:
                line = sys.stdin.readline()         #reads the messages from the server
                conn.send(line.encode('utf-8'))     #sends the messages
            else:
                break
    server_sock.close()         # Close the socket if while is left

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

class SymmRatchet(object):
    def __init__(self, key):
        self.state = key

    def next(self, inp=b''):
        # turn the ratchet, changing the state and yielding a new key and IV
        output = hkdf(self.state + inp, 80)
        self.state = output[:32]
        outkey, iv = output[32:64], output[64:]
        return outkey, iv


def serialize_public_key(public_key: X25519PublicKey):
    return public_key.public_bytes(encoding = serialization.Encoding.Raw, format = serialization.PublicFormat.Raw)

def deserialize_public_key(public_bytes) -> X25519PublicKey:
    return X25519PublicKey.from_public_bytes(public_bytes)

# 1. Bob creates 3 keys
# 2. Bob sends 3 keys via clear net
# 3. Alice makes x3dh with received keys
# 4. Alice now has shared key. init_ratchets
# 5. Alice creates 2 keys.
# 6. Alice sends 2 keys via clear net
# 7. Bob makes x3dh with received keys.
# 8. Bob now has shared key. init_ratchets


class Bob(object):
    def __init__(self):
        # generate Bob's keys
        self.IKb = X25519PrivateKey.generate()
        self.SPKb = X25519PrivateKey.generate()
        self.OPKb = X25519PrivateKey.generate()

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
        # initialise the root chain with the shared key
        self.root_ratchet = SymmRatchet(self.sk)
        # initialise the sending and recving chains
        self.recv_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        self.send_ratchet = SymmRatchet(self.root_ratchet.next()[0])
        # initialise Bob's DH ratchet
        self.DHratchet = X25519PrivateKey.generate()

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
        self.IKa = X25519PrivateKey.generate()
        self.EKa = X25519PrivateKey.generate()
        public_bytes_alice_IKa = serialize_public_key(self.IKa.public_key())
        print('original key, serialized:', public_bytes_alice_IKa)

        IKa_copy = deserialize_public_key(public_bytes_alice_IKa)
        public_bytes_alice_IKa_copy = serialize_public_key(IKa_copy)
        print('copy of key,  serialized:', public_bytes_alice_IKa_copy)

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


if __name__ == '__main__':

    ip_address = sys.argv[1]        #takes over the parameters
    port = int(sys.argv[2])

    role = int(input("Do you want to initialize[1] or be contacted[2]?"))
    if role == 1:
        alice = Alice()
        bob = Bob()
        role = alice
        alice.x3dh(bob)
        alice.init_ratchets()
        alice.dh_ratchet(bob.DHratchet.public_key())
    else:
        bob = Bob()
        alice = Alice()
        role = bob

    main()





    bob.x3dh(alice)


    # Bob comes online and performs an X3DH using Alice's public keys
    bob.x3dh(alice)

    # Initialize their symmetric ratchets
    bob.init_ratchets()

    # Initialise Alice's sending ratchet with Bob's public key
    alice.dh_ratchet(bob.DHratchet.public_key())

    # Alice sends Bob a message and her new DH ratchet public key
    alice.send(bob, b'Hello Bob!')

    # Bob uses that information to sync with Alice and send her a message
    bob.send(alice, b'Hello to you too, Alice!')



"""
- 1. Every person has a single feed
- 2.
-

    vent data structure (="log entry") in grammar form and as ASCII art:

  +-event------------------------------------------------------------------+
  | +-meta---------------------------------------+                         |
  | | feed_id, seq_no, h_prev, sign_info, h_cont |, signature, opt_content |
  | +--------------------------------------------+                         |
  +------------------------------------------------------------------------+

  event :== _cbor( [ meta, signature, opt_content ] )                           =

  meta  :== _cbor( [ feed_id, seq_no, h_prev, sign_info, h_cont ] )             =

  h_prev         :== [hash_info, "hash value of prev event's meta field"]       =
  signature      :== "signature of meta"                                        =
  h_cont         :== [hash_info, "hash value of opt_content"]

  sign_info:     enum (0=ed25519)                                               =
  hash_info:     enum (0=sha256)                                                =

  opt_content    :== _cbor( data )                                              =

  """
