from __future__ import annotations

from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from nacl.bindings import crypto_sign_ed25519_pk_to_curve25519, randombytes
from nacl.encoding import Base64Encoder
import nacl.utils

import hmac
from hashlib import sha256

from json import dump, load, loads

import crypto
from event import EVENT
from feed import FEED

from alias import add_alias, get_alias_by_id, get_id_by_alias


class USER:
    def __init__(self, fid, sk, follows, channels):
        self.fid = fid
        self.sk = sk
        self.follows = follows
        self.channels = channels

    @staticmethod
    def by_fid(fid) -> USER:
        try:
            with open("user-" + fid, 'r') as f:
                data = load(f)
                return USER(fid=fid, sk=data[0], follows=data[1], channels=data[2])
        except:
            return None

    @staticmethod
    def by_alias(alias) -> USER:
        fid = get_id_by_alias(alias)
        if fid == None:
            return None
        return USER.by_fid(fid)

    @staticmethod
    def new() -> USER:
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
        return crypto.ED25519(bytes.fromhex(self.sk))

    def get_curve_public_key(self) -> PublicKey:
        return self.get_signer().sk.verify_key.to_curve25519_public_key()

    def get_curve_private_key(self) -> PrivateKey:
        return self.get_signer().sk.to_curve25519_private_key()

    def follow(self, fid) -> bool:
        if self.fid == fid or self.follows.__contains__(fid):
            return True
        self.follows.append(fid)
        self.write_cleartext(get_message_json("log/follow", fid))
        return self.save()

    def unfollow(self, fid) -> bool:
        if not self.follows.__contains__(fid):
            return True
        self.follows.remove(fid)
        self.write_cleartext(get_message_json("log/unfollow", fid))
        return self.save()

    def invite(self, channel: CHANNEL, pk_joining):
        if not channel.is_owner(self):
            print('you are not owner of this channel')
            exit(1)
        channel.generate_dkey(self)
        channel.add_member(self, pk_joining)
        self.write_to(channel, 'chat/rekey', channel.dkeys_bytes()[0].hex(),
                      rekey=1)  # inform all members about new dkey
        self.write_to(channel, 'chat/invite', str(channel.export(share=True)),
                      pk_joining)  # inform new member with chat details

    def create_channel(self, channel) -> bool:
        if self.channels.__contains__(channel):
            print('channel already exists')
            return False
        CHANNEL(self, channel, True)
        self.write_cleartext(get_message_json('chat/create', channel))
        return True

    def add_channel(self, channel) -> bool:
        for c in self.channels:
            if c[0] == channel[0]:
                return False
        self.channels.append(channel)
        return self.save()

    def set_channel(self, channel) -> bool:
        b = []
        for c in self.channels:
            if c[0] == channel[0]:
                b.append(channel)
            else:
                b.append(c)
        self.channels = b
        return self.save()

    def get_channel(self, cid) -> bool:
        for c in self.channels:
            if c[0] == cid:
                return c
        return None

    def decrypt(self, event: EVENT, parse=False):
        # msg = '{"event": "app/action", "content": "xxx"}'
        # log_event = '{"hmac": "'+digest.hex()+'", "cyphertext": "'+encrypted.hex()+'"}'
        # log_event = {"cleartext": {"event": "chat/create", "content": "two"}}
        # log_event = {"cleartext": {"event": "log/sync", "content": "RAW_BACNET_EVENT"}}
        # print(event)
        sender = get_alias_by_id(self.fid)
        e = check_sync(event.content())
        if (e != None):
            # parse this content
            event = e
            sender = get_alias_by_id(e.fid.hex())
            # return 'sync: ' + e.fid.hex() + ' ' + e.content().__repr__()
        data = loads(event.content())

        try:
            return sender + '@all: ' + data['cleartext']['event'] + ' ' + data['cleartext']['content']
        except KeyError:
            cypher = bytes.fromhex(data['cyphertext'])
            if bytes.fromhex(data['hmac']) == hmac.digest(event.fid, cypher, sha256):
                try:
                    box = Box(self.get_curve_private_key(), PublicKey(crypto_sign_ed25519_pk_to_curve25519(event.fid)))
                    cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                    data = loads(cleartext)
                    inv = check_invite(data)
                    if parse and inv != None:
                        self.add_channel(inv)
                    return sender + '@private: ' + data['event'] + ' ' + data['content']
                except nacl.exceptions.CryptoError:
                    return sender + '@privatebox'
            for c in self.channels:  # loop through other channels hkey
                c = CHANNEL(self, c[0])
                channel = get_alias_by_id(c.cid)
                hkey = c.hkey_bytes()
                if bytes.fromhex(data['hmac']) == hmac.digest(hkey, cypher, sha256):
                    # print('matched hkey: '+hkey)
                    # print('hmac: '+data['hmac'])
                    # print('unboxing...')
                    for dk in c.dkeys_bytes():
                        try:
                            box = SecretBox(dk)
                            cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                            data = loads(cleartext)
                            rekey = check_rekey(data)
                            if parse and rekey != None:
                                c.add_dkey(self, rekey)
                            return sender + '@[' + channel + ']: ' + data['event'] + ' ' + data['content']
                        except nacl.exceptions.CryptoError:
                            continue  # perhaps there is another dkey
                    return sender + '@lock[' + channel + ']'  # no dkey found (not a member anymore)
            return sender + '@secret'  # - not cleartext nor matching a channel

    def log(self, raw=False):
        f = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer())
        if f.pcap == None:
            print('pcap error')
            exit(1)
        f.seq = 0
        f.hprev = None
        # print(f"Checking feed {f.fid.hex()}")
        # channels = list(map(lambda c: CHANNEL(self, c[0]), self.channels))
        for e in f:
            # print(e)
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq + 1}: chaining or signature problem")
            else:
                if raw:
                    print(f"-> event {e.seq}: ok, content={e.content().__repr__()}")
                else:
                    print(self.decrypt(e))
            f.seq += 1
            f.hprev = e.get_ref()

    def sync(self):
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

        for follow in self.follows:
            f = FEED("user-" + follow + '.pcap', bytes.fromhex(follow),
                     PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(follow))))
            if f.pcap == None:
                exit(1)
            f.seq = 0
            f.hprev = None
            # print(f"Checking feed {f.fid.hex()}")
            new_msg_count = 0
            for e in f:
                # print(e)
                if not f.is_valid_extension(e):
                    print(f"-> event {f.seq + 1}: chaining or signature problem")
                else:
                    try:
                        syncremote = synced[follow]
                    except:
                        syncremote = -1
                    if (syncremote < e.seq):  # if this event is not synced yet
                        synced[follow] = e.seq  # remember that we have synced this
                        eo = e
                        ev = check_sync(e.content())
                        if (ev != None):  # if it's a sync entry
                            if (ev.fid.hex() == self.fid):  # ignore the ones from our log
                                f.seq += 1
                                f.hprev = e.get_ref()
                                continue
                            try:
                                syncdeep = synced[ev.fid.hex()]  # get sync progress of this synced event
                            except:
                                syncdeep = -1
                            if (ev.seq <= syncdeep):  # ignore everything not newer
                                f.seq += 1
                                f.hprev = e.get_ref()
                                continue
                            synced[ev.fid.hex()] = ev.seq  # remember that we have synced this
                            eo = ev
                        self.write_cleartext(get_message_json("log/sync", eo.wire.hex()))
                        new_msg_count += 1
                        self.decrypt(eo, parse=True)
                        # print("add:",eo.seq,self.getFollowAlias(eo.fid.hex()))

                f.seq += 1
                f.hprev = e.get_ref()
            """ if (new_msg_count > 0):
                print(new_msg_count, " messages synced from", follow) """

    def create_feed(self):
        feed = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer(), True)
        if feed.pcap == None:
            print('could not create pcap')
            exit(1)
        feed.write('{"cleartext": ' + get_message_json('log/init', '') + '}')

    def write_feed(self, event):
        feed = FEED("user-" + self.fid + '.pcap', bytes.fromhex(self.fid), self.get_signer())
        if feed.pcap == None:
            print('pcap error')
            exit(1)
        feed.write(event)

    def write_cleartext(self, cleartext):
        self.write_feed('{"cleartext": ' + cleartext + '}')

    def write_cyphertext(self, digest, cyphertext):
        self.write_feed('{"hmac": "' + digest.hex() + '", "cyphertext": "' + cyphertext.hex() + '"}')

    def write_to(self, channel: CHANNEL, event, content, r=None, rekey=0):
        if r != None:
            box = Box(self.get_curve_private_key(), PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(r))))
            hkey = bytes.fromhex(self.fid)
        else:
            box = SecretBox(channel.dkeys_bytes()[rekey])
            hkey = channel.hkey_bytes()
        message = get_message_json(event, content).encode('utf-8')
        encrypted = box.encrypt(message, encoder=Base64Encoder)

        digest = hmac.digest(hkey, encrypted, sha256)
        self.write_cyphertext(digest, encrypted)

    def save(self) -> bool:
        try:
            with open("user-" + self.fid, "w") as f:
                dump([self.sk, self.follows, self.channels], f)
                return True
        except:
            return False


class CHANNEL:
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
        return bytes.fromhex(self.hkey)

    def dkeys_bytes(self) -> [bytes]:
        return list(map(lambda dk: bytes.fromhex(dk), self.dkeys))

    def generate_dkey(self, user):
        self.add_dkey(user, nacl.utils.random(SecretBox.KEY_SIZE).hex())

    def add_dkey(self, user, dkey):
        self.dkeys.insert(0, dkey)
        user.set_channel(self.export())

    def add_member(self, user, member):
        if self.members.__contains__(member):
            return
        self.members.append(member)
        user.set_channel(self.export())

    def is_owner(self, user: USER) -> bool:
        return self.owner == user.fid

    def export(self, share=False):
        if share:
            return [self.cid, self.owner, self.members, self.hkey, [self.dkeys[0]], self.seqno]
        return [self.cid, self.owner, self.members, self.hkey, self.dkeys, self.seqno]


def get_message_json(event, content) -> str:
    return '{"event": "' + event + '", "content": "' + content + '"}'


def check_sync(event) -> EVENT:
    data = loads(event)
    try:
        if (data['cleartext']['event'] == 'log/sync'):
            e = EVENT()
            e.from_wire(bytes.fromhex(data['cleartext']['content']))
            return e
        else:
            return None
    except KeyError:
        return None


def check_invite(data) -> []:
    try:
        if (data['event'] == 'chat/invite'):
            return eval(data['content'])
    except KeyError:
        return None


def check_rekey(data) -> str:
    try:
        if (data['event'] == 'chat/rekey'):
            return data['content']
    except KeyError:
        return None


if __name__ == '__main__':
    import argparse, sys

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

    args = parser.parse_args()
    if args.action == 'create':
        if get_id_by_alias(args.alias) != None:
            print("alias already existing, could not create user")
            exit(1)

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

    fid = get_id_by_alias(args.alias)
    if fid != None:
        user = USER.by_fid(fid)
        if user == None:
            print("could not load main user")
            exit(1)
    else:
        print("main alias not found")
        exit(1)

    user.sync()

    if args.action == 'info':
        print('fid', user.fid)
        print('follows', user.follows)
        print('channels', user.channels)

    if args.action == 'follow' or args.action == 'unfollow' or args.action == 'invite':
        other_fid = get_id_by_alias(args.other_alias)
        if other_fid != None:
            other_user = USER.by_fid(other_fid)
            if other_user == None:
                print("could not load second user")
                exit(1)
        else:
            print("second alias not found")
            exit(1)

        if args.action == 'follow':
            if user.fid == other_fid:
                print("you can not follow yourself")
                exit(1)
            if not user.follow(other_fid):
                print("could not save user")
                exit(1)
        if args.action == 'unfollow':
            if not user.unfollow(other_fid):
                print("could not save user")
                exit(1)

        if args.action == 'invite':
            c = get_id_by_alias(args.chat_alias)
            if c == None:
                print("chat alias not found")
                exit(1)
            user.invite(CHANNEL(user, c), other_fid)

    if args.action == 'log':
        user.log(args.raw)

    if args.action == 'chat':
        if user.create_channel(args.chat_alias):
            print('Secure team channel has been created!')
        else:
            print('Could not create chat!')
            exit(1)

    if args.action == 'message':
        c = get_id_by_alias(args.chat_alias)
        if c == None:
            print("chat alias not found")
            exit(1)
        c = CHANNEL(user, c)
        print('write your message and press enter...')
        user.write_to(c, 'chat/message', sys.stdin.readline().splitlines()[0])
