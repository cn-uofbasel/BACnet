from cryptography.hazmat.primitives.asymmetric.x25519 import X25519PrivateKey, X25519PublicKey

from helpers import serialize_public_key, deserialize_public_key
from helpers import serialize_private_key, deserialize_private_key
from helpers import b64, create_header_tcp, unpack_header_tcp
from helpers import header_length

from alice import Alice
from bob import Bob

import socket
import select
import sys


# Requirements:
# apt install python3 python3-pip
# pip3 install cryptography==2.8 pycrypto
### On windows you might want to use 'pip install pycryptodome', instead of 'pip3 install cryptography==2.8 pycrypto',
### because pycrypto might not work to install. This is a fork, so it might have security bugs.
### Got the tip from https://stackoverflow.com/a/54142469
# Some of the following is copied from: https://nfil.dev/coding/encryption/python/double-ratchet-example/


'''
# We need these dependencies to be able to work with logs:
workingDirectory = os.path.abspath(os.path.dirname(__file__)
eventCreationToolPath = os.path.join(dirname, '../../../../04-logMerge/eventCreationTool')
sys.path.append(eventCreationToolPath)
DBsrcPath = os.path.join(dirname, '../../../../07-14-logCtrl/src')
sys.path.append(DBsrcPath)

import cbor2
import pynacl
import EventCreationTool
from logStore.transconn.database_connector import DatabaseConnector
from logStore.funcs.event import Event, Meta, Content
from logStore.appconn.chat_connection import ChatFunction
'''

#Program steps when sending and receiving logs:
#   0. Detect log storage and read logs
#        - If no log storage or feed currently exists, create it
#        - load own keys from storage
#        <-
#
#   1a. Prompt if user wants to establish a new Chat (be Alice) with Bob or
#   1b. continue/read one of the old chats and/or wait for new messages (be Bob)
#
#   2a. Prompt which user from her contacts she wants to contact or
#       (Bonus extra functionality) propagate the log message, that she wants to contact info of a certain userAlias
#   2b. Extract all the chats from your logs and display them in the browser, for Bob to pick one to be displayed
#   3a. Alice picks the userAlies and then extracts his public key, signed prekey
#   3b. Bob can send a message:
#        - type message
#        - create_message_event()
#        - send_message_event() / send() [Former allows for other functions i.e. send_contact_info()]
#
#   4a. Alices does:
#       - x3dh()
#           -> Bob.IK, Bob.SPKb, Bob.OBKb
#           <- self.sk
#       - init_ratchets()
#       - dh_ratchet()
#
#   4bI. Bob can receive a message from an existing chat,
#        - he reads the new log
#        - he loads the log_message_pkg
#        - he determines
#   4bII. or a new initial message from Alice
#
#   5a.
#   5b.
#

buffer_size = 1024   # The max buffer size of one packet to be sent by the server. Should be higher for our use case?
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
        start_client(local_sock)  #Alice is the client and has to start the program first


def start_client(local_sock):  ## Alice
    inputs = [local_sock, sys.stdin]    # Array of all input select has to look for
    # (standard input and socket, does not work on windows)
    print('Successfully connected to other user.')  #message to the client that the connection worked

    alice = Alice()
    alice.alice_x3dh_over_tcp(socket=local_sock)


    (cipher_text, alice_dh_ratchet_public_key) = alice.encrypt_msg("Hello, Bob!")
    print("[Alice] Message: 'Hello, Bob!'")
    print("[Alice] cipher_text length:", len(cipher_text))
    print("[Alice] cipher_text:", cipher_text)
    print("[Alice] dh_ratchet_pubkey:", alice_dh_ratchet_public_key)
    header = create_header_tcp(cipher_text, alice_dh_ratchet_public_key)
    print("[Alice] headerlength:", len(header))
    print("[Alice] header:", header)
    local_sock.send(b''.join([header, cipher_text]))
    print("[Alice] Sent first message. Ready for user input.")


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
                    new_message = local_sock.recv(buffer_size)
                    if 'quit' == new_message.decode().rstrip():     #see if it is a quit message
                        print('Connection closed by other user')
                        running = False
                        return
                    #We read message event pkg
                    #We extract the
                    #We decipher the message
                    print(new_message.decode().rstrip()) #outputs the message
                except socket.error:
                    print('Could not read from socket')
                    running = False
                    return
            elif msgs is sys.stdin:     # case message is from standard input
                line = sys.stdin.readline()             #reads the messages from the client
                #Create message event to be sent
                #Send message event
                local_sock.send(line.encode('UTF-8'))   #sends the messages from the client
            else:
                break
    local_sock.close()   # Close the socket if while is left


def start_server():  ## Bob
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

    bob = Bob()
    bob.bob_x3dh_over_tcp(socket=conn)


    #received_message = conn.recv(buffer_size, 0x40)
    received_message = conn.recv(header_length)
    msg_length, DHratchet_public_key_alice = unpack_header_tcp(received_message)
    print("[Bob] received message:", received_message)
    print("[Bob] msg_length:", msg_length)
    cipher_text_received = conn.recv(msg_length)
    received_message_text = bob.decrypt_msg(cipher_text_received, DHratchet_public_key_alice)
    print("[Bob] received msg:", received_message_text)
    print("[Bob]: msg finished")

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
                    new_message = conn.recv(buffer_size)         #reads the incoming messages
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



# 1. Bob creates 4 keys: IKb, SPKb, OPKb, DHratchet_seed
# (I think this is wrong,
# but I don't know how to let Alice know Bob's DHratchet_seed in any other way...)
#
# 2. Bob sends 4 keys via clear net
# 3. Alice makes x3dh with received keys
# 4. Alice now has shared key. init_ratchets
# 5. Alice creates 3 keys IKa, EKa, DHratchet_seed. (Same as above, this is wrong)
# 6. Alice sends 2 keys via clear net.
# 7. Bob makes x3dh with received keys.
# 8. Bob now has shared key. init_ratchets
#10. Alice initializes dh_ratchet with bob public key


if __name__ == '__main__':
    ip_address = sys.argv[1]        #takes over the parameters
    port = int(sys.argv[2])
    '''
    chat_function = ChatFunction()
    current_event = chat_function.get_current_event(chat_function.get_all_feed_ids()[1])  # Test what happens with [0]
    event_factory = EventCreationTool.EventFactory()
    # feedIDs = event_factory.get_own_feed_ids(True) #what's the difference to get_stored_feed_ids(cls, directory_path=None, relative=True, as_strings=False)?
    master_id = chat_function.get_host_master_id()
    if not currentEvent:
        # WTF do I do now?
        feedExists = False
    else:
        first_event = EventFactory.first_event('chat', chat_function.get_host_master_id())
        chat_function.insert_event(first_event)
    '''
    """
    # Set EventFactory
        x = self.chat_function.get_current_event(self.chat_function.get_all_feed_ids()[1])
        most_recent_event = self.chat_function.get_current_event(self.feed_id)
        self.ecf = EventCreationTool.EventFactory(most_recent_event)  # damit wieder gleiche Id benutzt wird
    """


    #Later on, if feedExsists is false,
    #we create an initial event in a new feed and store our identity event in the

    """"
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
    """

    main()





    #bob.x3dh(alice)


    # Bob comes online and performs an X3DH using Alice's public keys
    #bob.x3dh(alice)

    # Initialize their symmetric ratchets
    #bob.init_ratchets()

    # Initialize Alice's sending ratchet with Bob's public key
    #alice.dh_ratchet(bob.DHratchet.public_key())

    # Alice sends Bob a message and her new DH ratchet public key
    #alice.send(bob, b'Hello Bob!')

    # Bob uses that information to sync with Alice and send her a message
    #bob.send(alice, b'Hello to you too, Alice!')



"""
- 1. Every person has a master feed
- 2. When executing a program, a new feed is created, which is linked to the master feed
    every chat could have its own feed, this is not sure yet
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

  opt_content    :== _cbor( data )                                              = ['ratchat/message', {'ciphertext': "EaIWPzFSaImapGnYahNFwteCcB4ZCMOka6zRBJZ+KvE=",
                                                                                   'chatID': '5b60d1ff04d8958917d7eab32b...',
                                                                                   'sequnceNumber': '3'
                                                                                   'timestamp': 1585201899}]
                                                                                   or
                                                                                   ['ratchat/connect', {'public_key': "b'g\x1b\x0f\xfb\x00\xa7\xc5!}\xaa\xa2\xa9\xc2p\xbe\x84g\xe1\xeb\x06\xea\xb4\xa4\xb3\xe2M\x1a\xa71\r\x8c5",
                                                                                    'ephemeral_key': '5b60d1ff04d8958917d7eab32b...',
                                                                                    'timestamp': 1585201888}]
                                                                                   or
                                                                                   ['ratchat/contactInfo':{'userAlias': "cantonesePorkBun",
                                                                                    'public_iden_key': "b'g\x1b\x0f\xfb\x00\xa7\xc5!}\xaa\xa2\xa9\xc2p\xbe\x84g\xe1\xeb\x06\xea\xb4\xa4\xb3\xe2M\x1a\xa71\r\x8c5",
                                                                                    'signed_prekey': '5b60d1ff04d8958917d7eab32b...',
                                                                                    'timestamp': 1585201888}]
                                                                                   or
                                                                                   ['ratchat/identity':{'private_iden_key': xxxx,
                                                                                    'signed_prekey':xxx}]


  """
