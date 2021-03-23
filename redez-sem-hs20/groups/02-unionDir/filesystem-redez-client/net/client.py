import socket
from browser import help
from utils import color
from net import protocol

class Client:

    def __init__(self, unionpath):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.IP = None
        self.PORT = 65184
        self.unionpath = unionpath

    def connect(self, IP):
        try:
            self.server_socket.connect((IP, self.PORT))
            self.IP = IP
            self.unionpath.connected = True
            return True
        except:
            return False

    def disconnect(self):
        try:
            self.server_socket.close()
            self.server_socket = None
        except:
            return False

    def send(self, msg):
        if self.unionpath.connected:
            self.server_socket.send(str.encode(msg))

    def send_bytes(self, bytes):
        if self.unionpath.connected:
            self.server_socket.send(bytes)











