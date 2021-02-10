import sys

from AbsGame import AbsGame
from Chess import Chess
from Commands import Invoker, Display, Move, TurnOf, Allowed, GInfo, WhoAmI, Forfeit, Status, Request
from DontGetAngry import DontGetAngry


class GameLoop:

    def __init__(self, type_of_game: str, game_id: str):

        invoker = Invoker()
        if type_of_game == 'chess':
            game = Chess(game_id)
        elif type_of_game == 'dga':
            game = DontGetAngry(game_id)
        else:
            return

        while True:
            inp = input('What\'s your next command?\n')
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
                invoker.set_command(GInfo(game))
            elif command == '/ff':
                invoker.set_command(Forfeit(game))
            elif command == '/status':
                invoker.set_command(Status(game))
            elif command == '/request':
                invoker.set_command(Request(game))
                invoker.do()
                if type_of_game == 'chess':
                    game = Chess(game_id)
                elif type_of_game == 'dga':
                    game = DontGetAngry(game_id)
                else:
                    return
                continue
            elif command == '/q':
                print('See you again!')
                sys.exit(0)
            else:
                print('Wrong command, please try again.')

            invoker.do()
