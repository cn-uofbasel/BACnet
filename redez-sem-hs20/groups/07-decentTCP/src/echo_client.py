import json
import os, sys
import time

from nacl.bindings import crypto_sign_ed25519_pk_to_curve25519
from nacl.public import PublicKey

from lib import crypto
from lib.feed import FEED

CONFIG_DIR = ".bacnet-proxy/"
DATA_DIR = CONFIG_DIR + "data/"
AUTH_FEEDS = CONFIG_DIR + ".authorized_feeds"


class CLIENT:

    def __init__(self, remote_fid=None, alias="cool_feed_id"):
        self.alias = alias
        self.remote_fid = remote_fid
        self.get_or_create_feed()
        if self.remote_fid is not None:
            if self.get_remote_data_feed() is not None:
                self.remote_seq = self.get_remote_data_feed().seq
            else:
                self.remote_seq = -1
        else:
            sys.exit()

    def get_remote_feed(self):
        remote_feed = None
        if os.path.isfile(CONFIG_DIR + self.remote_fid + ".pcap"):
            remote_feed = FEED(CONFIG_DIR + self.remote_fid + ".pcap",
                               bytes.fromhex(self.remote_fid),
                               PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(self.remote_fid))))
        return remote_feed

    def get_remote_data_feed(self):
        remote_feed = None
        if self.get_data_feed() is not None:
            if os.path.isfile( DATA_DIR + self.get_data_feed() + ".pcap"):
                remote_feed = FEED(DATA_DIR + self.get_data_feed() + ".pcap",
                                   bytes.fromhex(self.get_data_feed()),
                                   PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(self.get_data_feed()))))
        return remote_feed

    def get_or_create_feed(self):
        self.setup_feed_crypto()
        initialized = os.path.isfile(self.fid + ".pcap")
        if not initialized:
            self.feed = FEED(self.fid + ".pcap", bytes.fromhex(self.fid), self.get_signer(), True)
            if self.feed.pcap is None:
                print('error: could not create pcap')
                exit(1)
            self.feed.write(self.to_json("log/init", ""))
            sys.exit()
        else:
            self.feed = FEED(self.fid + ".pcap", bytes.fromhex(self.fid), self.get_signer())

    def setup_feed_crypto(self):
        fid_path = self.alias + ".fid"
        sk_path = self.alias + ".sk"
        fid_exists = os.path.isfile(fid_path)
        sk_exists = os.path.isfile(sk_path)
        if fid_exists and sk_exists:
            f = open(fid_path, "r")
            self.fid = f.readline()
            f.close()
            f = open(sk_path, "r")
            self.sk = f.readline()
            f.close()
        else:
            key_pair = crypto.ED25519()
            key_pair.create()
            self.fid = key_pair.get_public_key().hex()
            self.sk = key_pair.get_private_key().hex()
            f = open(fid_path, "w")
            f.write(self.fid)
            f.close()
            f = open(sk_path, "w")
            f.write(self.sk)
            f.close()

    def get_signer(self):
        return crypto.ED25519(bytes.fromhex(self.sk))

    def to_json(self, event, content):
        return json.dumps({"event": event, "content": content})

    def open(self, host, port):
        self.feed.write(self.to_json("tcp/open", {'host': host, 'port': port, 'alias': self.alias}))

    def wr(self, data):
        self.feed.write(self.to_json("tcp/write", {'data': data}))

    def rd(self):
        remote_temp = self.get_remote_data_feed()
        ret = None
        if remote_temp is not None:
            while self.remote_seq == remote_temp.seq:
                remote_temp = self.get_remote_data_feed()
            remote_temp.seq = 0
            remote_temp.hprev = None

            for e in remote_temp:
                if not remote_temp.is_valid_extension(e):
                    print(f"-> event {remote_temp.seq + 1}: chaining or signature problem")
                else:
                    if ret is None:
                        if self.remote_seq < remote_temp.seq + 1:
                            e_content = json.loads(e.content())
                            if e_content['content']['client_fid'] == self.fid:
                                self.remote_seq = remote_temp.seq + 1
                                ret = bytes.fromhex(e_content['content']['data'])
                remote_temp.seq += 1
                remote_temp.hprev = e.get_ref()
        return ret
    def close(self):
        self.feed.write(self.to_json("tcp/close", {}))

    def get_data_feed(self):
        temp_feed = self.get_remote_feed()
        ret = None
        if temp_feed is not None:
            temp_feed.seq = 0
            temp_feed.hprev = None

            for e in temp_feed:
                if not temp_feed.is_valid_extension(e):
                    print(f"-> event {temp_feed.seq + 1}: chaining or signature problem")
                else:
                    e_content = json.loads(e.content())
                    if ret is None:
                        if e_content['event'] == "data/init":
                            if self.fid == e_content['content']['client_fid']:
                                ret = e_content['content']['data_fid']
                temp_feed.seq += 1
                temp_feed.hprev = e.get_ref()
        return ret

if __name__ == '__main__':
    MASTER_FEED = "46bf7c88304d90dfca55a4fabb67ead3f208ae2629ff7c20d0a4d722c2199bf5"
    if len(sys.argv) > 1:
        client = CLIENT(alias=sys.argv[1], remote_fid=MASTER_FEED)
        client.open("buerkl.in", 22014)
        out = client.rd()
        print(out)
        client.wr("zeile einsAAA")
        client.wr("zeile einsAABBBA")
        if out is not None:
            time.sleep(10)
    else:
        client = CLIENT(remote_fid=MASTER_FEED)
        client.open("buerkl.in", 22014)
        print(client.rd())
        client.wr("zeile einsA")

        client.wr("zeile einsB")

    print(client.rd())
    print(client.rd())
    client.close()