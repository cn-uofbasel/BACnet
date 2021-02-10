import os
import sys

from Chess import Chess
from DontGetAngry import DontGetAngry
from IdkYet import GameLoop

if __name__ == '__main__':
    print('Hello, stranger!')
    while True:
        inp = input('Choose what to do:\n')
        args = inp.split(' ')
        command = args[0]
        game = args[1] if len(args) >= 2 else None
        arg = args[2] if len(args) == 3 else None
        print(game, arg)
        if command == '/play':
            if os.path.isfile('games/%s.dga' % arg) or os.path.isfile('games/%s.chess' % arg):
                print('in')
                GameLoop(game, arg)
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
            sys.exit(0)
