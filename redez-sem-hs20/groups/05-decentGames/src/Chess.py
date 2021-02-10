import copy
import json
import os
import sys

from Chessnut.game import InvalidMove

import State
from AbsGame import AbsGame
from Exceptions import FileAlreadyExists
from Chessnut import Game
from datetime import datetime
from GameInformation import GameInformation as gi, GameInformation


class Chess(AbsGame):

    def __init__(self, game_id: str = None):
        """

        :param game_id:
        """
        self.__game_id = game_id
        self.__game_path = 'games/%s.chess' % game_id
        self.__log_path = 'logs/log_game_%s.clog' % game_id

        self.__playable = False
        self.__game_is_updated = False

        self.__curr_game: Game = Game()
        self.__ginfo: GameInformation = None
        if game_id is not None:
            with open(self.__game_path, 'r') as f:
                game_info = f.readline()
            # game_fen, self.__dic = self.get_game_file_info(game_info)

            self.__ginfo = gi(json.loads(game_info))
            game_fen = self.__ginfo.get_fen()
            if self._validate(game_fen):
                if not self.__ginfo.game_is_initiated():
                    self._update()
                    print('Game must be restarted now.')
                    sys.exit(0)
                if self.__game_is_updated:
                    print('Validation passed, syncing now')
                    self._sync_log()
                else:
                    print('Same file, not syncing anything')

                self.__curr_game.set_fen(game_fen)

                if self.__ginfo.get_player(self._get_turn_of()) == self.get_who_am_i()\
                        and self.get_ginfo().get_status() == State.ONGOING:
                    self.__playable = True

            else:
                self.__curr_game.set_fen(game_fen)
                print('Game is not updated yet. Wait for your opponent.')

    def get_board(self):
        return self.__curr_game.get_fen().split(' ')[0]

    def get_who_am_i(self):
        # TODO: Add handler when there is no compatible MAC address
        return list(self.__ginfo.get_dic().keys())[list(self.__ginfo.get_dic().values()).index(self.__ginfo.get_mac())]

    def _get_turn_of(self):
        return self.__curr_game.get_fen().split(' ')[1]

    def get_turn_of(self):
        p = self._get_turn_of()
        return p + ': ' + self.__ginfo.get_player(p)

    def get_allowed_moves(self):
        return self.__curr_game.get_moves()

    def _get_playable(self):
        return self.__playable

    def _get_game_id(self):
        return self.__game_id

    def get_ginfo(self) -> GameInformation:
        return self.__ginfo

    def _set_playable(self, status: bool):
        self.__playable = status

    def move(self, move: str) -> None:
        try:
            if self._get_playable():
                self.__curr_game.apply_move(move)
                self.get_ginfo().inc_seq()

                self.__ginfo.set_fen(str(self.__curr_game))
                if not self.get_allowed_moves():
                    self.__ginfo.set_status(State.FINISHED)
                    self.__ginfo.set_winner(self.get_who_am_i())
                    self.__ginfo.set_loser('p1' if self.get_who_am_i() == 'p2' else 'p2')
                    print('CHECKMATE, mate! Well done, You won the game!')
                self._set_playable(False)
                self._update()
            else:
                print('You cannot make a move. It is the turn of your opponent')
        except InvalidMove:
            print('That move is not allowed. Try again.')

    def forfeit(self):
        if self.get_ginfo().get_status() == State.ONGOING:
            self.get_ginfo().set_status(State.FF)
            self.get_ginfo().set_ff(self.get_who_am_i())
            self.get_ginfo().set_winner('p1' if self.get_who_am_i() == 'p2' else 'p2')
            self.get_ginfo().set_loser(self.get_who_am_i())
            self._update()
        else:
            print('Game ended already. You cannot forfeit.')

    def _update(self):
        with open(self.__game_path, 'w') as f:
            f.write(str(self.__ginfo) + '\n')

        with open(self.__log_path, 'a') as f:
            f.write(self.get_time() + str(self.__ginfo) + '\n')

    def _sync_log(self) -> None:
        try:
            with open(self.__log_path, 'a') as f:
                f.write(self.get_time() + str(self.__ginfo) + '\n')
        except FileNotFoundError:
            print('Something went wrong')

    def _validate(self, curr_fen: str) -> bool:
        try:
            with open(self.__log_path, 'r')as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            # New game is initiated, log file must be created
            self.__create_log_file(self._get_game_id(), str(self.__ginfo))
            print('A new game was initiated!')
            return True

        last_line = lines[-1]
        try:
            prev_ginfo = GameInformation(json.loads(last_line.split('$')[1]))
        except IndexError:
            print(last_line)
            print('Something is wrong')
            sys.exit(0)

        curr = Game()
        curr.set_fen(curr_fen)

        if str(self.__ginfo) == str(prev_ginfo):
            self.__game_is_updated = False
            return True
        prev = Game()
        prev.set_fen(prev_ginfo.get_fen())
        print(prev)
        print(curr)
        if str(prev) == str(curr):
            self.__game_is_updated = True
            return True

        for move in prev.get_moves():
            tmp: Game = copy.deepcopy(prev)
            tmp.apply_move(move)
            if str(tmp) == str(curr):
                self.__game_is_updated = True
                print('Valid move made: %s' % move)
                return True
        print('Your opponent seems to be cheating... Game aborted. You are the winner.')
        self.__ginfo.set_status(State.CHEATED)
        self.__ginfo.set_winner(self.get_who_am_i())
        self.get_ginfo().set_loser('p1' if self.get_who_am_i() == 'p2' else 'p2')
        return False

    @staticmethod
    def create(game_id: str):
        base_info: GameInformation = gi.create_game_info(str(Game()))
        game_json: str = str(base_info)
        Chess.__create_game_file(game_id, game_json)
        Chess.__create_log_file(game_id, game_json)

    @staticmethod
    def __create_game_file(game_id: str, string: str):
        file: str = 'games/%s.chess' % game_id
        if not os.path.isfile(file):
            with open(file, 'w') as f:
                f.write(string + '\n')
        else:
            raise FileAlreadyExists('File already exists')

    @staticmethod
    def __create_log_file(game_id: str, string: str):
        log: str = 'logs/log_game_%s.clog' % game_id
        if not os.path.isfile(log):
            intro: str = 'log to games: %s\n-------------\n' % game_id
            with open(log, 'w') as f:
                f.write(intro)
                f.write(Chess.get_time() + string + '\n')
        else:
            raise FileAlreadyExists('File already exists')
