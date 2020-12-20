import socket
import sys
import struct
import os
from importlib import reload
from threading import Thread
import Parser as parser


class ClientTCP(Thread):
    def __init__(self, host, port, name):
        super(ClientTCP, self).__init__()
        self.host = host
        self.port = port
        self.name = name

        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind(("0.0.0.0", self.port))
        sock.listen(1)
        self.sock, addr = sock.accept()
        self.server_sock = None

    def run(self):
        self.debug("Proxy started!")
        while True:
            data = self.sock.recv(4096)
            if data:
                try:
                    reload(parser)
                    parser.parse(data, self.port, "client", self.name)
                except Exception as e:
                    self.debug(e)
                self.server_sock.sendall(data)

    def debug(self, msg):
        print("[{}-client_thread]({}): {}".format(self.name, self.port, msg))
        pass

    def send(self, data):
        return self.sock.sendto(data, (self.host, self.port))
