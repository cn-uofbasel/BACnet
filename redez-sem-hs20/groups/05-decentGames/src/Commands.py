from AbsGame import AbsGame
from abc import ABC, abstractmethod
from Board import Board
import State


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class Move(Command):

    def __init__(self, game: AbsGame, move: str) -> None:
        self.game = game
        self.__move = move

    def execute(self) -> None:
        if self.game.get_playable():
            self.game.get_ginfo().inc_seq()
            self.game.move(self.__move)
            self.game.set_playable(False)
            self.game.update()
        else:
            print('You cannot make a move. It is the turn of your opponent')


class Display(Command):
    def __init__(self, game: AbsGame) -> None:
        self.board: Board = Board(game.get_board())

    def execute(self) -> None:
        print(self.board)


class TurnOf(Command):
    def __init__(self, game: AbsGame) -> None:
        self.turn = game.get_turn_of()

    def execute(self) -> None:
        print(self.turn)


class WhoAmI(Command):
    def __init__(self, game: AbsGame) -> None:
        self.who_am_i = game.get_who_am_i()

    def execute(self) -> None:
        print(self.who_am_i)


class Allowed(Command):
    def __init__(self, game: AbsGame) -> None:
        self.moves = game.get_allowed_moves()

    def execute(self) -> None:
        print(self.moves)


class Dic(Command):
    def __init__(self, game: AbsGame) -> None:
        self.dic = game.get_ginfo()

    def execute(self) -> None:
        print(self.dic)


class Forfeit(Command):
    def __init__(self, game: AbsGame) -> None:
        self.game = game

    def execute(self) -> None:
        if self.game.get_ginfo().get_status() == State.ONGOING:
            self.game.get_ginfo().set_status(State.FF)
            self.game.get_ginfo().set_ff(self.game.get_who_am_i())
            self.game.get_ginfo().set_winner('p1' if self.game.get_who_am_i() == 'p2' else 'p2')
            self.game.get_ginfo().set_loser(self.game.get_who_am_i())
            self.game.update()
        else:
            print('Game ended already. You cannot forfeit.')


class Status(Command):
    def __init__(self, game: AbsGame) -> None:
        self.game = game

    def execute(self) -> None:
        if self.game.get_ginfo().get_status() == State.FF:
            print('%s gave up. Winner is %s' % (self.game.get_ginfo().get_loser(), self.game.get_ginfo().get_winner()))

        if self.game.get_ginfo().get_status() == State.FINISHED:
            print('Winner of the game is %s' % (self.game.get_ginfo().get_winner()))

        if self.game.get_ginfo().get_status() == State.CHEATED:
            print('Winner of the game is %s due to cheating of opponent.' % (self.game.get_ginfo().get_winner()))


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
