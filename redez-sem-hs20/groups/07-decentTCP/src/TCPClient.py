import socket
import sys
import struct
import os
from importlib import reload
from threading import Thread
import Parser as parser
from BaseHandler import BaseHandler

BUFFER_SIZE = 8192


class TCPClient(Thread):
    host = None
    port = None
    running = None

    def __init__(self, handler: BaseHandler):
        super().__init__()
        self.handler = handler
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("", 0))
        self.local_port = self.sock.getsockname()[1]
        self.connected = False

    def run(self):
        self.debug("Proxy started!")
        if not self.connected:
            self.dbg("Error, please use connect first.")
            return
        while self.running:
            data = self.sock.recv(BUFFER_SIZE)
            if data:
                self.handler.handle_tcp(data)

    def dbg(self, msg):
        print("[TCP-Client] {}".format(msg))
        pass

    def send(self, data):
        return self.sock.sendto(data, (self.host, self.port))

    def connect(self, host, port):
        self.host = host
        self.port = port
        self.sock.connect((self.host, self.port))
        self.connected = True
        self.running = True
        self.start()
        return True

    def stop(self):
        self.running = False
        self.sock.close()
        return True
