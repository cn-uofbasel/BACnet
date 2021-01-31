#!/usr/bin/env python3


""" User
This script contains the user class as well as the channel class.
Furthermore, the main method for the secure team chat is part of this file.

This file contains the two following classes and functions outside of classes:
    * class USER (with several methods)
    * class CHANNEL (with several methods)
    * function get_message_json - converts info to json
    * function check_sync - checks if there was a synchronization
    * function check_invite - checks if there was an invitation
    * function check_rekey -  checks if there was a rekey
    * function main - run secure team chat
"""

from __future__ import annotations

from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from nacl.bindings import crypto_sign_ed25519_pk_to_curve25519, randombytes
from nacl.encoding import Base64Encoder
import nacl.utils

from toposort import toposort, toposort_flatten

import hmac
from hashlib import sha256

from json import dump, load, loads, dumps

import crypto
from event import EVENT
from feed import FEED

from alias import add_alias, get_alias_by_id, get_id_by_alias


class USER:
    """
    A class used to represent a user

    Attributes
    ----------
    fid : str
       public key of a user, which is also the id of the user
    sk : str
       secret key of a user
    follows : [USER]
        list of all users, as public key, which the user follows
    channels : [CHANNEL]
        all channels where the user is a member. A channel is represented as an array 
        [cid, owner ("fid" of the user), [members] (array of "fids"), hkey, [dkeys], seqno] 

    Methods
    -------
    by_fid(fid)
        Function identifies user by fid
    by_alias(ALIAS)
        Function identifies user by alias
    new()
        This function creates a new user
    get_signer()
         This function identifies the signer of the user
    get_curve_public_key
        This function returns the curved public key of the user
    get_curve_private_key
        This function returns the curved private key of the user
    follow(fid)
        This function enables a user to follow a user with given fid
    unfollow(fid)
        This function enables a user to unfollow a user with given fid
    invite(channel: CHANNEL, pk_joining)
        This function adds new user with its public key to a desired channel
    create_channel(channel)
        This function creates a new channel
    add_channel(channel)
        This function adds a channel to the channel list of the user
    set_channel(channel)
        This function updates an existing channel inside the channel list
    get_channel(cid)
        This function returns channel with given cid
    decrypt(event: EVENT, parse=False)
        This function encrypt an event if user has correct keys.
    log()
        This function prints the log of the user
    sync()
        This function syncs the user according to the osers he follows.
    create_feed()
        This function creates a feed of a user
    write_feed(event)
        This function writes an event to the feed
    write_cleartext(cleartext)
        This function writes cleartext
    write_cyphertext(digest, cyphertext)
        This function writes cyphertext
    write_to(channel: CHANNEL, event, content, r=None, rekey=0)
        This function enables sending an encoded message to a channel.
    save()
        This function is used if information of a user need to be updated and saved.
    """

    def __init__(self, fid, sk, follows, channels):
        self.fid = fid
        self.sk = sk
        self.follows = follows
        self.channels = channels

    @staticmethod
    def by_fid(fid) -> USER:
        """
        This function identifies a user by its fid.

        Parameters
        ----------
        fid : str
            The fid of the user
        Returns
        -------
        USER
            User with given fid
        """
        try:
            with open("user-" + fid, 'r') as f:
                data = load(f)
                return USER(fid=fid, sk=data[0], follows=data[1], channels=data[2])
        except:
            return None

    @staticmethod
    def by_alias(alias) -> USER:
        """
        This function identifies a user by its alias.

        Parameters
        ----------
        alias : str
            The alias name of the user
        Returns
        -------
        USER
            User with given alias
        """
        fid = get_id_by_alias(alias)
        if fid == None:
            return None
        return USER.by_fid(fid)

    @staticmethod
    def new() -> USER:
        """
        This function creates a new user.
        Returns
        -------
        USER
            new created user
        """
        key_pair = crypto.ED25519()
        key_pair.create()
        u = USER(
            fid=key_pair.get_public_key().hex(),
            sk=key_pair.get_private_key().hex(),
            follows=[],
            channels=[]
        )
        if u.save():
            return u
        return None

    def get_signer(self) -> crypto.ED25519:
        """
        This function identifies the signer of the user
        Parameters
        ----------
        self : USER
            The alias name of the user
        Returns
        -------
        crypto.ED25519
            Signer of the user
        """
        return crypto.ED25519(bytes.fromhex(self.sk))

    def get_curve_public_key(self) -> PublicKey:
        """
        This function returns the curved public key of the user.
        Parameters
        ----------
        self : USER
            The user which curve_public_key is needed
        Returns
        -------
        PublicKey
            The curve_public_key of the user
        """
        return self.get_signer().sk.verify_key.to_curve25519_public_key()

    def get_curve_private_key(self) -> PrivateKey:
        """
        This function returns the curved private key of the user.
        Parameters
        ----------
        self : USER
            The user which curve_private_key is needed
        Returns
        -------
        PublicKey
            The curve_private_key of the user
        """
        return self.get_signer().sk.to_curve25519_private_key()

    def follow(self, fid) -> bool:
        """
        This function enables a user to follow another user
        Parameters
        ----------
        self : USER
            The user which want to follow someone
        fid : str
            The fid of the user to follow
        Returns
        -------
        bool
            True if following process completed
        """
        # check if fid is own fid or already following this user
        if self.fid == fid or self.follows.__contains__(fid):
            return True
        # append new follower to own followers
        self.follows.append(fid)
        # write to log
        self.write_cleartext(get_message_json("log/follow", fid))
        return self.save()

    def unfollow(self, fid) -> bool:
        """
        This function enables a user to unfollow another user
        Parameters
        ----------
        self : USER
            The user which want to unfollow someone
        fid : str
            The fid of the user to unfollow
        Returns
        -------
        bool
            True if unfollowing process completed
        """
        # if non-following do nothing
        if not self.follows.__contains__(fid):
            return True
        # remove a fid from follower list
        self.follows.remove(fid)
        # write to log
        self.write_cleartext(get_message_json("log/unfollow", fid))
        return self.save()

    def invite(self, channel: CHANNEL, pk_joining):
        """
        This function invites a desired user to a channel.

        Parameters
        ----------
        self : USER
            The user inviting another user
        channel : CHANNEL
            The channel where user should be added
        pk_joining : str
            The public kew of invited user
        """
        # only owner of a channel can invite others
        if not channel.is_owner(self):
            print('you are not owner of this channel')
            exit(1)
        # generate new dkex
        channel.generate_dkey(self)
        # add new member
        channel.add_member(self, pk_joining)
        # log rekey process and invite
        back_ref = self.get_back_ref()
        self.write_to(channel, 'chat/rekey', channel.dkeys_bytes()[0].hex(),
                      back_ref=back_ref, rekey=1)  # inform all members about new dkey
        self.write_to(channel, 'chat/invite', str(channel.export(share=True)),
                      back_ref=back_ref, r=pk_joining)  # inform new member with chat details

    def create_channel(self, channel) -> bool:
        """
        This function creates a new channel.

        Parameters
        ----------
        self : USER
            The user creating a new channel
        channel : string
            New channel
        Returns
        -------
        bool
            True if channel successfully created
        """
        # check if channel already exists
        if self.channels.__contains__(channel):
            print('channel already exists')
            return False
        # create channel
        CHANNEL(self, channel, True)
        # log new channel
        self.write_cleartext(get_message_json('chat/create', channel))
        return True

    def add_channel(self, channel) -> bool:
        """
        This function adds a channel to the channels of a user.

        Parameters
        ----------
        self : USER
            The user which adds a channel
        channel : str
            The channel to add
        Returns
        -------
        bool
            True if channel successfully added
        """
        # go through all channels and if return false if channel already in list
        for c in self.channels:
            if c[0] == channel[0]:
                return False
        # append channel to list
        self.channels.append(channel)
        return self.save()

    def set_channel(self, channel) -> bool:
        """
        This function updates an existing channel inside the channel list.

        Parameters
        ----------
        self : USER
            The user which updates a channel
        channel : str
            The channel to update
        Returns
        -------
        bool
            True if channel successfully updated
        """
        b = []
        for c in self.channels:
            if c[0] == channel[0]:
                b.append(channel)
            else:
                b.append(c)
        self.channels = b
        return self.save()

    def get_channel(self, cid) -> bool:
        """
        This function identifies channel by fid.

        Parameters
        ----------
        self : USER
            The alias name of the user
        cid : str
            The cid of the channel
        Returns
        -------
        bool
            Returns channel of cid
        """
        # iterate through all channels
        for c in self.channels:
            # if cid equals a saved channel, return the channel
            if c[0] == cid:
                return c
        # no channel with this cid
        return None

    def decrypt(self, event: EVENT, parse=False, cleartext_only=False):
        """
        Using this function a user tries to decrypt an event.
        TODO doc
        Parameters
        ----------
        self : USER
            The user decrypting an event
        event : EVENT
            The event to decrypt
        parse : bool
            Describes if event need to be parsed
        cleartext_only: bool
            Describes if cleartext only used
        """
        # msg = '{"event": "app/action", "content": "xxx"}'
        # log_event = '{"hmac": "'+digest.hex()+'", "cyphertext": "'+encrypted.hex()+'"}'
        # log_event = {"cleartext": {"event": "chat/create", "content": "two"}}
        # log_event = {"cleartext": {"event": "log/sync", "content": "RAW_BACNET_EVENT"}}
        # print(event)

        # determine sender
        sender = get_alias_by_id(self.fid)
        # check if need to sync
        e = check_sync(event.content())
        if (e != None):
            # parse this content
            event = e
            sender = get_alias_by_id(e.fid.hex())
            # return 'sync: ' + e.fid.hex() + ' ' + e.content().__repr__()
        data = loads(event.content())

        try:
            # print cleartext
            if cleartext_only:
                return data['cleartext']
            return sender + '@all: ' + data['cleartext']['event'] + ' ' + data['cleartext']['content']
        except KeyError:
            # cyphertext --> needs decryption
            cypher = bytes.fromhex(data['cyphertext'])
            if bytes.fromhex(data['hmac']) == hmac.digest(event.fid, cypher, sha256):
                try:
                    # try to decrypt private event
                    box = Box(self.get_curve_private_key(), PublicKey(crypto_sign_ed25519_pk_to_curve25519(event.fid)))
                    cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                    data = loads(cleartext)
                    inv = check_invite(data)
                    if parse and inv != None:
                        self.add_channel(inv)
                    if cleartext_only:
                        return data
                    return sender + '@private: ' + data['event'] + ' ' + data['content']
                except nacl.exceptions.CryptoError:
                    # not allowed to decrypt private boy
                    if cleartext_only:
                        return None
                    return sender + '@privatebox'
            # loop through other channels hkey
            for c in self.channels:
                c = CHANNEL(self, c[0])
                channel = get_alias_by_id(c.cid)
                hkey = c.hkey_bytes()
                if bytes.fromhex(data['hmac']) == hmac.digest(hkey, cypher, sha256):
                    # print('matched hkey: '+hkey)
                    # print('hmac: '+data['hmac'])
                    # print('unboxing...')
                    for dk in c.dkeys_bytes():
                        try:
                            # decrypt message in channel
                            box = SecretBox(dk)
                            cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                            data = loads(cleartext)
                            rekey = check_rekey(data)
                            if parse and rekey != None:
                                c.add_dkey(self, rekey)
                            if cleartext_only:
                                return data
                            if data['backref'] != None:
                                # print(data['backref'].encode('ISO-8859-1'))
                                return sender + '@[' + channel + ']: ' + data['event'] + ' ' + data['content'] + ' ' + \
                                       data['backref']
                            return sender + '@[' + channel + ']: ' + data['event'] + ' ' + data['content']
                        except nacl.exceptions.CryptoError:
                            # not allowed to decrypt channel message
                            continue  # perhaps there is another dkey
                    if cleartext_only:
                        return None
                    return sender + '@lock[' + channel + ']'  # no dkey found (not a member anymore)
            if cleartext_only:
                return None
            return sender + '@secret'  # - not cleartext nor matching a channel

    def decrypt_channel(self, event: EVENT, channel_read, parse=False, cleartext_only=False):
        """
        TODO doc
        """
        # msg = '{"event": "app/action", "content": "xxx"}'
        # log_event = '{"hmac": "'+digest.hex()+'", "cyphertext": "'+encrypted.hex()+'"}'
        # log_event = {"cleartext": {"event": "chat/create", "content": "two"}}
        # log_event = {"cleartext": {"event": "log/sync", "content": "RAW_BACNET_EVENT"}}
        # print(event)

        # determine sender
        sender = get_alias_by_id(self.fid)
        # check if need to sync
        e = check_sync(event.content())
        if (e != None):
            # parse this content
            event = e
            sender = get_alias_by_id(e.fid.hex())
            # return 'sync: ' + e.fid.hex() + ' ' + e.content().__repr__()
        data = loads(event.content())

        try:
            # print cleartext
            if cleartext_only:
                return
            i = sender + '@all: ' + data['cleartext']['event'] + ' ' + data['cleartext']['content']
            return None
        except KeyError:
            # cyphertext --> needs decryption
            cypher = bytes.fromhex(data['cyphertext'])
            if bytes.fromhex(data['hmac']) == hmac.digest(event.fid, cypher, sha256):
                try:
                    # try to decrypt private event
                    box = Box(self.get_curve_private_key(), PublicKey(crypto_sign_ed25519_pk_to_curve25519(event.fid)))
                    cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                    data = loads(cleartext)
                    inv = check_invite(data)
                    if parse and inv != None:
                        self.add_channel(inv)
                    if cleartext_only:
                        return data
                    #return sender + '@private: ' + data['event'] + ' ' + data['content']
                except nacl.exceptions.CryptoError:
                    # not allowed to decrypt private boy
                    if cleartext_only:
                        return None
                    #return sender + '@privatebox'
            # loop through other channels hkey
            for c in self.channels:
                c = CHANNEL(self, c[0])
                channel = get_alias_by_id(c.cid)
                #print(get_id_by_alias(channel_read) + 'get_alias_by_id(c) READ')
                if channel == channel_read:
                    hkey = c.hkey_bytes()
                    if bytes.fromhex(data['hmac']) == hmac.digest(hkey, cypher, sha256):
                        # print('matched hkey: '+hkey)
                        # print('hmac: '+data['hmac'])
                        # print('unboxing...')
                        for dk in c.dkeys_bytes():
                            try:
                                # decrypt message in channel
                                box = SecretBox(dk)
                                cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                                data = loads(cleartext)
                                rekey = check_rekey(data)
                                if parse and rekey != None:
                                    c.add_dkey(self, rekey)
                                if cleartext_only:
                                    return data
                                if data['event'] == 'chat/message':
                                    #print(event)
                                    ref = event.get_ref()[1]
                                    if data['backref'] != None:
                                        # print(data['backref'].encode('ISO-8859-1'))
                                        # return sender + '@[' + channel + ']: ' + data['event'] + ' ' + data['content'] + ' ' + data['backref']
                                        return (ref, sender, data['content'], data['backref'])
                                    # self referencing if first message
                                    return (ref, sender, data['content'], ref)
                                    # return sender + '@[' + channel + ']: ' + data['event'] + ' ' + data['content']

                            except nacl.exceptions.CryptoError:
                                # not allowed to decrypt channel message
                                continue  # perhaps there is another dkey
        return None

    def log(self, raw=False):
        """
        This function prints the log of a user.

        Parameters
        ----------
        self : USER
            The user whos log needs to be shown
        raw : bool
            Specifies if content shown raw or decrypted
        """
        # get feed
        f = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer())
        if f.pcap == None:
            print('pcap error')
            exit(1)
        f.seq = 0
        f.hprev = None
        # print(f"Checking feed {f.fid.hex()}")
        # channels = list(map(lambda c: CHANNEL(self, c[0]), self.channels))
        # go though all events of the feed
        for e in f:
            # print(e)
            # event not valid
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq + 1}: chaining or signature problem")
            # event valid
            else:
                # print raw details
                if raw:
                    print(f"-> event {e.seq}: ok, content={e.content().__repr__()}")
                # decrypt content
                else:
                    print(self.decrypt(e))
            # go to next event in feed
            f.seq += 1
            f.hprev = e.get_ref()

    def sync(self):
        """
        This function completes a synchronization process of a user
        which gets the updates of the users he follows.

        Parameters
        ----------
        self : USER
            The user which does a sync
        """
        synced = {}
        f = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer())
        if f.pcap == None:
            return
        f.seq = 0
        f.hprev = None
        # print(f"Checking feed {f.fid.hex()}")
        for e in f:
            # print(e)
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq + 1}: chaining or signature problem")
            else:
                event = check_sync(e.content())
                if (event != None):
                    synced[event.fid.hex()] = event.seq

            f.seq += 1
            f.hprev = e.get_ref()
        # print(synced)

        # iterate through the users he follows
        for follow in self.follows:
            f = FEED("user-" + follow + '.pcap', bytes.fromhex(follow),
                     PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(follow))))
            if f.pcap == None:
                exit(1)
            f.seq = 0
            f.hprev = None
            # print(f"Checking feed {f.fid.hex()}")
            new_msg_count = 0
            # iterate through events in their feeds
            for e in f:
                # print(e)
                # event not valid
                if not f.is_valid_extension(e):
                    print(f"-> event {f.seq + 1}: chaining or signature problem")
                # event valid
                else:
                    try:
                        syncremote = synced[follow]
                    except:
                        syncremote = -1
                    # if this event is not synced yet
                    if (syncremote < e.seq):
                        # remember that we have synced this
                        synced[follow] = e.seq
                        eo = e
                        ev = check_sync(e.content())
                        # if it's a sync entry
                        if (ev != None):
                            # ignore the ones from our log
                            if (ev.fid.hex() == self.fid):
                                f.seq += 1
                                f.hprev = e.get_ref()
                                continue
                            try:
                                # get sync progress of this synced event
                                syncdeep = synced[ev.fid.hex()]
                            except:
                                syncdeep = -1
                            # ignore everything not newer
                            if (ev.seq <= syncdeep):
                                f.seq += 1
                                f.hprev = e.get_ref()
                                continue
                            # remember that we have synced this
                            synced[ev.fid.hex()] = ev.seq
                            eo = ev
                        # write cleartext to log oof sync process
                        self.write_cleartext(get_message_json("log/sync", eo.wire.hex()))
                        new_msg_count += 1
                        self.decrypt(eo, parse=True)
                        # print("add:",eo.seq,self.getFollowAlias(eo.fid.hex()))
                # go to next event in feed
                f.seq += 1
                f.hprev = e.get_ref()
            """ if (new_msg_count > 0):
                print(new_msg_count, " messages synced from", follow) """

    def get_back_ref(self):
        synced = None
        f = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer())
        if f.pcap == None:
            return
        f.seq = 0
        f.hprev = None
        # print(f"Checking feed {f.fid.hex()}")
        for e in f:
            # print(e)
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq + 1}: chaining or signature problem")
            else:
                event = check_sync(e.content())
                if (event != None):
                    cleartext = self.decrypt(event, cleartext_only=True)
                    if (cleartext == None or cleartext['event'] != 'chat/message'):
                        # continue
                        synced = event.get_ref()
            f.seq += 1
            f.hprev = e.get_ref()
        if (synced != None):
            return synced[1].decode('ISO-8859-1')
        return None

    def create_feed(self):
        """
        This function creates a feed of a specific user

        Parameters
        ----------
        self : USER
            The user creating the feed
        """
        # create feed
        feed = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer(), True)
        if feed.pcap == None:
            # feed creation failed
            print('could not create pcap')
            exit(1)
        # write completion of feed creation in cleartext
        feed.write('{"cleartext": ' + get_message_json('log/init', '') + '}')

    def write_feed(self, event):
        """
        This function writes an event to the feed

        Parameters
        ----------
        self : USER
             The user writing to the feed
        event : EVENT
            The event to write
        """
        # open feed
        feed = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer())
        if feed.pcap == None:
            # feed not valid -> exit
            print('pcap error')
            exit(1)
        # write event to feed
        feed.write(event)

    def write_cleartext(self, cleartext):
        """
        This function writes cleartext

        Parameters
        ----------
        self : USER
            The user who writes
        cleartext: str
            The message
        """
        self.write_feed('{"cleartext": ' + cleartext + '}')

    def write_cyphertext(self, digest, cyphertext):
        """
        This function writes cyphertext

        Parameters
        ----------
        self : USER
            The user who writes
        digest: bytes
            The hmac of the encryption
        cyphertext: nacl.utils.EncryptedMessage
            The encrypted message
        """
        self.write_feed('{"hmac": "' + digest.hex() + '", "cyphertext": "' + cyphertext.hex() + '"}')

    def write_to(self, channel: CHANNEL, event, content, back_ref=None, r=None, rekey=0):
        """
        This function creates a write statement after encrypting the message.
        TODO doc
        Parameters
        ----------
        self : USER
            The user who writes
        channel : CHANNEL
            The channel where user writes to
        event: EVENT
            The event to write
        content: str
            The content of the event
        r: String
            The public key of the recipient user
        rekey: int
            Indicates which dkey to use (0 = latest, 1 = one before latest, ...)
        """
        # no rekey
        if r != None:
            # create a box between owner of a channel and invited user
            box = Box(self.get_curve_private_key(), PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(r))))
            hkey = bytes.fromhex(self.fid)
        # rekey necessary
        else:
            # create a box containing all members of a channel
            box = SecretBox(channel.dkeys_bytes()[rekey])
            hkey = channel.hkey_bytes()
        # build message from event and content and encrypt it
        message = get_message_json(event, content, back_ref).encode('utf-8')
        encrypted = box.encrypt(message, encoder=Base64Encoder)

        # write cyphertext using digest (=cypher) and encrypted message
        digest = hmac.digest(hkey, encrypted, sha256)
        self.write_cyphertext(digest, encrypted)

    def save(self) -> bool:
        """
        This function saves the updates of a user.

        Parameters
        ----------
        self : USER
            The user who wants to save
        Returns
        -------
        bool
            True if save successfully done, otherwise false
        """
        try:
            # update successful secrete key, users to follow and channels
            with open("user-" + self.fid, "w") as f:
                dump([self.sk, self.follows, self.channels], f)
                return True
        except:
            # update failed
            return False

    def read(self, c):
        messages = []
        # get feed
        f = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer())
        if f.pcap == None:
            print('pcap error')
            exit(1)
        f.seq = 0
        f.hprev = None
        # print(f"Checking feed {f.fid.hex()}")
        # channels = list(map(lambda c: CHANNEL(self, c[0]), self.channels))
        # go though all events of the feed
        for e in f:
            # print(e)
            # event not valid
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq + 1}: chaining or signature problem")
            # event valid
            else:
                # decrypt content
                i = self.decrypt_channel(e, c)
                if i!=None:
                    messages.append(i)
            # go to next event in feed
            f.seq += 1
            f.hprev = e.get_ref()
        dict = {}
        for i in range(0, len(messages)):
            if isinstance(messages[i][3], bytes):
                dict[messages[i][0]] = {messages[i][3]}
            else:
                dict[messages[i][0]] = {messages[i][3]}
        print(dict)
        #print(list(toposort(dict)))


class CHANNEL:
    """
    A class used to represent an channel

    Attributes
    ---------
    cid : str
       id of a channel
    owner : USER
       User which owns channel
    members : [USER]
        list containing all members of a channel
    hkey : bytes
        authentication key of channel
    dkeys : [bytes]
        encryption keys of channel
    seqno : int
        identifies sequence number (not yet used)

    Methods
    -------
    hkey_bytes()
        Function returns hkey of channel
    dkeys_bytes()
        Function returns dkeys of channel
    generate_dkey(user)
        Function creates dkey of a channel
    add_dkey(user, dkey)
        Function adds dkey of a channel
    add_member(user, member)
        Function adds new member to channel
    is_owner(user: USER)
        Function checks if user is owner of channel
    export(share=False)
        FUnction exports all channel attributes
    """

    def __init__(self, user: USER, cid, new=False):
        if new:
            self.cid = randombytes(8).hex()
            self.owner = user.fid
            self.members = [user.fid]
            self.hkey = randombytes(16).hex()
            self.dkeys = [nacl.utils.random(SecretBox.KEY_SIZE).hex()]
            self.seqno = 0
            user.add_channel(self.export())
            if not add_alias(cid, self.cid):
                print("could not create chat alias:", cid)
                exit(1)
        else:
            c = user.get_channel(cid)
            if c != None:
                self.cid = c[0]
                self.owner = c[1]
                self.members = c[2]
                self.hkey = c[3]
                self.dkeys = c[4]
                self.seqno = c[5]
            else:
                print("unknown channel:", cid)
                exit(1)

    def hkey_bytes(self) -> bytes:
        """
        This function returns authentication key (hkey) of channel.

        Parameters
        ----------
        self : CHANNEL
            The channel to get hkey
        Returns
        -------
        bytes
            Bytes of hkey
        """
        return bytes.fromhex(self.hkey)

    def dkeys_bytes(self) -> [bytes]:
        """
        This function returns encyption key (dkey) of channel.

        Parameters
        ----------
        self : CHANNEL
            The channel to get dkey
        Returns
        -------
        bytes
            Bytes of dkey
        """
        return list(map(lambda dk: bytes.fromhex(dk), self.dkeys))

    def generate_dkey(self, user):
        """
        This function creates encyption key (dkey) of a user for a channel.

        Parameters
        ----------
        self : CHANNEL
            The channel of user
        user : str
            The user to create dkey
        """
        self.add_dkey(user, nacl.utils.random(SecretBox.KEY_SIZE).hex())

    def add_dkey(self, user, dkey):
        """
        This function adds encyption key (dkey) to channel and sets channel of user.

        Parameters
        ----------
        self : CHANNEL
            The channel of a user
        user : str
            The user to set channel
        dkey : str
            dkey to add to channel
        """
        self.dkeys.insert(0, dkey)
        user.set_channel(self.export())

    def add_member(self, user, member):
        """
        This function adds new member to channel

        Parameters
        ----------
        self : CHANNEL
            The channel to add members to
        user : str
            User to add
        member : str
            Member to add
        """
        # check if member not yet in channel
        if self.members.__contains__(member):
            return
        # append member to channel
        self.members.append(member)
        # set channel to user (=member)
        user.set_channel(self.export())

    def is_owner(self, user: USER) -> bool:
        """
        This function checks if user is owner

        Parameters
        ----------
        self : CHANNEL
            channel to check
        user : USER
            owner
        Returns
        -------
        bool
            True if user is owner, otherwise false
        """
        return self.owner == user.fid

    def export(self, share=False):
        """
        This function exports a channel.

        Parameters
        ----------
        self : CHANNEL
            The channel to export
        share : bool
            Defines if export is shared along all
        Returns
        -------
        bool
            True if new alias has been added, otherwise false
        """
        # if share == true, take dkey of first entry
        if share:
            return [self.cid, self.owner, self.members, self.hkey, [self.dkeys[0]], self.seqno]
        return [self.cid, self.owner, self.members, self.hkey, self.dkeys, self.seqno]


def get_message_json(event, content, back_ref=None) -> str:
    """
    This function converts an event and its content to a json format.
    TODO doc
    Parameters
    ----------
    event : EVENT
        Event to translate
    content : str
        Content of event
    Returns
    -------
    str
        json format of event and content
    """
    return dumps({"event": event, "content": content, "backref": back_ref})


def check_sync(event) -> EVENT:
    """
    This function checks if there was a synchronization.

    Parameters
    ----------
    event : EVENT
        The event to check
    Returns
    -------
    EVENT
        Content of an invite or none if no invitation
    """
    # load data from event
    data = loads(event)
    try:
        # check if data represents a sync event
        if (data['cleartext']['event'] == 'log/sync'):
            # return e because it was a sync
            e = EVENT()
            e.from_wire(bytes.fromhex(data['cleartext']['content']))
            return e
        else:
            # return none because no sync
            return None
    except KeyError:
        return None


def check_invite(data) -> []:
    """
    This function checks if there was a invitation.

    Parameters
    ----------
    data : [bytes]
        The data to check
    Returns
    -------
    []
        Content of a invite or none if no invitation
    """
    try:
        # if content of data-event is an invite return content
        if (data['event'] == 'chat/invite'):
            return eval(data['content'])
    except KeyError:
        # return none if no invite
        return None


def check_rekey(data) -> str:
    """
    This function checks if there was a rekey.

    Parameters
    ----------
    data : [bytes]
        The data to check
    Returns
    -------
    str
        Content of a rekey of a channel
    """
    try:
        if (data['event'] == 'chat/rekey'):
            return data['content']
    except KeyError:
        return None


if __name__ == '__main__':
    """
    This is the main function of the secure team chat application.
    """
    import argparse, sys

    # possible arguments to parse (automatically generating of help option)
    parser = argparse.ArgumentParser(description='Secure Team Chat')
    parser.add_argument('alias', help='user alias')

    subparsers = parser.add_subparsers(help='actions', dest='action', required=True)

    create_parser = subparsers.add_parser('create', help='Create an user')

    log_parser = subparsers.add_parser('log', help='Show user log')
    log_parser.add_argument('-r', default=False, action='store_true', dest='raw', help='show raw events')

    info_parser = subparsers.add_parser('info', help='Show user info')

    follow_parser = subparsers.add_parser('follow', help='Follow an user')
    follow_parser.add_argument('other_alias', help='alias of user to follow')

    unfollow_parser = subparsers.add_parser('unfollow', help='Unfollow an user')
    unfollow_parser.add_argument('other_alias', help='alias of user to unfollow')

    chat_parser = subparsers.add_parser('chat', help='Create a chat')
    chat_parser.add_argument('chat_alias', help='alias of chat')

    message_parser = subparsers.add_parser('message', help='Send a message')
    message_parser.add_argument('chat_alias', help='alias of chat')

    invite_parser = subparsers.add_parser('invite', help='Invite an user')
    invite_parser.add_argument('chat_alias', help='alias of chat')
    invite_parser.add_argument('other_alias', help='alias of invited user')

    channel_parser = subparsers.add_parser('channel', help='View a channel')
    channel_parser.add_argument('chat_alias', help='alias of chat')

    # parsing
    args = parser.parse_args()
    # create a new user
    if args.action == 'create':
        # no unique user alias
        if get_id_by_alias(args.alias) != None:
            print("alias already existing, could not create user")
            exit(1)
        # create unique user
        u = USER.new()
        if u != None:
            print("user created, id:", u.fid)
            u.create_feed()
            if not add_alias(args.alias, u.fid):
                print("could not save alias")
                exit(1)
            exit(0)
        else:
            print("could not create user")
            exit(1)

    # save alias of current run
    fid = get_id_by_alias(args.alias)
    if fid != None:
        # identified user
        user = USER.by_fid(fid)
        if user == None:
            print("could not load main user")
            exit(1)
    # alias not existing
    else:
        print("main alias not found")
        exit(1)

    # user needs to sync to get last updates
    user.sync()

    # print information for specific user
    if args.action == 'info':
        print('fid', user.fid)
        print('follows', user.follows)
        print('channels', user.channels)

    # arg has influence on channel and requests a second user
    if args.action == 'follow' or args.action == 'unfollow' or args.action == 'invite':
        # identify second user
        other_fid = get_id_by_alias(args.other_alias)
        if other_fid != None:
            # second user exists
            other_user = USER.by_fid(other_fid)
            # second user not loaded
            if other_user == None:
                print("could not load second user")
                exit(1)
        # second user not existing
        else:
            print("second alias not found")
            exit(1)

        # following action
        if args.action == 'follow':
            # check that not following itself
            if user.fid == other_fid:
                print("you can not follow yourself")
                exit(1)
            # follow other user
            if not user.follow(other_fid):
                # follow other user not worked
                print("could not save user")
                exit(1)
        # unfollow action
        if args.action == 'unfollow':
            # unfollow other user
            if not user.unfollow(other_fid):
                # unfollow other user not worked
                print("could not save user")
                exit(1)
        # invite action
        if args.action == 'invite':
            # parse channel where eto invite user
            c = get_id_by_alias(args.chat_alias)
            # check if channel exists
            if c == None:
                # channel not existing
                print("chat alias not found")
                exit(1)
            # channel exists and invite of user is possible
            user.invite(CHANNEL(user, c), other_fid)

    # print log of user
    if args.action == 'log':
        user.log(args.raw)

    # create a chat channel
    if args.action == 'chat':
        # create channel with name according to input
        if user.create_channel(args.chat_alias):
            print('Secure team channel has been created!')
        else:
            # channel creation failed
            print('Could not create chat!')
            exit(1)

    # write a message to a channel
    if args.action == 'message':
        # parse channel where to write message to and check is channel exists
        c = get_id_by_alias(args.chat_alias)
        if c == None:
            # if channel not exists return
            print("chat alias not found")
            exit(1)
        c = CHANNEL(user, c)
        print('write your message and press enter...')
        # parse input as message and write it to the channel
        back_ref = user.get_back_ref()
        user.write_to(c, 'chat/message', sys.stdin.readline().splitlines()[0], r=None, back_ref=back_ref)

    # read a channel
    if args.action == 'channel':
        # parse channel which chat should be shown
        c = get_id_by_alias(args.chat_alias)
        if c == None:
            # if channel not exists return
            print("chat alias not found")
            exit(1)
        # read channel
        user.read(args.chat_alias)
