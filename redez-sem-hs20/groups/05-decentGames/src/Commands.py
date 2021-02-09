from Chess import Chess
from abc import ABC, abstractmethod
from Board import Board


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class Move(Command):

    def __init__(self, game: Chess, move: str) -> None:
        self.game = game
        self.__move = move

    def execute(self) -> None:
        if self.game.get_playable():
            self.game.move(self.__move)
            self.game.get_ginfo().inc_seq()
            self.game.set_playable(False)
        else:
            print('You cannot make a move. It is the turn of your opponent')


class Display(Command):
    def __init__(self, game: Chess) -> None:
        self.board: Board = Board(game.get_board())

    def execute(self) -> None:
        print(self.board)


class TurnOf(Command):
    def __init__(self, game: Chess) -> None:
        self.turn = game.get_turn_of()

    def execute(self) -> None:
        print(self.turn)


class WhoAmI(Command):
    def __init__(self, game: Chess) -> None:
        self.who_am_i = game.get_who_am_i()

    def execute(self) -> None:
        print(self.who_am_i)


class Allowed(Command):
    def __init__(self, game: Chess) -> None:
        self.moves = game.get_allowed_moves()

    def execute(self) -> None:
        print(self.moves)


class Dic(Command):
    def __init__(self, game: Chess) -> None:
        self.dic = game.get_dic()

    def execute(self) -> None:
        print(self.dic)


class Invoker:
    _command = None

    def set_command(self, command: Command):
        self._command = command

    def get_command(self) -> Command:
        return self._command

    def do(self):
        if self._command is not None:
            self._command.execute()
            self.set_command(None)
