import copy
import json
import random
import sys

from getmac import get_mac_address as gma


class GameInformation:

    @staticmethod
    def create_game_info() -> dict:
        base_info = {
            'p1': gma(),
            'p2': None,
            'w': None,
            'b': None,
            'seq': -1
        }
        return base_info

    def __init__(self, info: dict):
        self.__info = info
        self.__p1 = info['p1']
        self.__p2 = info['p2']
        self.__w = info['w']
        self.__b = info['b']
        self.__seq = info['seq']
        self.__this_user_mac = gma()

    def get_dic(self) -> dict:
        return self.assemble()

    def game_is_initiated(self) -> bool:
        if not self.p2_exists():
            if self.__p1 == self.get_mac():
                print('You are already player1. Wait for player 2...')
                sys.exit(0)

            while True:
                inp = input('There is no 2nd player, would you like to play? (y/n)')
                if inp == 'y':
                    self.set_p2(gma())
                    break
                elif inp == 'n':
                    sys.exit(0)
                else:
                    pass

            self.assign_roles()

            color = 'White' if self.__w == 'p2' else 'Black'
            print('Assigning roles, you are %s' % color)
            self.inc_seq()
            return False
        else:
            print('Game is loading..')
            return True

    def p2_exists(self):
        return self.__p2 is not None

    def set_p1(self, pid: str):
        self.__p1 = pid

    def set_p2(self, pid: str):
        self.__p2 = pid

    def inc_seq(self):
        self.__seq += 1

    def assign_roles(self):
        roles = random.randint(0, 1)
        if roles:
            self.__w = 'p1'
            self.__b = 'p2'
        else:
            self.__w = 'p2'
            self.__b = 'p1'

    def get_mac(self):
        return self.__this_user_mac

    def assemble(self) -> dict:
        self.__info['p1'] = self.__p1
        self.__info['p2'] = self.__p2
        self.__info['w'] = self.__w
        self.__info['b'] = self.__b
        self.__info['seq'] = self.__seq
        return self.__info

    def assigned(self):
        return self.__w is not None and self.__b is not None

    def __str__(self):
        return json.dumps(self.assemble())
