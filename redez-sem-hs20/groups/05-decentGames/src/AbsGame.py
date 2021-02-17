import os
import socket
import time
import xmlrpc.client as rpc
from abc import ABC, abstractmethod
from datetime import datetime

from Chessnut import Game

from DGA import DGA
from Exceptions import FileAlreadyExists
from GameInformation import GameInformation

MY_IP = socket.gethostbyname(socket.gethostname()) if not socket.gethostbyname(socket.gethostname()) == '127.0.1.1' else input('IP please: ')


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
            print('No server connection with %s' % ip1)

        if ip2 is not None:
            try:
                with rpc.ServerProxy("http://%s:8001/" % ip2) as proxy:
                    multicall = rpc.MultiCall(proxy)
                    multicall.game_is_updated(path, my_ip)
                    multicall()
            except:
                print('No server connection with %s' % ip2)

        time.sleep(3)

    def get_type_of(self):
        return type(self)

    @staticmethod
    def create(file_name: str, game: str):
        if game == 'chess':
            base_info: GameInformation = GameInformation.create_game_info(str(Game()))
            game_json: str = str(base_info)
            AbsGame.__create_log_file(file_name, game, game_json)
        elif game == 'dga':
            base_info: DGA = DGA(DGA.start_board)
            game_json: str = str(base_info)
            AbsGame.__create_log_file(file_name, game, game_json)

    @staticmethod
    def __create_log_file(game_id: str, game: str, string: str):
        log: str = 'games/%s.%s' % (game_id, game)
        if not os.path.isfile(log):
            intro: str = 'log to %s: %s\n-------------\n' % (game, game_id)
            with open(log, 'w') as f:
                f.write(intro)
                f.write(AbsGame.get_time() + string + '\n')
        else:
            raise FileAlreadyExists('File already exists')

    @abstractmethod
    def refresh(self):
        pass

    @abstractmethod
    def fetch(self):
        pass

    @staticmethod
    def _fetch_lines(path: str, seq_num: int, ip1: str, ip2: str = None):
        with rpc.ServerProxy("http://%s:8001/" % ip1) as proxy:
            multicall = rpc.MultiCall(proxy)
            multicall.fetching(path, seq_num)
            file_string = tuple(multicall())[0]
        print(file_string)
        if file_string:
            with open(path, 'a') as f:
                for elem in file_string:
                    f.write(elem + '\n')
                f.close()
            return

        if ip2 is not None:
            with rpc.ServerProxy("http://%s:8001/" % ip2) as proxy:
                multicall = rpc.MultiCall(proxy)
                multicall.fetching(path, seq_num)
                file_string = tuple(multicall())[0]
            print(file_string)
            if file_string:
                with open(path, 'a') as f:
                    for elem in file_string:
                        f.write(elem + '\n')
                    f.close()
                return
