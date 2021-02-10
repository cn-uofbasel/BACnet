import socket
from xmlrpc.server import SimpleXMLRPCServer


class Server:

    def __init__(self):
        ip = socket.gethostbyname(socket.gethostname())
        port = 8001
        server = SimpleXMLRPCServer((ip, port))
        print("Listening on %s:%s..." % (ip, port))

        server.register_function(self.is_even, "is_even")
        server.serve_forever()

    def is_even(self, path):
        with open(path, 'r') as f:
            game_info = f.readline()
        return game_info


if __name__ == '__main__':
    Server()
