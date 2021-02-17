import copy
import json
import os
import random
import socket
import sys
import xmlrpc.client

import State
from AbsGame import AbsGame, MY_IP
from DGA import DGA
from Exceptions import FileAlreadyExists
from GameInformation import GameInformation


class DontGetAngry(AbsGame):

    def _sync_log(self) -> None:
        pass

    def fetch(self):
        n = self.__ginfo.get_seq()
        self._fetch_lines(self.__game_path, n, self.__ip1, self.__ip2)

    def refresh(self):
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

    def __init__(self, game_id: str, ip1: str, ip2):
        self.__game_id = game_id
        self.__game_path = 'games/%s.dga' % game_id

        self.__ip1 = ip1
        self.__ip2 = ip2

        self.__playable = False
        self.__game_is_updated = False

        if game_id is not None:
            with open(self.__game_path, 'r') as f:
                time, game_info = f.read().splitlines()[-1].split('$')
            self.__ginfo: DGA = DGA(json.loads(game_info))
            self.__curr_game = self.__ginfo.get_board()

            if self._validate(self.__curr_game):
                if not self.__ginfo.game_is_initiated():
                    self._update()
                    print('Game must be restarted now.')
                    sys.exit(0)

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
        with open(self.__game_path, 'a') as f:
            f.write(self.get_time() + str(self.__ginfo) + '\n')
            f.close()
        self.ping_the_updates(self.__game_path, self.__ip1, self.__ip2, MY_IP)

    def _validate(self, curr_board: dict) -> bool:
        with open(self.__game_path, 'r')as f:
            lines = f.read().splitlines()

        second_last_line = lines[-2]
        prev_ginfo = DGA(json.loads(second_last_line.split('$')[1]))

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
        print(self.__ginfo.get_status())
        return False

    def _get_turn_of(self) -> str:
        return self.__ginfo.get_playing_rn()

    def _get_game_id(self) -> str:
        return self.__game_id

    def get_board(self) -> dict:
        return self.__curr_game
