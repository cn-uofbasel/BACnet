from abc import ABC, abstractmethod

from GameInformation import GameInformation


class AbsGame(ABC):

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
    def get_dic(self):
        pass

    @abstractmethod
    def get_playable(self):
        pass

    @abstractmethod
    def set_playable(self, state: bool):
        pass

    @abstractmethod
    def move(self, move: str):
        pass

    @abstractmethod
    def get_ginfo(self) -> GameInformation:
        pass

    @abstractmethod
    def update(self) -> None:
        pass
