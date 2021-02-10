from xmlrpc.server import SimpleXMLRPCServer


class Server:

    def __init__(self):
        server = SimpleXMLRPCServer(('192.168.0.103', 8001))
        print("Listening on port 8000...")

        server.register_function(self.is_even, "is_even")
        server.serve_forever()

    def is_even(self, path):
        with open(path, 'r') as f:
            game_info = f.readline()
        return game_info


if __name__ == '__main__':
    Server()
