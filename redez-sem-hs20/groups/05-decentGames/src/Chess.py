import copy
import json
import os
import sys

from Chessnut.game import InvalidMove

from Exceptions import FileAlreadyExists
from Chessnut import Game
from datetime import datetime
from GameInformation import GameInformation as gi, GameInformation


class Chess:

    def __init__(self, game_id: str = None):
        """

        :param game_id:
        """
        self.__game_id = game_id
        self.__game_path = 'games/%s.chess' % game_id
        self.__log_path = 'logs/log_game_%s.clog' % game_id

        self.__playable = False

        self.__curr_game: Game = Game()
        self.__ginfo: GameInformation = None
        if game_id is not None:
            with open(self.__game_path, 'r') as f:
                game_info = f.readline()
            game_fen, self.__dic = self.get_game_file_info(game_info)

            self.__ginfo = gi(self.__dic)

            if self.validate(game_fen):
                if not self.__ginfo.game_is_initiated():
                    self.__update()
                    return

                self.__sync_log(game_fen)

                self.__curr_game.set_fen(game_fen)

                if self.__dic[self.__get_turn_of()] == self.get_who_am_i():
                    self.__playable = True

            else:
                self.__curr_game.set_fen(game_fen)
                print('Game is not updated yet. Wait for your opponent.')

    def assemble(self):
        return self.__curr_game.get_fen() + '|' + self.__dic

    def get_board(self):
        return self.__curr_game.get_fen().split(' ')[0]

    def get_who_am_i(self):
        return list(self.__dic.keys())[list(self.__dic.values()).index(self.__ginfo.get_mac())]

    def __get_turn_of(self):
        return self.__curr_game.get_fen().split(' ')[1]

    def get_turn_of(self):
        return self.__curr_game.get_fen().split(' ')[1] + ': ' + self.__dic[self.__curr_game.get_fen().split(' ')[1]]


    def get_moves_num(self):
        return self.__curr_game.get_fen().split(' ')[5]

    def get_allowed_moves(self):
        return self.__curr_game.get_moves()

    def get_playable(self):
        return self.__playable

    def get_game_id(self):
        return self.__game_id

    def get_dic(self):
        return self.__dic

    def get_assembled_game(self) -> str:
        return self.__curr_game.get_fen() + '$' + str(self.__ginfo) + '\n'

    def get_ginfo(self):
        return self.__ginfo

    @staticmethod
    def get_game_file_info(info: str) -> (str, dict):
        game_fen, dic = info.split('$')
        return game_fen, json.loads(dic)

    def set_playable(self, status: bool):
        self.__playable = status

    def move(self, move: str) -> None:
        try:
            self.__curr_game.apply_move(move)
            self.__update()
        except InvalidMove:
            print('That move is not allowed. Try again.')

    def __update(self):
        with open(self.__game_path, 'w') as f:
            f.write(self.get_assembled_game())

        with open(self.__log_path, 'a') as f:
            f.write(self.get_time() + self.get_assembled_game())

    def __sync_log(self, opponent_fen: str) -> None:
        try:
            with open(self.__log_path, 'a') as f:
                f.write(self.get_time() + opponent_fen + '$' + str(self.__ginfo) + '\n')
        except FileNotFoundError:
            print('Something went wrong')

    def validate(self, curr_fen: str) -> bool:
        prev = Game()
        try:
            with open(self.__log_path, 'r')as f:
                lines = f.read().splitlines()
        except FileNotFoundError:
            # New game is initiated, log file must be created
            self.__create_log_file(self.get_game_id(), curr_fen + '$' + str(self.__ginfo))
            print('A new game was initiated!')
            return True

        last_line = lines[-1]
        try:
            prev_fen = last_line.split('$')[1]
        except IndexError:
            print(last_line)
            print('Something is wrong')
            sys.exit(0)
        print(prev_fen)
        prev.set_fen(prev_fen)

        curr = Game()
        curr.set_fen(curr_fen)
        if str(curr) == str(prev):
            print('No move yet')
            return True

        for move in prev.get_moves():
            tmp: Game = copy.deepcopy(prev)
            tmp.apply_move(move)
            if str(tmp) == str(curr):
                print('Valid move made: %s' % move)
                return True
        return False

    @staticmethod
    def create(game_id: str):
        base_info = gi.create_game_info()
        string: str = str(Game()) + '$' + str(gi(base_info))
        Chess.__create_game_file(game_id, string)
        Chess.__create_log_file(game_id, string)

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

    @staticmethod
    def get_time() -> str:
        return datetime.now().strftime('%Y-%m-%d_%H:%M:%S') + '$'
