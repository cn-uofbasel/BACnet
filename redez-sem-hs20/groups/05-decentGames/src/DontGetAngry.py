import json

from AbsGame import AbsGame
from DGA import DGA
from GameInformation import GameInformation


class DontGetAngry(AbsGame):

    def __init__(self, game_id: str):
        self.__game_id = game_id
        self.__game_path = 'games/%s.dag' % game_id
        self.__log_path = 'logs/log_dag_%s.dlog' % game_id

        self.__playable = False
        self.__game_is_updated = False

        self.__ginfo: GameInformation = None

        if game_id is not None:
            with open(self.__game_path, 'r') as f:
                game_info = f.readline()
            self.__curr_dga: DGA = DGA(json.loads(game_info))

        pass

    def get_turn_of(self) -> str:
        return self.__curr_dga.get_playing_rn()

    def get_who_am_i(self) -> str:
        pass

    def get_allowed_moves(self):
        return [1, 2, 3, 4, 5, 6]

    def move(self, move: str):
        self.__curr_dga.apply_move(move)

    def get_ginfo(self):
        return str(self.__curr_dga)

    def forfeit(self):
        return 'Not possible in this game'

    def _get_playable(self):
        pass

    def _set_playable(self, state: bool):
        pass

    def _update(self) -> None:
        pass

    def _validate(self, fen: str) -> bool:
        pass

    def _get_turn_of(self) -> str:
        pass

    def _get_game_id(self) -> str:
        pass

    def _sync_log(self) -> None:
        pass

    def get_board(self) -> dict:
        return self.__curr_dga.get_board()
