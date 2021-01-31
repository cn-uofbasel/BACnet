import socket
import sys
import struct
import os
from importlib import reload
from threading import Thread
import Parser as parser


class ServerTCP(Thread):
    def __init__(self, host, port, name):
        super(ServerTCP, self).__init__()
        self.host = host
        self.port = port
        self.name = name

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect((host, port))
        self.client_sock = None

    def run(self):
        self.debug("Proxy started!")
        while True:
            data = self.sock.recv(4096)
            if data:
                try:
                    reload(parser)
                    parser.parse(data, self.port, "server", self.name)
                except Exception as e:
                    self.debug(e)
                self.client_sock.sendall(data)

    def debug(self, msg):
        print("[{}-server_thread]({}): {}".format(self.name, self.port, msg))
        pass

    def send(self, data):
        return self.sock.sendto(data, (self.host, self.port))
