import sys

from AbsGame import AbsGame
from Chess import Chess
from Commands import Invoker, Display, Move, TurnOf, Allowed, Dic, WhoAmI


class GameLoop:

    def __init__(self, game_id: str):

        invoker = Invoker()
        game = Chess(game_id)
        while True:
            inp = input('What\'s your next move?\n')
            args = inp.split(' ')
            command = args[0]
            arg = args[1] if len(args) == 2 else None
            if command == '/display':
                invoker.set_command(Display(game))
            elif command == '/move':
                invoker.set_command(Move(game, arg))
            elif command == '/turnof':
                invoker.set_command(TurnOf(game))
            elif command == '/whoami':
                invoker.set_command(WhoAmI(game))
            elif command == '/allowed':
                invoker.set_command(Allowed(game))
            elif command == '/dinfo':
                invoker.set_command(Dic(game))
            elif command == '/q':
                print('See you again!')
                sys.exit(0)
            else:
                print('Wrong command, please try again.')

            invoker.do()
