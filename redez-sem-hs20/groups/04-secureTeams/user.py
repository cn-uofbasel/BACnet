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

from alias import addAlias, getAliasById, getIdByAlias

class USER:
    def __init__(self, fid, sk, follows, channels, known_hosts):
        self.fid = fid
        self.sk = sk
        self.follows = follows
        self.channels = channels
        self.known_hosts = known_hosts
    
    @staticmethod
    def byFid(fid) -> USER:
        try:
            with open("user-"+fid, 'r') as f:
                data = load(f)
                return USER(fid=fid,sk=data[0],follows=data[1],channels=data[2],known_hosts=data[3])
        except:
            return None
    
    @staticmethod
    def byAlias(alias) -> USER:
        fid = getIdByAlias(alias)
        if fid == None:
            return None
        return USER.byFid(fid)

    @staticmethod
    def new() -> USER:
        key_pair = crypto.ED25519()
        key_pair.create()
        u = USER(
            fid=key_pair.get_public_key().hex(),
            sk=key_pair.get_private_key().hex(),
            follows=[],
            channels=[],
            known_hosts=[]
        )
        if u.save():
            return u
        return None
    
    def getSigner(self) -> crypto.ED25519:
        return crypto.ED25519(bytes.fromhex(self.sk))

    def getCurvePublicKey(self) -> PublicKey:
        return self.getSigner().sk.verify_key.to_curve25519_public_key()

    def getCurvePrivateKey(self) -> PrivateKey:
        return self.getSigner().sk.to_curve25519_private_key()

    def follow(self, fid) -> bool:
        if self.fid == fid or self.follows.__contains__(fid):
            return True
        self.follows.append(fid)
        self.writeCleartext(getMessageJSON("log/follow", fid))
        return self.save()
    
    def unfollow(self, fid) -> bool:
        if not self.follows.__contains__(fid):
            return True
        self.follows.remove(fid)
        self.writeCleartext(getMessageJSON("log/unfollow", fid))
        return self.save()
    
    def invite(self, channel: CHANNEL, pk_joining):
        if not channel.is_owner(self):
            print('you are not owner of this channel')
            exit(1)
        channel.generate_dkey(self)
        channel.add_member(self, pk_joining)
        self.writeTo(channel, 'chat/rekey', channel.dkeys_bytes()[0].hex(), rekey=1) # inform all members about new dkey
        self.writeTo(channel, 'chat/invite', str(channel.export(share=True)), pk_joining) # inform new member with chat details

    def createChannel(self, channel) -> bool:
        if self.channels.__contains__(channel):
            print('channel already exists')
            return False
        CHANNEL(self, channel, True)
        self.writeCleartext(getMessageJSON('chat/create', channel))
        return True
    
    def addChannel(self, channel) -> bool:
        for c in self.channels:
            if c[0]==channel[0]:
                return False
        self.channels.append(channel)
        return self.save()
    
    def setChannel(self, channel) -> bool:
        b = []
        for c in self.channels:
            if c[0]==channel[0]:
                b.append(channel)
            else:
                b.append(c)
        self.channels = b
        return self.save()
    
    def getChannel(self, cid) -> bool:
        for c in self.channels:
            if c[0]==cid:
                return c
        return None
    
    def decrypt(self, event, parse=False):
        # msg = '{"event": "app/action", "content": "xxx"}'
        # log_event = '{"hmac": "'+digest.hex()+'", "cyphertext": "'+encrypted.hex()+'"}'
        # log_event = {"cleartext": {"event": "chat/create", "content": "two"}}
        # log_event = {"cleartext": {"event": "log/sync", "content": "RAW_BACNET_EVENT"}}
        #print(event)
        sender = getAliasById(self.fid)
        e = checkSync(event)
        if (e!=None):
            # parse this content
            event = e.content()
            sender = getAliasById(e.fid.hex())
            #return 'sync: ' + e.fid.hex() + ' ' + e.content().__repr__()
        data = loads(event)
        try:
            return sender+'@all: ' + data['cleartext']['event'] + ' ' + data['cleartext']['content']
        except KeyError:
            cypher = bytes.fromhex(data['cyphertext'])
            for host in self.known_hosts:
                if bytes.fromhex(data['hmac']) == hmac.digest(bytes.fromhex(host), cypher, sha256):
                    try:
                        box = Box(self.getCurvePrivateKey(),  PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(host))))
                        cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                        data = loads(cleartext)
                        inv = checkInvite(data)
                        if parse and inv != None:
                            self.addChannel(inv)
                        return sender+'@[private]: ' + data['event'] + ' ' + data['content']
                    except nacl.exceptions.CryptoError:
                        #return sender+'@cyphertext[private] -  error while decrypting private message'
                        return sender+'@secret'
            for c in self.channels:#loop through other channels hkey
                c = CHANNEL(self, c[0])
                channel=getAliasById(c.cid)
                hkey=c.hkey_bytes()
                if bytes.fromhex(data['hmac']) == hmac.digest(hkey, cypher, sha256):
                    #print('matched hkey: '+hkey)
                    #print('hmac: '+data['hmac'])
                    #print('unboxing...')
                    for dk in c.dkeys_bytes():
                        try:
                            box = SecretBox(dk)
                            cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                            data = loads(cleartext)
                            rekey = checkRekey(data)
                            if parse and rekey != None:
                                c.add_dkey(self, rekey)
                            return sender+'@['+channel+']: ' + data['event'] + ' ' + data['content']
                        except nacl.exceptions.CryptoError:
                            continue #perhaps there is another dkey
                    return sender+'@secret['+channel+']' #no dkey found (not member or private message)
            return sender+'@secret' # - not cleartext nor matching a channel

    def log(self, raw=False):
        f = FEED("user-"+self.fid+'.pcap', bytes.fromhex(self.fid), self.getSigner())
        if f.pcap == None:
            print('pcap error')
            exit(1)
        f.seq = 0
        f.hprev = None
        #print(f"Checking feed {f.fid.hex()}")
        #channels = list(map(lambda c: CHANNEL(self, c[0]), self.channels))
        for e in f:
            # print(e)
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq+1}: chaining or signature problem")
            else:
                if raw:
                    print(f"-> event {e.seq}: ok, content={e.content().__repr__()}")
                else:
                    print(self.decrypt(e.content()))
            f.seq += 1
            f.hprev = e.get_ref()
    
    def sync(self):
        synced={}
        f = FEED("user-"+self.fid+'.pcap', bytes.fromhex(self.fid), self.getSigner())
        if f.pcap == None:
            return
        f.seq = 0
        f.hprev = None
        #print(f"Checking feed {f.fid.hex()}")
        for e in f:
            # print(e)
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq+1}: chaining or signature problem")
            else:
                event = checkSync(e.content())
                if (event != None):
                    synced[event.fid.hex()] = event.seq
            
            f.seq += 1
            f.hprev = e.get_ref()
        #print(synced)

        for follow in self.follows:
            f = FEED("user-"+follow+'.pcap', bytes.fromhex(follow), PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(follow))))
            if f.pcap == None:
                exit(1)
            f.seq = 0
            f.hprev = None
            #print(f"Checking feed {f.fid.hex()}")
            newMsgCount = 0
            for e in f:
                # print(e)
                if not f.is_valid_extension(e):
                    print(f"-> event {f.seq+1}: chaining or signature problem")
                else:
                    try:
                        syncremote = synced[follow]
                    except:
                        syncremote = -1
                    if (syncremote < e.seq): # if this event is not synced yet
                        synced[follow] = e.seq # remember that we have synced this
                        eo = e
                        ev = checkSync(e.content())
                        if (ev != None): # if it's a sync entry
                            if (ev.fid.hex() == self.fid): # ignore the ones from our log
                                f.seq += 1
                                f.hprev = e.get_ref()
                                continue
                            try:
                                syncdeep = synced[ev.fid.hex()] # get sync progress of this synced event
                            except:
                                syncdeep = -1
                            if (ev.seq <= syncdeep): # ignore everything not newer
                                f.seq += 1
                                f.hprev = e.get_ref()
                                continue
                            synced[ev.fid.hex()] = ev.seq # remember that we have synced this
                            eo = ev
                        self.writeCleartext(getMessageJSON("log/sync", eo.wire.hex()))
                        newMsgCount += 1
                        self.known_hosts = list(synced.keys())
                        self.decrypt(eo.content(), parse=True)
                        #print("add:",eo.seq,self.getFollowAlias(eo.fid.hex()))
                
                f.seq += 1
                f.hprev = e.get_ref()
            """ if (newMsgCount > 0):
                print(newMsgCount, " messages synced from", follow) """
        self.save()
    
    def createFeed(self):
        feed = FEED("user-"+self.fid+'.pcap', bytes.fromhex(self.fid), self.getSigner(), True)
        if feed.pcap == None:
            print('could not create pcap')
            exit(1)
        feed.write('{"cleartext": '+getMessageJSON('log/init', '')+'}')
    
    def writeFeed(self, event):
        feed = FEED("user-"+self.fid+'.pcap', bytes.fromhex(self.fid), self.getSigner())
        if feed.pcap == None:
            print('pcap error')
            exit(1)
        feed.write(event)
    
    def writeCleartext(self, cleartext):
        self.writeFeed('{"cleartext": '+cleartext+'}')

    def writeCyphertext(self, digest, cyphertext):
        self.writeFeed('{"hmac": "'+digest.hex()+'", "cyphertext": "'+cyphertext.hex()+'"}')
    
    def writeTo(self, channel: CHANNEL, event, content, r=None, rekey=0):
        if r!=None:
            box =  Box(self.getCurvePrivateKey(), PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(r))))
            hkey = bytes.fromhex(self.fid)
        else:
            box = SecretBox(channel.dkeys_bytes()[rekey])
            hkey = channel.hkey_bytes()
        message = getMessageJSON(event, content).encode('utf-8')
        encrypted = box.encrypt(message, encoder=Base64Encoder)

        digest = hmac.digest(hkey, encrypted, sha256)
        self.writeCyphertext(digest, encrypted)
    
    def save(self) -> bool:
        try:
            with open("user-"+self.fid, "w") as f:
                dump([self.sk, self.follows, self.channels, self.known_hosts], f)
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
            user.addChannel(self.export())
            if not addAlias(cid, self.cid):
                print("could not create chat alias:", cid)
                exit(1)
        else:
            c = user.getChannel(cid)
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
        user.setChannel(self.export())
    def add_member(self, user, member):
        if self.members.__contains__(member):
            return
        self.members.append(member)
        user.setChannel(self.export())
    def is_owner(self, user: USER) -> bool:
        return self.owner == user.fid
    def export(self, share=False):
        if share:
            return [self.cid, self.owner, self.members, self.hkey, [self.dkeys[0]], self.seqno]
        return [self.cid, self.owner, self.members, self.hkey, self.dkeys, self.seqno]

def getMessageJSON(event, content) -> str:
    return '{"event": "'+event+'", "content": "'+content+'"}'

def checkSync(event) -> EVENT:
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

def checkInvite(data) -> []:
    try:
        if (data['event'] == 'chat/invite'):
            return eval(data['content'])
    except KeyError:
        return None

def checkRekey(data) -> str:
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
        if getIdByAlias(args.alias) != None:
            print("alias already existing, could not create user")
            exit(1)

        u = USER.new()
        if u != None:
            print("user created, id:", u.fid)
            u.createFeed()
            if not addAlias(args.alias, u.fid):
                print("could not save alias")
                exit(1)
            exit(0)
        else:
            print("could not create user")
            exit(1)
    
    fid = getIdByAlias(args.alias)
    if  fid != None:
        user = USER.byFid(fid)
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
        print('known_hosts', user.known_hosts)

    if args.action == 'follow' or args.action == 'unfollow' or args.action == 'invite':
        other_fid = getIdByAlias(args.other_alias)
        if  other_fid != None:
            other_user = USER.byFid(other_fid)
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
            c = getIdByAlias(args.chat_alias)
            if  c == None:
                print("chat alias not found")
                exit(1)
            user.invite(CHANNEL(user, c), other_fid)
    
    if args.action == 'log':
        user.log(args.raw)
    
    if args.action == 'chat':
        if user.createChannel(args.chat_alias):
            print('Secure team channel has been created!')
        else:
            print('Could not create chat!')
            exit(1)
    
    if args.action == 'message':
        c = getIdByAlias(args.chat_alias)
        if  c == None:
            print("chat alias not found")
            exit(1)
        c = CHANNEL(user, c)
        print('write your message and press enter...')
        user.writeTo(c, 'chat/message', sys.stdin.readline().splitlines()[0])
