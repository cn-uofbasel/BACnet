import json
import select
import socket
import sys, os
import getopt
import time
from threading import Thread
import queue

from nacl.bindings import crypto_sign_ed25519_pk_to_curve25519
from nacl.public import PublicKey

from lib import crypto
from lib.feed import FEED

CONFIG_DIR = ".bacnet-proxy/"
DATA_DIR = CONFIG_DIR + "data/"
AUTH_FEEDS = CONFIG_DIR + ".authorized_feeds"


class BACNETTCP():

    def __init__(self, alias=None):
        try:
            os.mkdir(CONFIG_DIR)

        except FileExistsError:
            pass
        try:
            os.mkdir(DATA_DIR)
        except FileExistsError:
            pass
        if alias is None:
            alias = "proxy"
        self.fid = {}
        self.sk = {}
        self.alias = alias
        self.get_or_create_feed()
        self.load_authorized_feeds()

    def get_or_create_feed(self):
        self.setup_feed_crypto(self.alias)
        initialized = os.path.isfile(CONFIG_DIR +  self.fid[self.alias] + ".pcap")
        if not initialized:
            self.master_feed = FEED(CONFIG_DIR + self.fid[self.alias] + ".pcap", bytes.fromhex(self.fid[self.alias]),
                                    self.get_signer(self.alias), True)
            if self.master_feed.pcap is None:
                print('error: could not create pcap')
                exit(1)
            self.master_feed.write(self.to_json("log/init", ""))
            sys.exit()
        else:
            self.master_feed = FEED(CONFIG_DIR + self.fid[self.alias] + ".pcap", bytes.fromhex(self.fid[self.alias]),
                                    self.get_signer(self.alias))

    def setup_feed_crypto(self, alias, dir=CONFIG_DIR):
        fid_path = dir + alias + ".fid"
        sk_path = dir + alias + ".sk"
        fid_exists = os.path.isfile(fid_path)
        sk_exists = os.path.isfile(sk_path)
        if fid_exists and sk_exists:
            f = open(fid_path, "r")
            self.fid[alias] = f.readline()
            f.close()
            f = open(sk_path, "r")
            self.sk[alias] = f.readline()
            f.close()
        else:
            key_pair = crypto.ED25519()
            key_pair.create()
            self.fid[alias] = key_pair.get_public_key().hex()
            self.sk[alias] = key_pair.get_private_key().hex()
            f = open(fid_path, "w")
            f.write(self.fid[alias])
            f.close()
            f = open(sk_path, "w")
            f.write(self.sk[alias])
            f.close()

    def get_signer(self, alias):
        return crypto.ED25519(bytes.fromhex(self.sk[alias]))

    def to_json(self, event, content):
        return json.dumps({"event": event, "content": content})

    def load_authorized_feeds(self):
        self.authorized_feeds = []
        if os.path.isfile(CONFIG_DIR + ".authorized_feeds"):
            f = open(CONFIG_DIR + ".authorized_feeds", "r")
            for line in f:
                self.authorized_feeds.append(line.strip())
                self.setup_data_feed(line.strip())
    def bacnet_watchdog(self):
        old_seq = {}
        self.tcp_threads = {}
        for authorized_feed in self.authorized_feeds:
            old_seq[authorized_feed] = -1

        while True:
            for authorized_feed in self.authorized_feeds:
                if os.path.isfile(authorized_feed + ".pcap"):
                    temp_feed = FEED(authorized_feed + ".pcap",
                                     bytes.fromhex(authorized_feed),
                                     PublicKey(crypto_sign_ed25519_pk_to_curve25519(bytes.fromhex(authorized_feed))))
                    if old_seq[authorized_feed] != temp_feed.seq and old_seq[authorized_feed] >= 0:
                        temp_feed.seq = 0
                        temp_feed.hprev = None
                        for e in temp_feed:
                            if not temp_feed.is_valid_extension(e):
                                print(f"-> event {temp_feed.seq + 1}: chaining or signature problem")
                            else:
                                if temp_feed.seq == old_seq[authorized_feed]:

                                    e_content = json.loads(e.content())
                                    if e_content['event'] == "tcp/open":
                                        host = e_content['content']['host']
                                        port = int(e_content['content']['port'])
                                        self.setup_data_feed(authorized_feed)

                                        if not authorized_feed in self.tcp_threads.keys():
                                            self.tcp_threads[authorized_feed] = {}
                                            self.tcp_threads[authorized_feed]['tasks'] = queue.Queue()
                                            self.tcp_threads[authorized_feed]['thread'] = Thread(
                                                target=self.tcp_watchdog,
                                                args=(authorized_feed, host, port))
                                            self.tcp_threads[authorized_feed]['thread'].start()
                                    elif e_content['event'] == "tcp/write":
                                        if authorized_feed in self.tcp_threads.keys():
                                            self.tcp_threads[authorized_feed]['tasks'].put(e_content)
                                    elif e_content['event'] == "tcp/close":
                                        if authorized_feed in self.tcp_threads.keys():
                                            self.tcp_threads[authorized_feed]['tasks'].put(e_content)
                            if old_seq[authorized_feed] < temp_feed.seq:
                                break
                            temp_feed.seq += 1
                            temp_feed.hprev = e.get_ref()
                    old_seq[authorized_feed] = temp_feed.seq
            time.sleep(1)

    def tcp_watchdog(self, client_feed, host, port):
        print("connecting to {}:{}".format(host, port))

        data_fid = self.get_data_feed(client_feed)
        my_alias =  None
        for alias, fid in self.fid.items():
            if fid == data_fid:
                my_alias = alias
                break

        if my_alias is not None:
            data_feed = FEED(DATA_DIR + data_fid + ".pcap",
                             bytes.fromhex(data_fid),self.get_signer(my_alias))
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.connect((host, port))
                # s.setblocking(False)
                inputs = [s]
                while True:
                    readable, writable, exceptional = select.select(inputs, [], inputs, 0.1)
                    for sock in readable:
                        if sock == s:
                            data = s.recv(1024)
                            data_feed.write(
                                self.to_json("tcp/recv", {"data": data.hex(), "client_fid": client_feed}))
                    try:
                        next_msg = self.tcp_threads[client_feed]['tasks'].get_nowait()
                    except queue.Empty:
                        continue
                    else:
                        if next_msg['event'] == "tcp/close":
                            s.close()
                            break
                        s.send(next_msg['content']['data'].encode())
            self.tcp_threads[client_feed] = None
            del self.tcp_threads[client_feed]
            print("connection closed!")

    def start(self):
        bacnet_thread = Thread(target=self.bacnet_watchdog)
        bacnet_thread.start()

    def setup_data_feed(self, other_feed):
        alias_old = other_feed
        alias = alias_old + "_data"
        self.setup_feed_crypto(alias, dir=DATA_DIR)
        initialized = os.path.isfile(DATA_DIR + self.fid[alias] + ".pcap")
        if not initialized:
            data_feed = FEED(DATA_DIR + self.fid[alias] + ".pcap", bytes.fromhex(self.fid[alias]),
                             self.get_signer(alias), True)
            if data_feed.pcap is None:
                print('error: could not create pcap')
                exit(1)
            data_feed.write(self.to_json("log/init", ""))
            self.master_feed.write(self.to_json("data/init", {"client_fid": other_feed, "data_fid": self.fid[alias]}))

    def get_data_feed(self, other_feed):
        temp_feed = self.master_feed
        temp_feed.seq = 0
        temp_feed.hprev = None
        ret = None
        for e in temp_feed:
            if not temp_feed.is_valid_extension(e):
                print(f"-> event {temp_feed.seq + 1}: chaining or signature problem")
            else:
                e_content = json.loads(e.content())
                if ret is None:
                    if e_content['event'] == "data/init":
                        if other_feed == e_content['content']['client_fid']:
                            ret = e_content['content']['data_fid']
            temp_feed.seq += 1
            temp_feed.hprev = e.get_ref()
        return ret



def authorize(fid, alias="proxy"):
    print("[BACnetTCP] auth feed: " + fid)
    try:
        os.mkdir(CONFIG_DIR)

    except FileExistsError:
        pass
    try:
        os.mkdir(DATA_DIR)
    except FileExistsError:
        pass
    f = open(AUTH_FEEDS, "a")
    f.write(fid + "\n")
    f.close()


if __name__ == '__main__':
    opts, args = getopt.getopt(sys.argv[1:], "ha:", ["help", "authorize"])
    current_action = None
    current_alias = "proxy"
    for opt, arg in opts:
        if opt in ("-h", "--help"):
            print("TODO: Help")
            sys.exit()
        elif opt in ("-a", "--authorize"):
            if current_action is None:
                authorize(arg,alias=current_alias)
                bacnet_tcp = BACNETTCP(alias=current_alias)
                current_action = "auth"

    if current_action is None:
        bacnet_tcp = BACNETTCP(alias=current_alias)
        bacnet_tcp.start()
