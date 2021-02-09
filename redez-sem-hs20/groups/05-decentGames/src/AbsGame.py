from abc import ABC, abstractmethod

from GameInformation import GameInformation


class AbsGame(ABC):

    # Methods for the command class------------------------------------------------------------------------------------
    @abstractmethod
    def get_board(self) -> str:
        pass

    @abstractmethod
    def get_turn_of(self) -> str:
        pass

    @abstractmethod
    def get_who_am_i(self) -> str:
        pass

    @abstractmethod
    def get_allowed_moves(self):
        pass

    @abstractmethod
    def move(self, move: str):
        pass

    @abstractmethod
    def get_ginfo(self) -> GameInformation:
        pass

    @abstractmethod
    def forfeit(self):
        pass

    # Enforced methods for the game-------------------------------------------------------------------------------------
    @abstractmethod
    def __get_playable(self):
        pass

    @abstractmethod
    def __set_playable(self, state: bool):
        pass

    @abstractmethod
    def __update(self) -> None:
        pass

    @abstractmethod
    def __validate(self, fen: str) -> bool:
        pass

    @abstractmethod
    def __get_turn_of(self) -> str:
        pass

    @abstractmethod
    def __get_game_id(self) -> str:
        pass

    @abstractmethod
    def __sync_log(self) -> None:
        pass
