import json
import socket
import xmlrpc.client
from xmlrpc.server import SimpleXMLRPCServer
import xmlrpc.client as rpc

from AbsGame import MY_IP


class RequestServer:

    def __init__(self):
        self.ip = MY_IP
        if self.ip == '127.0.0.1' or self.ip == '127.0.1.1' :
            self.ip = input(
                'You seem to be working on Linux. I only recognise your localhost, you have to enter your IP manually: '
            )
        port = 8001

        server = SimpleXMLRPCServer((self.ip, port), allow_none=True)
        print('Listening on %s:%s' % (self.ip, port))
        server.register_multicall_functions()
        server.register_function(RequestServer.game_request, 'game_request')
        server.register_function(RequestServer.game_is_updated, 'game_is_updated')
        server.register_function()
        server.serve_forever()

    @staticmethod
    def game_request(path) -> str:
        """
        The game file is requested by a machine.
        Parameters
        ----------
        path: The machines share the same location, but the server does not know where the file is, so it must be
        passed as an argument

        Returns
        -------
        The game information as a string
        """
        with open(path, 'r') as f:
            game_info = f.read().splitlines()[-1]
        print('Game has been requested')
        return game_info

    @staticmethod
    def fetching(path: str, seq_num: int):
        with open(path, 'r') as f:
            tmp = json.loads(f.read().splitlines()[-1].split('$')[1])['seq']
        print(tmp)

        diff = tmp - seq_num if tmp - seq_num > 0 else None
        if diff is not None:
            with open(path, 'r') as f:
                game_info = f.read().splitlines()[:-diff]
            print('Fetching %d lines' % diff)
            return game_info

        return []



    @staticmethod
    def game_is_updated(path, ip):
        """
        I get pinged that an update is made, therefore I request the update of the machine that pinged me.
        Parameters
        ----------
        path: The machines share the same location, but the server does not know where the file is, so it must be
        passed as an argument
        ip: This is the IP that pinged and from which I must request now.

        Returns
        -------

        """
        print('File got updated, I request now')
        print(ip)
        with rpc.ServerProxy("http://%s:8001/" % ip) as proxy:
            multicall = rpc.MultiCall(proxy)
            multicall.game_request(path)
            multicall()

        updated_game = tuple(multicall())[0]
        print('test ', updated_game)
        with open(path, 'a') as f:
            f.write(updated_game + '\n')
            f.close()
