import os
import getpass
import socket
import math
import json
import shutil
from browser import create, help_functions, inputhandler_old, help
from net.protocol import handle_message
from utils import color, hash_
from datetime import datetime


class Client:

    def __init__(self, IP = None):
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.IP = IP
            self.PORT = 65184
            self.filesystem_hash = None
            self.get_connection(IP)
        except BlockingIOError:
            self.server_socket.close()

    def disconnect_dialog(self, servername):
        while True:
            response = input(color.yellow("Disconnect from {}? [Y/N]: ".format(servername)))
            if help.check_if_alias(response, 'y'):
                return True
            elif help.check_if_alias(response, 'n'):
                return False

    def connect(self, IP):
        try:
            self.server_socket.connect((IP, self.PORT))
            return True
        except:
            return False

    def disconnect(self):
        try:
            self.server_socket.close()
        except:
            return False

    def get_connection(self, IP):
        if not IP:
            IP = input(color.green("Enter the IP of the server you want to connect to: "))
        try:
            self.server_socket.connect((IP, self.PORT))
        except:
            print(color.red("Unable to connect to {}".format(IP)))
            raise BlockingIOError

    def send(self, msg):
        self.server_socket.send(str.encode(msg))

    def send_bytes(self, bytes):
        self.server_socket.send(bytes)











