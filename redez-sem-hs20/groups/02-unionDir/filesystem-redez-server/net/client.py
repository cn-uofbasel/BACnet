from net import protocol
from utils import color
import _thread
from pathlib import Path

BUFFER_SIZE = 8 * 1024

class Client:
    def __init__(self, conn, addr, unionpath):
        self.socket = conn
        self.addr = addr
        self.IP = self.addr[0]
        self.unionpath = unionpath
        self.protocol = protocol.Protocol(self, self.unionpath)
        self.hash = None
        self.username = None
        _thread.start_new_thread(self.client_thread, ())

    def client_thread(self):
        while True:
            message = self.socket.recv(2048)
            if message:
                self.send(self.protocol.handle(message.decode('utf-8')))

    def send(self, msg):
        if msg:
            self.socket.send(str.encode(msg))

    def send_bytes(self, bytes):
        self.socket.send(bytes)

    def get(self):
        return self.socket.recv(2048).decode('utf-8')


