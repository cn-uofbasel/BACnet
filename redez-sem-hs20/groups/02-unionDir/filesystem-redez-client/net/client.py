import socket
from browser import help
from utils import color

class Client:

    def __init__(self):
        try:
            self.server_socket = None
            self.IP = None
            self.PORT = 65184
            self.connect_status = False
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
            self.server_socket = None
            self.connect_status = False
        except:
            return False

    def get_connection(self, IP=None):
        if not IP:
            IP = input(color.green("Enter the IP of the server you want to connect to: "))
        try:
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.connect((IP, self.PORT))
            self.IP = IP
            self.connect_status = True
        except:
            self.server_socket = None
            print(color.red("Unable to connect to {}".format(IP)))
            raise BlockingIOError

    def send(self, msg):
        self.server_socket.send(str.encode(msg))

    def send_bytes(self, bytes):
        self.server_socket.send(bytes)











