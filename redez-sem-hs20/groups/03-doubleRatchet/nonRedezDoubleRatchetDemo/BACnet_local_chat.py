from helpers import encapsulate_message_tcp, expose_message_tcp

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

# Program steps when sending and receiving logs:
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

# import time
import os
from logStore.appconn.ratchet_chat_connection import RatchetChatFunction
from logStore.appconn.connection import Function
from logStore.funcs.EventCreationTool import EventFactory
from logStore.funcs.EventCreationTool import EventCreationTool
from logStore.funcs.event import Event, Meta, Content
import datetime
path_msg = os.getcwd() + '/message.txt'


def send_msg_local(msg: bytes):
    with open(path_msg, 'wb') as f:
        f.write(msg)
    pass


def send_Bacnet_msg(msg, feed_id_from_partner, own_feed_id):
    timestamp = datetime.datetime.now()
    new_event = ecf.next_event('ratchet/message', {'ciphertext': msg,
                                                    'own_feedID': own_feed_id,
                                                    'feedID_from_partner': feed_id_from_partner,
                                                    'chat_id': 1,
                                                    'sequenceNumber': 3,
                                                    'lastSequenceNumber': 5,
                                                    'timestamp': str(timestamp)})
    cf.insert_event(new_event)

def send_Bacnet_identifier(feed_id: bytes):
    pass

def send_second_Bacnet_prekey_bundle( key_bundle, own_feed_id, feed_id_from_partner):
    timestamp = datetime.datetime.now()
    new_event = ecf.next_event('ratchet/connect', {'key_bundle': key_bundle,
                                                   'own_feedID': own_feed_id,
                                                   'feedID_from_partner': feed_id_from_partner,
                                                   'chat_id': 1,
                                                    'sequenceNumber': 3,
                                                    'lastSequenceNumber': 5,
                                                    'timestamp': str(timestamp)})
    cf.insert_event(new_event)

def send_first_Bacnet_prekey_bundle(own_feed_id, key_bundle):
    timestamp = datetime.datetime.now()
    new_event = ecf.next_event('ratchet/contactInfo', {'key_bundle': key_bundle,
                                                       'own_feedID': own_feed_id,
                                                       'feedID_from_partner': '',
                                                       'timestamp': str(timestamp),
                                                       'chat_id': 1,
                                                       'sequenceNumber': 3,
                                                       'lastSequenceNumber': 5})
    cf.insert_event(new_event)

def retrieve_msg_local() -> bytes:
    message = None
    with open(path_msg, 'rb') as f:
        message = f.read()
    os.remove(path_msg)
    return message


buffer_size = 1024  # The max buffer size of one packet to be sent by the server. Should be higher for our use case?
ip_address = ''
port = 0
cf = RatchetChatFunction()
function = Function()

try:
    os.mkdir(os.getcwd() + '/public_key')
except FileExistsError:
    pass
if not EventCreationTool().get_stored_feed_ids(directory_path=os.getcwd() + '/public_key'):
    ecf = EventFactory(path_to_keys=os.getcwd() + '/public_key')
    #print('new feed generated')
    #print('feed_id: ,', ecf.get_feed_id())

else:
    start_feed_id = EventCreationTool().get_stored_feed_ids(directory_path=os.getcwd() + '/public_key')
    current_event = function.get_current_event(feed_id=start_feed_id[0])
    ecf = EventFactory(path_to_keys=os.getcwd() + '/public_key', last_event=current_event)
    #print('use old feed')


def main(role: str):
    if role == 'Alice':
        start_client()
    elif role == 'Bob':
        start_server()
    '''
    local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    # Created the datagram socket
    try:
        local_sock.settimeout(1)  # Sets the socket to timeout after 1 second of no activity
        local_sock.connect((ip_address, port))  # tries to connect with the parameters
        is_server = False  # if it connects there is already a server and a client is started
    except socket.error:
        print('Could not connect, the other user is not yet here')
        is_server = True  # if the connection fails, a server is started
        local_sock.close()
        try:
            start_server()  # Bob is the server and has to start the program first
        except OSError:
            print('This port is already in use, try another one')
            return
    if not is_server:
        start_client(local_sock)  # Alice is the client and has to start the program after Bob.
    '''


def start_client():  ## Alice
    #inputs = [sys.stdin]  # Array of all input select has to look for
    # (standard input and socket, does not work on windows)
    print('Successfully connected to other user.')  # message to the client that the connection worked

    print("I AM ALICE")
    alice = Alice(identifier_other='Bob')
    print("X3DH status:", alice.x3dh_status)
    event_list = cf.get_all_saved_events(1)
    #print('len(event_list):', len(event_list))
    content = None
    if len(event_list) > 0:
        last_event = event_list[-1]
        content, meta = last_event
        feed_id = Meta.from_cbor(meta).feed_id

    if content[0] == 'ratchet/contactInfo':
        if alice.x3dh_status == 0:
            # received_keys = local_sock.recv(224)
            #received_keys = retrieve_msg_local()
            key_bundle_to_send = alice.x3dh_create_key_bundle_from_received_key_bundle(content[1]['key_bundle'])
            # local_sock.send(key_bundle_to_send)
            #send_msg_local(key_bundle_to_send)
            #print('befor send to send:', (key_bundle_to_send, ecf.get_feed_id(), feed_id))
            send_second_Bacnet_prekey_bundle(key_bundle_to_send, ecf.get_feed_id(), feed_id)

    """if content[0] == 'ratchet/message' or content[0] == 'ratchet/connect':
        if alice.x3dh_status == 2:
            print('in ratchet/message loop')
            #received_message_raw = retrieve_msg_local()
            #try:"""
    if ecf.get_feed_id() != feed_id:
        own_last_event_sequence_number = function.get_current_seq_no(ecf.get_feed_id())

        own_last_event = Event.from_cbor(function.get_event(ecf.get_feed_id(), own_last_event_sequence_number))
        last_own_message_not_reached = True
        for x in event_list:

            if x[0][0] != 'ratchet/message':
                continue
            if last_own_message_not_reached:
                if x[0][1]['ciphertext'] == own_last_event.content.content[1]['ciphertext']:
                    last_own_message_not_reached = False
                    continue

                continue

            #print(x[0][1]['ciphertext'])
            received_message_raw = expose_message_tcp(x[0][1]['ciphertext'], alice)
            print("Received:", received_message_raw)

    while True:
        try:
            msg = input('Please enter your message: ')
            send_Bacnet_msg(encapsulate_message_tcp(alice, msg), feed_id, ecf.get_feed_id())
        except KeyboardInterrupt:
            print('Interrupted')


    # msg_to_bob = 'Hello, Bob!'
    # send_tcp(socket=local_sock, person=alice, message=msg_to_bob)
    # print("[Alice] sent:", msg_to_bob)
    # print("[Alice] received:", recv_tcp(socket=local_sock, person=alice))

    running = True
    sentKeys = False
    print("ok.. finished.")
    '''
    while running:
        try:
            in_rec, out_rec, ex_rec = select.select(inputs, [], [])  # Let select save all the incoming input to in_rec
        except KeyboardInterrupt:  # Catch Interrupts which happen if one shuts down the program forcefully
            print('Closed the connection')
            local_sock.send('quit'.encode('UTF8'))  # sends the message to the server that the client socket closes
            break
        
        for msgs in in_rec:  # Work up all the received messages saved in in_rec
            if msgs is local_sock:  # Case message is from socket
                try:
                    new_message = local_sock.recv(buffer_size)
                    try:
                        msg = new_message.decode()
                        if 'quit' == msg:  # see if it is a quit message
                            print('Connection closed by other user')
                            running = False
                            return
                    except UnicodeDecodeError:
                        pass
                    # We read message event pkg
                    # We extract the
                    # We decipher the message
                    # message = recv_tcp(socket=local_sock, person=alice)
                    message = expose_message_tcp(message=new_message, person=alice)
                    print('[Alice]: received:', message)  # outputs the message
                except socket.error:
                    print('Could not read from socket')
                    running = False
                    return
            elif msgs is sys.stdin:  # case message is from standard input
                line = sys.stdin.readline().rstrip()  # reads the messages from the client
                # Create message event to be sent
                # Send message event
                bytes_to_send = encapsulate_message_tcp(person=alice,
                                                        message=line)  # sends the messages from the client
                local_sock.send(bytes_to_send)
            else:
                break
    local_sock.close()  # Close the socket if while is left
    '''


def start_server():  ## Bob
    '''
    server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # Created the datagram socket
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)  # checks your own ip address

    s.connect(("8.8.8.8", 80))
    ip_address = s.getsockname()[0]
    port = 0
    server_sock.bind((ip_address, port))  # bind it to the wished ip and some port
    server_sock.listen(1)  # connection to only one client
    print('server started with: ip {} port {}'.format(server_sock.getsockname()[0], server_sock.getsockname()[1]))
    # outputs the local ip and port
    try:
        conn, addr = server_sock.accept()  # Wait for a connection to the client
    except KeyboardInterrupt:
        return 1
    print('Other user arrived. Connection address:', addr)  # prints the ip and port of the clients
    '''

    print("I AM BOB")
    bob = Bob(identifier_other='Alice')
    print("Status:", bob.x3dh_status)
    event_list = cf.get_all_saved_events(1)

    if len(event_list) > 0:
        last_event = event_list[-1]
        content, meta = last_event
        feed_id = Meta.from_cbor(meta).feed_id

    if bob.x3dh_status == 0:
        prekey_bundle = bob.x3dh_1_create_prekey_bundle()
        # TODO (identifier_other comes from bacnet): save_prekeys(prekey_bundle, identifier_other)
        # conn.send(prekey_bundle)
        #send_msg_local(prekey_bundle)
        send_first_Bacnet_prekey_bundle(ecf.get_feed_id(), prekey_bundle)
        exit()

    if event_list[1][0][0] == 'ratchet/connect' and bob.x3dh_status == 1:
        if bob.x3dh_status == 1:
            # alice_key_bundle = conn.recv(64)
            #alice_key_bundle = retrieve_msg_local()
            #print("LEN:", len(alice_key_bundle))
            #print("keybundle:", alice_key_bundle)
            # TODO: delete_prekeys(identifier_other)

            #print(event_list[1][0][1]['key_bundle'])
            bob.x3dh_2_complete_transaction_with_alice_keys(event_list[1][0][1]['key_bundle'])

            print("Waiting for an initial message from alice...")

            bob.x3dh_status = 2
            #print(bob.x3dh_status)


    if content[0] == 'ratchet/message' or content[0] == 'ratchet/connect':
        if bob.x3dh_status == 2:

            #received_message_raw = retrieve_msg_local()

            if ecf.get_feed_id() != feed_id:
                own_last_event_sequence_number = function.get_current_seq_no(ecf.get_feed_id())

                own_last_event = Event.from_cbor(function.get_event(ecf.get_feed_id(), own_last_event_sequence_number))
                last_own_message_not_reached = True
                for x in event_list:

                    if own_last_event.content.content[0] == 'ratchet/contactInfo':
                        if x[0][0] != 'ratchet/message':
                            last_own_message_not_reached = False
                            continue

                    elif own_last_event.content.content[0] == 'ratchet/message':
                        if x[0][0] != 'ratchet/message':
                            continue
                    if last_own_message_not_reached:
                        if x[0][1]['ciphertext'] == own_last_event.content.content[1]['ciphertext']:
                            last_own_message_not_reached = False
                            continue

                        continue


                    #print('print msg')
                    received_message_raw = expose_message_tcp(x[0][1]['ciphertext'], bob)
                    print("Received:", received_message_raw)


                #received_message_raw = expose_message_tcp(content[1]['ciphertext'], bob)
                #print("Received:", received_message_raw)

            else:
                print('no new messages')

            while True:
                try:
                    msg = input('Please enter your message: ')
                    send_Bacnet_msg(encapsulate_message_tcp(bob, msg), feed_id, ecf.get_feed_id())
                except KeyboardInterrupt:
                    print ('Interrupted')
                    sys.exit(0)

    #  recvd_message = conn.recv(buffer_size)
    #  print("[Bob] received:", expose_message_tcp(message=recvd_message, person=bob))

    print("Ok... finished.")

    #inputs = [sys.stdin]  # Array of all input select has to look for

    '''
    running = True
    receivedKeyPair = False
    while running:
        try:
            in_rec, out_rec, ex_rec = select.select(inputs, [], [])  # Try to receive input from the socket
            # and save it in in_rec
        except KeyboardInterrupt:  # Catch Interrupts which happen if one shuts down the program forcefully
            print('Closed the connection')
            conn.send('quit'.encode('UTF8'))
            break
        for msgs in in_rec:  # Work up all the received messages saved in in_rec
            if msgs is conn:
                try:
                    new_message = conn.recv(buffer_size)  # reads the incoming messages
                    try:
                        msg = new_message.decode('utf-8').rstrip()
                        if 'quit' == msg:
                            print('Connection closed by other user')
                            running = False
                            return
                    except UnicodeDecodeError:
                        pass
                    # print("[Bob] received:", recv_tcp(socket=conn, person=bob))    #prints the messages
                    print("[Bob] received:", expose_message_tcp(message=new_message, person=bob))  # prints the messages
                except socket.error:
                    print('Could not read from socket')
                    running = False
                    return
            elif msgs is sys.stdin:
                line = sys.stdin.readline().rstrip()  # reads the messages from the server
                bytes_to_send = encapsulate_message_tcp(person=bob, message=line)  # sends the messages
                conn.send(bytes_to_send)
            else:
                break
    server_sock.close()  # Close the socket if while is left
    '''


# 1. Bob creates 4 keys: IK, SPKb, OPKb, DHratchet_seed.
# 2. Bob sends 3 keys via clear net, and DHratchet_public_key in header.
# 3. Alice makes x3dh with received keys.
# 4. Alice now has shared key. Alice runs init_ratchets().
# 5. Alice creates 2 keys IK, EKa.
# 6. Alice sends 2 keys via clear net, and DHratchet_seed in header.
# 7. Bob makes x3dh with received keys.
# 8. Bob now has shared key. Bob runs init_ratchets().
# 10. Alice initializes dh_ratchet with bob public key


if __name__ == '__main__':
    #ip_address = sys.argv[1]  # takes over the parameters
    #port = int(sys.argv[2])
    role = sys.argv[1]
    assert(role == 'Alice' or role == 'Bob')
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

    # Later on, if feedExsists is false,
    # we create an initial event in a new feed and store our identity event in the

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

    main(role)

    # bob.x3dh(alice)

    # Bob comes online and performs an X3DH using Alice's public keys
    # bob.x3dh(alice)

    # Initialize their symmetric ratchets
    # bob.init_ratchets()

    # Initialize Alice's sending ratchet with Bob's public key
    # alice.dh_ratchet(bob.DHratchet.public_key())

    # Alice sends Bob a message and her new DH ratchet public key
    # alice.send(bob, b'Hello Bob!')

    # Bob uses that information to sync with Alice and send her a message
    # bob.send(alice, b'Hello to you too, Alice!')

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
