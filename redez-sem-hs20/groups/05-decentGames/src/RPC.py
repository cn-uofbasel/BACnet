import socket
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer


class Server:

    def __init__(self):
        ip = socket.gethostbyname(socket.gethostname())
        port = 8001
        server = SimpleXMLRPCServer((ip, port))
        print("Listening on %s:%s..." % (ip, port))

        server.register_function(self.is_even, "is_even")
        server.register_function(self.react, "act")
        server.serve_forever()

    def is_even(self, path):
        with open(path, 'r') as f:
            game_info = f.readline()
        return game_info

    def react(self, path, ip):
        with xmlrpc.client.ServerProxy("http://%s:8001/" % ip) as proxy:
            file_string = proxy.is_even(path)
        with open(path, 'w') as f:
            f.write(file_string + '\n')
            f.close()


if __name__ == '__main__':
    Server()
