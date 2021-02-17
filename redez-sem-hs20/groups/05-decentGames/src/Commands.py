from AbsGame import AbsGame
from abc import ABC, abstractmethod
from Board import Board
import State
from Chess import Chess
from DGABoard import DGABoard
from DontGetAngry import DontGetAngry

"""
The Command Design Pattern was used to generate separately commands/functions for all 1v1 games (the abstract form of 
the games is used in the methods).

"""


class Command(ABC):
    @abstractmethod
    def execute(self) -> None:
        pass


class Move(Command):
    """
    Makes the move that is necessary to continue the game.
    """

    def __init__(self, game: AbsGame, move: str) -> None:
        self.game = game
        self.__move = move

    def execute(self) -> None:
        self.game.move(self.__move)


class Display(Command):
    """
    Displays the board of the given game in the console.
    """
    def __init__(self, game: AbsGame) -> None:
        if isinstance(game, Chess):
            self.board: Board = Board(game.get_board())
        if isinstance(game, DontGetAngry):
            self.board: DGABoard = DGABoard(game.get_board())

    def execute(self) -> None:
        print(self.board)


class TurnOf(Command):
    """
    Displays who's turn it is right now.
    """
    def __init__(self, game: AbsGame) -> None:
        self.turn = game.get_turn_of()

    def execute(self) -> None:
        print(self.turn)


class WhoAmI(Command):
    """
    Displays which player I am.
    """
    def __init__(self, game: AbsGame) -> None:
        self.who_am_i = game.get_who_am_i()

    def execute(self) -> None:
        print(self.who_am_i)


class Allowed(Command):
    """
    Displays all allowed moves (will be eventually deleted as command).
    """
    def __init__(self, game: AbsGame) -> None:
        self.moves = game.get_allowed_moves()

    def execute(self) -> None:
        print(self.moves)


class GInfo(Command):
    """
    Displays the JSON construct of the game information
    """
    def __init__(self, game: AbsGame) -> None:
        self.ginfo = game.get_ginfo()

    def execute(self) -> None:
        print(self.ginfo)


class Forfeit(Command):
    def __init__(self, game: AbsGame) -> None:
        self.game = game

    def execute(self) -> None:
        self.game.forfeit()


class Status(Command):
    """
    Displays the status of the game (not who's turn it is)
    """
    def __init__(self, game: AbsGame) -> None:
        self.game = game

    def execute(self) -> None:
        if self.game.get_ginfo().get_status() == State.FF:
            print('%s gave up. Winner is %s' % (self.game.get_ginfo().get_loser(), self.game.get_ginfo().get_winner()))

        if self.game.get_ginfo().get_status() == State.FINISHED:
            print('Winner of the game is %s' % (self.game.get_ginfo().get_winner()))

        if self.game.get_ginfo().get_status() == State.CHEATED:
            print('Winner of the game is %s due to cheating of opponent.' % (self.game.get_ginfo().get_winner()))

        if self.game.get_ginfo().get_status() == State.ONGOING:
            print('Game is still going on.')


class Refresh(Command):

    def __init__(self, game: AbsGame):
        self.game = game

    def execute(self) -> None:
        self.game.refresh()


class Fetch(Command):

    def __init__(self, game: AbsGame):
        self.game = game

    def execute(self) -> None:
        self.game.fetch()


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
