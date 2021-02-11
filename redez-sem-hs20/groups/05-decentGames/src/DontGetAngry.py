import copy
import json
import os
import random
import socket
import sys
import xmlrpc.client

import State
from AbsGame import AbsGame
from DGA import DGA
from Exceptions import FileAlreadyExists
from GameInformation import GameInformation

my_ip = socket.gethostbyname(socket.gethostname())


class DontGetAngry(AbsGame):

    def request(self):
        print('Refreshing')
        pass
        # with xmlrpc.client.ServerProxy("http://%s:8001/" % self.__ip1) as proxy:
        #     file_string = proxy.is_even(self.__game_path)
        #
        # # Only refresh if it is the next sequence number
        # if DGA(json.loads(file_string)).get_seq() == self.__ginfo.get_seq() + 1:
        #     with open(self.__game_path, 'w') as f:
        #         f.write(file_string + '\n')
        #         f.close()
        #     return
        #
        # with xmlrpc.client.ServerProxy("http://%s:8001/" % self.__ip2) as proxy:
        #     file_string = proxy.is_even(self.__game_path)
        #
        # # Only refresh if it is the next sequence number
        # if DGA(json.loads(file_string)).get_seq() == self.__ginfo.get_seq() + 1:
        #     with open(self.__game_path, 'w') as f:
        #         f.write(file_string + '\n')
        #         f.close()

    def ping(self):
        with xmlrpc.client.ServerProxy("http://%s:8001/" % self.__ip1) as proxy:
            multicall = xmlrpc.client.MultiCall(proxy)
            multicall.react(self.__game_path, my_ip)
            multicall()

        with xmlrpc.client.ServerProxy("http://%s:8001/" % self.__ip2) as proxy:
            multicall = xmlrpc.client.MultiCall(proxy)
            multicall.react(self.__game_path, my_ip)
            multicall()

    def __init__(self, game_id: str, ip1: str, ip2):
        self.__game_id = game_id
        self.__game_path = 'games/%s.dga' % game_id
        self.__log_path = 'logs/log_dga_%s.dlog' % game_id

        self.__ip1 = ip1
        self.__ip2 = ip2

        self.__playable = False
        self.__game_is_updated = False

        if game_id is not None:
            with open(self.__game_path, 'r') as f:
                game_info = f.readline()
            self.__ginfo: DGA = DGA(json.loads(game_info))
            self.__curr_game = self.__ginfo.get_board()

            if self._validate(self.__curr_game):
                if not self.__ginfo.game_is_initiated():
                    self._update()
                    print('Game must be restarted now.')
                    sys.exit(0)
                if self.__game_is_updated:
                    print('Validation passed, syncing now')
                    self._sync_log()
                else:
                    print('Same file, not syncing anything')

                if self.__ginfo.get_player(self._get_turn_of()) == self.get_who_am_i()\
                        and self.get_ginfo().get_status() == State.ONGOING:
                    self.__playable = True
            else:
                print('Not validated?')

    def get_turn_of(self) -> str:
        p = self._get_turn_of()
        return p + ': ' + self.__ginfo.get_player(p)

    def get_who_am_i(self) -> str:
        return list(self.__ginfo.get_dic().keys())[list(self.__ginfo.get_dic().values()).index(self.__ginfo.get_mac())]

    def get_allowed_moves(self):
        return [1, 2, 3, 4, 5, 6]

    def move(self, move: str):
        move = random.randint(1, 7)
        if self._get_playable():
            self.__ginfo.apply_move(move)
            self.get_ginfo().inc_seq()
            self._update()
            self.ping()
            self._set_playable(False)
        else:
            print('You cannot make a move.')

    def get_ginfo(self):
        return self.__ginfo

    def forfeit(self):
        return 'Not possible in this game'

    def _get_playable(self):
        return self.__playable

    def _set_playable(self, state: bool):
        self.__playable = state

    def _update(self) -> None:
        with open(self.__game_path, 'w') as f:
            f.write(str(self.__ginfo) + '\n')

        with open(self.__log_path, 'a') as f:
            f.write(self.get_time() + str(self.__ginfo) + '\n')

    def _validate(self, curr_board: dict) -> bool:
        try:
            with open(self.__log_path, 'r')as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            # New game is initiated, log file must be created
            self.__create_log_file(self._get_game_id(), str(self.__ginfo))
            print('A new game was initiated!')
            return True

        last_line = lines[-1]
        prev_ginfo = DGA(json.loads(last_line.split('$')[1]))

        # Check if same file/string
        if str(self.__ginfo) == str(prev_ginfo):
            print('Absolute same string')
            self.__game_is_updated = False
            return True

        prev_board = prev_ginfo.get_board()
        # Check only board
        if str(prev_board) == str(curr_board):
            print('Same board, but other things changed')
            self.__game_is_updated = True
            return True

        # Check if moves before were legit
        for move in self.get_allowed_moves():
            tmp: DGA = copy.deepcopy(prev_ginfo)
            tmp.apply_move(str(move))
            if str(tmp.get_board()) == str(curr_board):
                self.__game_is_updated = True
                print('Valid move was made: %s' % move)
                return True
        print('An opponent seems to be cheating... Game aborted.')
        self.__ginfo.set_status(State.CHEATED)
        self.__ginfo.inc_seq()
        self._update()
        self.ping()
        print(self.__ginfo.get_status())
        return False

    def _get_turn_of(self) -> str:
        return self.__ginfo.get_playing_rn()

    def _get_game_id(self) -> str:
        return self.__game_id

    def _sync_log(self) -> None:
        try:
            with open(self.__log_path, 'a') as f:
                f.write(self.get_time() + str(self.__ginfo) + '\n')
        except FileNotFoundError:
            print('Something went wrong')

    def get_board(self) -> dict:
        return self.__curr_game

    @staticmethod
    def create(game_id: str):
        base_info = DGA(DGA.start_board)
        game_json: str = str(base_info)
        DontGetAngry.__create_game_file(game_id, game_json)
        DontGetAngry.__create_log_file(game_id, game_json)

    @staticmethod
    def __create_game_file(game_id: str, string: str):
        file: str = 'games/%s.dga' % game_id
        if not os.path.isfile(file):
            with open(file, 'w') as f:
                f.write(string + '\n')
        else:
            raise FileAlreadyExists('File already exists')

    @staticmethod
    def __create_log_file(game_id: str, string: str):
        log: str = 'logs/log_dga_%s.dlog' % game_id
        if not os.path.isfile(log):
            intro: str = 'log to games: %s\n-------------\n' % game_id
            with open(log, 'w') as f:
                f.write(intro)
                f.write(DontGetAngry.get_time() + string + '\n')
        else:
            raise FileAlreadyExists('File already exists')