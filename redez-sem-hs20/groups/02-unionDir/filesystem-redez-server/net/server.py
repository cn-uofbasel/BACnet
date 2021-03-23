import socket
from net import client_list, client
from browser import unionpath

class Server:

    def __init__(self):
        self.unionpath = unionpath.Unionpath()
        self.Port = 65184
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.IP = self.getIP()
        self.clients = None

    def getIP(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        IP = s.getsockname()[0]
        s.close()
        return IP

    def run(self):
        self.clients = client_list.ClientList()
        try:
            print("IP: {} | Port: {}".format(self.IP, self.Port))
            self.server_socket.bind((self.IP, self.Port))
            self.server_socket.listen(20)
            while True:
                conn, addr = self.server_socket.accept()
                add_client = client.Client(conn, addr, self.unionpath)
                self.clients.add(add_client.hash, client)
        except KeyboardInterrupt:
            self.clients.send_all("DEN")