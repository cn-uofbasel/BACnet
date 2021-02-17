import os
import socket
import sys

from AbsGame import AbsGame
from Chess import Chess
from DontGetAngry import DontGetAngry
from IdkYet import GameLoop
from RPC import RequestServer
import xmlrpc.client as rpc
import _thread as t



def initialise_server():
    RequestServer()


if __name__ == '__main__':
    print('Hello, stranger!')
    while True:
        inp = input('Choose what to do: ')
        args = sys.argv
        inputs = inp.split(' ')
        command = inputs[0] if len(inputs) >= 1 else None
        arg = inputs[1] if len(inputs) == 2 else None
        game = args[1] if len(args) >= 2 else None
        ip1 = args[2] if len(args) >= 3 else None
        ip2 = args[3] if len(args) == 4 else None
        print(game, arg)
        print(ip1, ip2)
        if command == '/play':
            if os.path.isfile('games/%s.dga' % arg) or os.path.isfile('games/%s.chess' % arg):
                print('in')
                GameLoop(game, arg, ip1, ip2)
            else:
                print('This games does not exist, please try again.')

        elif command == '/create':
            if game == 'chess':
                Chess.create(arg)
            elif game == 'dga':
                DontGetAngry.create(arg)
            else:
                print('Wrong Input?')
                continue
            print('Game created!')
            RequestServer()
        elif command == '/request':
            if not os.path.isfile('games/%s.%s' % (arg, game)):
                DontGetAngry.create(arg)
            t.start_new_thread(initialise_server, ())
            AbsGame.request_new_game_file('games/%s.%s' % (arg, game), ip1)
