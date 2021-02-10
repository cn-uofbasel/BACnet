from abc import ABC, abstractmethod
from datetime import datetime

from GameInformation import GameInformation


class AbsGame(ABC):

    # Methods for the command class------------------------------------------------------------------------------------
    @abstractmethod
    def get_board(self):
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
    def _get_playable(self):
        pass

    @abstractmethod
    def _set_playable(self, state: bool):
        pass

    @abstractmethod
    def _update(self) -> None:
        pass

    @abstractmethod
    def _validate(self, fen: str) -> bool:
        pass

    @abstractmethod
    def _get_turn_of(self) -> str:
        pass

    @abstractmethod
    def _get_game_id(self) -> str:
        pass

    @abstractmethod
    def _sync_log(self) -> None:
        pass

    @staticmethod
    def get_time() -> str:
        return datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + '$'

    @abstractmethod
    def request(self):
        pass
