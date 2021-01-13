from threading import Thread

from TCPServer import ServerTCP
from TCPClient import ClientTCP


class TCPProxy(Thread):

    def __init__(self, server_host, port, server_port, name):
        super(TCPProxy, self).__init__()
        self.server_host = server_host
        self.port = port
        self.server_port = server_port
        self.name = name

    def run(self):
        while True:
            self.client_thread = ClientTCP(self.server_host, self.port, self.name)
            self.server_thread = ServerTCP(self.server_host, self.server_port, self.name)

            # Setting the connection between proxies
            self.client_thread.server_sock = self.server_thread.sock
            self.server_thread.client_sock = self.client_thread.sock

            self.client_thread.start()
            self.server_thread.start()
