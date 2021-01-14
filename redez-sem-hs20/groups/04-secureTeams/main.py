# create an identity    ./lib/crypto.py > alice-secret.key
# create a feed         ./lib/feed.py --keyfile alice-secret.key alice.pcap create
# append to feed        ./lib/feed.py --keyfile alice-secret.key alice.pcap append
# check feed            ./lib/feed.py --keyfile alice-secret.key alice.pcap check
# dump content          ./lib/pcap.py mixed.pcap

from nacl.public import PrivateKey, PublicKey, Box
from nacl.secret import SecretBox
from nacl.encoding import Base64Encoder
from nacl.bindings import crypto_sign_ed25519_pk_to_curve25519, crypto_sign_ed25519_sk_to_curve25519, crypto_scalarmult, randombytes
import nacl.utils

from json import dump, load, loads
import hmac
from hashlib import sha256

from feed import FEED
from event import EVENT
import crypto

class USER:
    def __init__(self, name):
        key_dir = 'keys/'
        key_path = key_dir+name+'.key'
        channel_dir = 'channel/'
        channels_path = channel_dir+name+'.channels'
        
        if not os.path.isfile(key_path):
            print("User keys not accessible. Creating new identity...")
            if not os.path.exists(key_dir):
                os.mkdir(key_dir)
            with open(key_path, "w") as f:
                key_pair = crypto.ED25519()
                key_pair.create()
                f.write('{\n  '+(',\n '.join(key_pair.as_string().split(','))[1:-1])+'\n}\n')
                print('new ED25519 key pair has been generated')

        try:
            with open(channels_path, 'r') as filehandle:
                channels = load(filehandle)
        except Exception:
            channels = []

        with open(key_path, 'r') as f:
            key = eval(f.read())
            if key['type'] == 'ed25519':
                self.name = name
                self.key_path = key_path
                self.channel_dir = channel_dir
                self.channels_path = channels_path
                self.channels = channels
                self.fid = bytes.fromhex(key['public'])
                self.signer = crypto.ED25519(bytes.fromhex(key['private']))
                self.digestmod = 'sha256'
                self.secretkey = self.signer.sk.to_curve25519_private_key()
                self.publickey = self.signer.sk.verify_key.to_curve25519_public_key()
            else:
                print('unknown key type')
                sys.exit()

    def add_channel(self, channel):
        with open(self.channels_path, 'w') as filehandle:
            self.channels.append(channel)
            dump(self.channels, filehandle)
    def channelConfigPath(self, channel):
        return 'channel/'+self.name+'-'+channel+'.state'
    def getFollows(self):
        try:
            with open(self.name+'.follows', "r") as f:
                a = load(f)
        except:
            a = []
        return a
    def follow(self, fid, alias):
        a = self.getFollows()
        with open(self.name+'.follows', "w") as f:
            a.append([fid, alias])
            dump(a,f)
        writeCleartext(u, getMessageJSON("log/follow", fid))
    def unfollow(self, fid):
        b = []
        for f in self.getFollows():
            if (f[0] != fid):
                b.append([f[0], f[1]])
        with open(self.name+'.follows', "w") as f:
            dump(b,f)
        writeCleartext(u, getMessageJSON("log/unfollow", fid))

class CHANNEL:
    def __init__(self, user: USER, name, new=False):
        if new:
            self.name = name
            self.owner = user.fid.hex()
            self.members = [[user.name, user.fid.hex()]]
            self.hkey = randombytes(16).hex()
            self.dkeys = [nacl.utils.random(SecretBox.KEY_SIZE).hex()]
            self.seqno = 0
            self.save(user)
            user.add_channel(name)
        else:
            try:
                with open(user.channelConfigPath(name), 'r') as filehandle:
                    data = load(filehandle)
                    self.name = data[0]
                    self.owner = data[1]
                    self.members = data[2]
                    self.hkey = data[3]
                    self.dkeys = data[4]
                    self.seqno = data[5]
            except Exception:
                print("unknown channel: ",name)
                sys.exit()

    def hkey_bytes(self):
        return bytes.fromhex(self.hkey)
    def dkeys_bytes(self):
        return list(map(lambda dk: bytes.fromhex(dk), self.dkeys))
    def generate_Dkey(self, user: USER):
        self.dkeys.append(nacl.utils.random(SecretBox.KEY_SIZE).hex())
        self.save(user)
    def add_member(self, user, member, alias):
        self.members.append([alias, member])
        self.save(user)
    def is_owner(self, user: USER):
        return self.owner == user.fid.hex()
    def save(self, user: USER):
        if not os.path.exists(user.channel_dir):
            os.mkdir(user.channel_dir)
        with open(user.channelConfigPath(self.name), 'w') as filehandle:
            dump([self.name, self.owner, self.members, self.hkey, self.dkeys, self.seqno], filehandle)

def writeFeed(user: USER, event):
    feed = FEED(user.name+'.pcap', user.fid, user.signer, True)
    if feed.pcap != None:
        feed.write(event)
    else:
        print('pcap error')
        sys.exit()

def writeCleartext(user: USER, cleartext):
    writeFeed(user, '{"cleartext": '+cleartext+'}')

def writeCyphertext(user: USER, digest, cyphertext):
    writeFeed(user, '{"hmac": "'+digest.hex()+'", "cyphertext": "'+cyphertext.hex()+'"}')

def getMessageJSON(event, content):
    return '{"event": "'+event+'", "content": "'+content+'"}'

#def some():
    #{’app’ : ’sch_mgmt’,’ref’: ref,’cmd’:’add’,’seqno’: self.seqno+1,’id’ : feed_id}

def writeTo(user: USER, channel: CHANNEL, event, content, r=None):
    if r!=None:
        key = bytes.fromhex(r)
        box =  Box(user.secretkey, PublicKey(crypto_sign_ed25519_pk_to_curve25519(PublicKey(key).__bytes__())))
        hkey = key
    else:
        box = SecretBox(channel.dkeys_bytes()[0])
        hkey = channel.hkey_bytes()
    message = getMessageJSON(event, content).encode('utf-8')
    encrypted = box.encrypt(message, encoder=Base64Encoder)

    digest = hmac.digest(hkey, encrypted, sha256)
    writeCyphertext(user, digest, encrypted)

def decrypt(user: USER, channels: [CHANNEL], event):
    # msg = '{"event": "app/action", "content": "xxx"}'
    # log_event = '{"hmac": "'+digest.hex()+'", "cyphertext": "'+encrypted.hex()+'"}'
    # log_event = {"cleartext": {"event": "chat/create", "content": "two"}}
    # log_event = {"cleartext": {"event": "log/sync", "content": "RAW_BACNET_EVENT"}}
    #print(event)
    e = getEvent(event)
    if (e!=None):
        # parse this content
        event = e.content()
        #return 'sync: ' + e.fid.hex() + ' ' + e.content().__repr__()
    data = loads(event)
    try:
        return 'cleartext: ' + data['cleartext']['event'] + ' ' + data['cleartext']['content']
    except KeyError:
        cypher = bytes.fromhex(data['cyphertext'])
        x = USER('default')#how to know sender? through list of follower? -> for loop if yes
        if bytes.fromhex(data['hmac']) == hmac.digest(x.fid, cypher, sha256):
            try:
                box = Box(x.secretkey, u.publickey)
                cleartext = box.decrypt(cypher, encoder=Base64Encoder)
                data = loads(cleartext)
                return 'cyphertext[private]: ' + data['event'] + ' ' + data['content']
            except nacl.exceptions.CryptoError:
                return 'cyphertext[private] -  error while decrypting private message'
        for c in channels:#loop through other channels hkey
            channel=c.name
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
                        return 'cyphertext['+channel+']: ' + data['event'] + ' ' + data['content']
                    except nacl.exceptions.CryptoError:
                        continue #perhaps there is another dkey
                return 'cyphertext['+channel+'] -  no dkey found (not member or private message)'
        return 'not cleartext nor matching a channel'

def create(user: USER, channel):
    if user.channels.__contains__(channel):
        print('channel already exists')
        return
    CHANNEL(user, channel, True)
    writeCleartext(user, getMessageJSON('chat/create', channel))

def getEvent(event) -> EVENT:
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

def log(user: USER, raw=False):
    f = FEED(user.name+'.pcap', user.fid, user.signer)
    if f.pcap == None:
        sys.exit()
    f.seq = 0
    f.hprev = None
    #print(f"Checking feed {f.fid.hex()}")
    channels = list(map(lambda c: CHANNEL(user, c), user.channels))
    for e in f:
        # print(e)
        if not f.is_valid_extension(e):
            print(f"-> event {f.seq+1}: chaining or signature problem")
        else:
            if raw:
                print(f"-> event {e.seq}: ok, content={e.content().__repr__()}")
            else:
                print(decrypt(user, channels, e.content()))
        f.seq += 1
        f.hprev = e.get_ref()

def replicate(user: USER):
    for follow in user.getFollows():
        remote = USER(follow[1])
        f = FEED(user.name+'.pcap', user.fid, user.signer)
        if f.pcap == None:
            return
        f.seq = 0
        f.hprev = None
        #print(f"Checking feed {f.fid.hex()}")
        maxSyncedSeq = 0
        for e in f:
            # print(e)
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq+1}: chaining or signature problem")
            else:
                """ if is cleartext log/sync from remote user, add to already sinced ones
                then go through the remote feed, and everything higher, paste into own feed as log sync """
                event = getEvent(e.content())
                if (event != None and event.fid == remote.fid):
                    maxSyncedSeq = event.seq
            
            f.seq += 1
            f.hprev = e.get_ref()
        
        f = FEED(remote.name+'.pcap', remote.fid, remote.signer)
        if f.pcap == None:
            sys.exit()
        f.seq = 0
        f.hprev = None
        #print(f"Checking feed {f.fid.hex()}")
        newMsgCount = 0
        for e in f:
            # print(e)
            if not f.is_valid_extension(e):
                print(f"-> event {f.seq+1}: chaining or signature problem")
            else:
                if (e.seq > maxSyncedSeq):
                    #only sync if it's not a sync entry of our own log
                    ev = getEvent(e.content())
                    if (ev == None or ev.fid != user.fid):
                        writeCleartext(u, getMessageJSON("log/sync", e.wire.hex()))
                        newMsgCount += 1
            
            f.seq += 1
            f.hprev = e.get_ref()
        if (newMsgCount > 0):
            print(newMsgCount, " messages synced from", remote.fid.hex())

def invite(user: USER, channel: CHANNEL, pk_joining, alias):
    if not channel.is_owner(user):
        print('you are not owner of this channel')
        sys.exit()
    channel.generate_Dkey(user) # rekey
    channel.add_member(user, pk_joining, alias)
    writeTo(user, channel, 'chat/add', channel.dkeys_bytes()[-1].hex()) # inform all members
    #todo: also send hmac and other details
    writeTo(user, channel, 'chat/invite', channel.dkeys_bytes()[-1].hex(), pk_joining) # inform new member with secrets

if __name__ == '__main__':
    import argparse
    import sys
    import os

    parser = argparse.ArgumentParser(description='Secure Team Chat')
    parser.add_argument('--user')
    parser.add_argument('--chat')
    parser.add_argument('CMD', choices=['create','invite','message','log','raw','follow','unfollow'])
    
    args = parser.parse_args()

    if args.user == None:
       print ("ERROR: --user required")
       exit(1)

    if (args.CMD == 'create' or args.CMD == 'invite' or args.CMD == 'message'):
        if (args.chat == None):
            print ("ERROR: --chat option required for this action")
            exit(1)

    u = USER(args.user)
    replicate(u)
    if args.CMD == 'create':
        if u.channels.__contains__(args.chat):
            print('channel already exists')
            exit(1)
        CHANNEL(u, args.chat, True)
        writeCleartext(u, getMessageJSON('chat/create', args.chat))
        print('Secure team channel has been created!')
        exit
        
    if args.CMD == 'log':
        log(u)
    elif args.CMD == 'raw':
        log(u, True)
    elif args.CMD == 'follow':
        print('type someone\'s id and press enter...')
        id = sys.stdin.readline().splitlines()[0]
        print('type an alias for this id and press enter...')
        alias = sys.stdin.readline().splitlines()[0]
        u.follow(id, alias)
    elif args.CMD == 'unfollow':
        u.unfollow(sys.stdin.readline().splitlines()[0])
    else:
        c = CHANNEL(u, args.chat)
        if args.CMD == 'message':
            print('write your message and press enter...')
            writeTo(u, c, 'chat/message', sys.stdin.readline().splitlines()[0])
        elif args.CMD == 'invite':
            print('type someone\'s id and press enter...')
            id = sys.stdin.readline().splitlines()[0]
            print('type an alias for this id and press enter...')
            alias = sys.stdin.readline().splitlines()[0]
            invite(u, c, id, alias)
