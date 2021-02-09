import os
import sys

from Chess import Chess
from IdkYet import GameLoop

if __name__ == '__main__':
    print('Hello, stranger!')
    while True:
        inp = input('Choose what to do:\n')
        args = inp.split(' ')
        command = args[0]
        arg = args[1] if len(args) == 2 else None

        if command == '/play':
            if os.path.isfile('games/%s.chess' % arg):
                GameLoop(arg)
            else:
                print('This games does not exist, please try again.')

        elif command == '/create':
            Chess.create(arg)
            print('Game created!')
            sys.exit(0)
