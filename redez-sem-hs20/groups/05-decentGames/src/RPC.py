import socket
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer


class Server:

    def __init__(self):
        ip = socket.gethostbyname(socket.gethostname())
        port = 8001
        server = SimpleXMLRPCServer((ip, port))
        print("Listening on %s:%s..." % (ip, port))
        server.register_multicall_functions()
        server.register_function(self.is_even, "is_even")
        server.register_function(self.react, "react")
        server.serve_forever()

    def is_even(self, path):
        with open(path, 'r') as f:
            game_info = f.readline()
        return game_info

    def react(self, path, ip):
        print('here')
        print(ip)
        with xmlrpc.client.ServerProxy("http://%s:8001/" % ip) as proxy:
            multicall = xmlrpc.client.MultiCall(proxy)
            multicall.is_even(path)
            file_string = tuple(multicall())[0]
        with open(path, 'w') as f:
            f.write(file_string + '\n')
            f.close()
        print('end')
        return 'meh'


if __name__ == '__main__':
    Server()
