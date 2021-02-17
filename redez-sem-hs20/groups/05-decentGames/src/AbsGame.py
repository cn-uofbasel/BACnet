import time
import xmlrpc.client as rpc
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
    def get_ginfo(self):
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

    @staticmethod
    def request_new_game_file(path: str, ip: str):
        with rpc.ServerProxy("http://%s:8001/" % ip) as proxy:
            multicall = rpc.MultiCall(proxy)
            multicall.game_request(path)
            file_string = tuple(multicall())[0]
        with open(path, 'a') as f:
            f.write(file_string + '\n')
            f.close()

    @staticmethod
    def ping_the_updates(path, ip1, ip2, my_ip):
        print('i am pinging', ip1, ip2, my_ip)
        try:
            with rpc.ServerProxy("http://%s:8001/" % ip1) as proxy:
                multicall = rpc.MultiCall(proxy)
                multicall.game_is_updated(path, my_ip)
                multicall()
        except:
            print('No server connection')

        if ip2 is not None:
            try:
                with rpc.ServerProxy("http://%s:8001/" % ip2) as proxy:
                    multicall = rpc.MultiCall(proxy)
                    multicall.game_is_updated(path, my_ip)
                    multicall()
            except:
                print('No server connection')

        time.sleep(3)

    def get_type_of(self):
        return type(self)

    @abstractmethod
    def request(self):
        pass
