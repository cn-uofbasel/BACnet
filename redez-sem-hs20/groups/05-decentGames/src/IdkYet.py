import sys

from AbsGame import AbsGame
from Chess import Chess
from Commands import Invoker, Display, Move, TurnOf, Allowed, GInfo, WhoAmI, Forfeit, Status, Refresh, Fetch
from DontGetAngry import DontGetAngry
from RPC import RequestServer
import _thread as t


def initialise_server():
    RequestServer()


class GameLoop:

    def __init__(self, type_of_game: str, game_id: str, ip1: str, ip2: str):

        invoker = Invoker()
        if type_of_game == 'chess':
            game = Chess(game_id, ip1)
        elif type_of_game == 'dga':
            game = DontGetAngry(game_id, ip1, ip2)
        else:
            return
        while game.is_looping:
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
            elif command == '/fetch':
                invoker.set_command(Fetch(game))
            elif command == '/refresh':
                invoker.set_command(Refresh(game))
                invoker.do()
                if type_of_game == 'chess':
                    game = Chess(game_id, ip1)
                elif type_of_game == 'dga':
                    game = DontGetAngry(game_id, ip1, ip2)
                else:
                    return
                continue
            elif command == '/q':
                print('See you again!')
                sys.exit(0)
            else:
                print('Wrong command, please try again.')

            invoker.do()
