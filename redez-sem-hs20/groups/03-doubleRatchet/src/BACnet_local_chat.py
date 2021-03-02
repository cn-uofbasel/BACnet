from helper_functions.helpers import encapsulate_message_tcp, expose_message_tcp
from helper_functions.helpers import FOLDERNAME_KEYS

from helper_functions.alice import Alice
from helper_functions.bob import Bob

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

path_msg = os.getcwd() + FOLDERNAME_KEYS + '/message.txt'

from logStore.appconn.ratchet_chat_connection import RatchetChatFunction
from logStore.appconn.connection import Function
from logStore.funcs.EventCreationTool import EventFactory
from logStore.funcs.EventCreationTool import EventCreationTool
from logStore.funcs.event import Event, Meta, Content
import datetime


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
                                                    'sequenceNumber': '',
                                                    'lastSequenceNumber': '',
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
                                                    'sequenceNumber': '',
                                                    'lastSequenceNumber': '',
                                                    'timestamp': str(timestamp)})
    cf.insert_event(new_event)

def send_first_Bacnet_prekey_bundle(own_feed_id, key_bundle):
    timestamp = datetime.datetime.now()
    new_event = ecf.next_event('ratchet/contactInfo', {'key_bundle': key_bundle,
                                                       'own_feedID': own_feed_id,
                                                       'feedID_from_partner': '',
                                                       'timestamp': str(timestamp),
                                                       'chat_id': 1,
                                                       'sequenceNumber': '',
                                                       'lastSequenceNumber': ''})
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
            if msg == 'quit':
                break
            send_Bacnet_msg(encapsulate_message_tcp(alice, msg), feed_id, ecf.get_feed_id())
        except KeyboardInterrupt:
            print('Interrupted')
            sys.exit(0)

    running = True
    sentKeys = False

def start_server():  ## Bob
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
        send_first_Bacnet_prekey_bundle(ecf.get_feed_id(), prekey_bundle)
        exit()

    if event_list[1][0][0] == 'ratchet/connect' and bob.x3dh_status == 1:
        if bob.x3dh_status == 1:
            #print(event_list[1][0][1]['key_bundle'])
            bob.x3dh_2_complete_transaction_with_alice_keys(event_list[1][0][1]['key_bundle'])

            print("Waiting for an initial message from alice...")

            bob.x3dh_status = 2


    if content[0] == 'ratchet/message' or content[0] == 'ratchet/connect':
        if bob.x3dh_status == 2:

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

            else:
                print('no new messages')

            while True:
                try:
                    msg = input('Please enter your message: ')
                    if msg == 'quit':
                        break
                    send_Bacnet_msg(encapsulate_message_tcp(bob, msg), feed_id, ecf.get_feed_id())
                except KeyboardInterrupt:
                    print ('Interrupted')
                    sys.exit(0)

if __name__ == '__main__':
    #ip_address = sys.argv[1]  # takes over the parameters
    #port = int(sys.argv[2])
    role = sys.argv[1]
    assert(role == 'Alice' or role == 'Bob')

    main(role)

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
                                                                                   'feedID_from_partner': b'K*&w\xff\x1c>9\x9c\xc5\x904/\xa2w\x9a`\xae\x070\x18\xa4\x7f\xe2\x13\r\xa9x\x85P1\xdd',
                                                                                   'chatID': '5b60d1ff04d8958917d7eab32b...',
                                                                                   'sequnceNumber': ''
                                                                                   'lastSequenceNumber': '',
                                                                                   'timestamp': 1585201899}]
                                                                                   or
                                                                                   ['ratchat/connect', {'key_bundle': "b'g\x1b\x0f\xfb\x00\xa7\xc5!}\xaa\xa2\xa9\xc2p\xbe\x84g\xe1\xeb\x06\xea\xb4\xa4\xb3\xe2M\x1a\xa71\r\x8c5",
                                                                                    'own_feedID': b'Q\xeb\xbf\x18\x87jz\xc1\x1b\x03\xcb\xb1\x14\x1f\xca\xfaI\xe1R\xfa\xeaj\x92(~O\xa8\xf8\x94\xc1Uh',
                                                                                    'feedID_from_partner': b'K*&w\xff\x1c>9\x9c\xc5\x904/\xa2w\x9a`\xae\x070\x18\xa4\x7f\xe2\x13\r\xa9x\x85P1\xdd',
                                                                                    'chatID': '5b60d1ff04d8958917d7eab32b...',
                                                                                    'sequenceNumber': '',
                                                                                    'lastSequenceNumber': '',
                                                                                    'timestamp': 1585201888}]
                                                                                   or
                                                                                   ['ratchat/contactInfo':{'key_bundle': "b'g\x1b\x0f\xfb\x00\xa7\xc5!}\xaa\xa2\xa9\xc2p\xbe\x84g\xe1\xeb\x06\xea\xb4\xa4\xb3\xe2M\x1a\xa71\r\x8c5",
                                                                                    'own_feedID': b'K*&w\xff\x1c>9\x9c\xc5\x904/\xa2w\x9a`\xae\x070\x18\xa4\x7f\xe2\x13\r\xa9x\x85P1\xdd',
                                                                                    'feedID_from_partner': '',
                                                                                    'timestamp': 1585201888,
                                                                                    'chatID': '5b60d1ff04d8958917d7eab32b...',
                                                                                    'sequenceNumber': '',
                                                                                    'lastSequenceNumber': ''}]



  """
