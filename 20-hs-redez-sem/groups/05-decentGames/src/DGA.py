import copy
import json
import random
import sys

import State
from getmac import get_mac_address as gma


class DGA:
    BLUE: str = 'B'
    RED = 'R'
    YELLOW = 'Y'
    EMPTY = 'O'
    INNER_FIELD = 'x'
    GOAL = 'X'
    B_START_POS = '0'
    B_PATH_START = 27
    R_START_POS = '9'
    R_PATH_START = 31
    Y_START_POS = '18'
    Y_PATH_START = 35
    OUTTER_RING = 26
    GOAL_STEPS = 30
    GOAL_POS = '39'

    start_board = {
        'fen': {0: 'B', 1: 'O', 2: 'O', 3: 'O', 4: 'O', 5: 'O', 6: 'O', 7: 'O', 8: 'O',
                9: 'R', 10: 'O', 11: 'O', 12: 'O', 13: 'O', 14: 'O', 15: 'O', 16: 'O', 17: 'O',
                18: 'Y', 19: 'O', 20: 'O', 21: 'O', 22: 'O', 23: 'O', 24: 'O', 25: 'O', 26: 'O',
                27: 'x', 28: 'x', 29: 'x', 30: 'x',
                31: 'x', 32: 'x', 33: 'x', 34: 'x',
                35: 'x', 36: 'x', 37: 'x', 38: 'x',
                39: 'X'},                       # The game board
        'counter': {'B': 0, 'R': 0, 'Y': 0},    # Steps counter
        'status': 'normal',                     # Game status
        'turn': 'B',                            # Whose turn is it
        'p1': gma(),                            # Player 1 Identification
        'p2': None,                             # Player 2 Identification
        'p3': None,                             # Player 3 Identification
        'B': None,                              # Role assignment
        'R': None,                              # Role assignment
        'Y': None,                              # Role assignment
        'seq': -1                               # Sequence number
    }

    def __init__(self, game_info: dict):
        self.__can_i_update = True
        self.__board = game_info['fen']
        self.__counter = game_info['counter']
        self.__status = game_info['status']
        self.__B_pos = self.__get_pos_of(DGA.BLUE)
        self.__R_pos = self.__get_pos_of(DGA.RED)
        self.__Y_pos = self.__get_pos_of(DGA.YELLOW)

        self.__playing_rn = game_info['turn']

        self.__p1 = game_info['p1']
        self.__p2 = game_info['p2']
        self.__p3 = game_info['p3']

        self.__B = game_info[DGA.BLUE]
        self.__R = game_info[DGA.RED]
        self.__Y = game_info[DGA.YELLOW]

        self.__seq = game_info['seq']

        self.__this_user_mac = gma()

    def __get_pos_of(self, figure: str) -> int:
        return list(self.__board.keys())[list(self.__board.values()).index(figure)]

    def get_r_pos(self):
        return self.__get_pos_of(DGA.RED)

    def get_b_pos(self):
        return self.__get_pos_of(DGA.BLUE)

    def get_y_pos(self):
        return self.__get_pos_of(DGA.YELLOW)

    def get_b_steps(self):
        return self.__counter[DGA.BLUE]

    def set_b_steps(self, steps: str):
        self.__counter[DGA.BLUE] = steps

    def get_r_steps(self):
        return self.__counter[DGA.RED]

    def set_r_steps(self, steps: str):
        self.__counter[DGA.RED] = steps

    def get_y_steps(self):
        return self.__counter[DGA.YELLOW]

    def set_y_steps(self, steps: str):
        self.__counter[DGA.YELLOW] = steps

    def get_rnp_steps(self):
        return self.__counter[self.get_playing_rn()]

    def add_steps(self, steps: str):
        new_count: str = str(int(self.__counter[self.get_playing_rn()]) + int(steps))
        self.__counter[self.get_playing_rn()] = new_count

    def get_playing_rn(self):
        return self.__playing_rn

    def get_path_start(self):
        if DGA.BLUE == self.get_playing_rn():
            return DGA.B_PATH_START
        if DGA.RED == self.get_playing_rn():
            return DGA.R_PATH_START
        if DGA.YELLOW == self.get_playing_rn():
            return DGA.Y_PATH_START
        else:
            raise Exception

    def get_p1(self):
        return self.__p1

    def get_p2(self):
        return self.__p2

    def get_p3(self):
        return self.__p3

    def get_winner(self):
        return self.__board[DGA.GOAL_POS]

    def assign_roles(self):
        roles = random.randint(0, 6)

        if roles == 0:
            self.__B = 'p1'
            self.__R = 'p2'
            self.__Y = 'p3'
        elif roles == 1:
            self.__B = 'p2'
            self.__R = 'p1'
            self.__Y = 'p3'
        elif roles == 2:
            self.__B = 'p2'
            self.__R = 'p3'
            self.__Y = 'p1'
        elif roles == 3:
            self.__B = 'p1'
            self.__R = 'p3'
            self.__Y = 'p2'
        elif roles == 4:
            self.__B = 'p3'
            self.__R = 'p2'
            self.__Y = 'p1'
        elif roles == 5:
            self.__B = 'p3'
            self.__R = 'p1'
            self.__Y = 'p2'

    def get_status(self):
        return self.__status

    def set_status(self, state: str):
        self.__status = state

    def __change_playing_rn(self):
        self.__playing_rn = DGA.RED if self.get_playing_rn() == DGA.BLUE else DGA.YELLOW if self.get_playing_rn() == DGA.RED else DGA.BLUE

    def apply_move(self, steps: str):
        if self.get_status() != State.ONGOING:
            return
        pos = int(self.__get_pos_of(self.__playing_rn))
        steps = int(steps)

        if int(self.get_rnp_steps()) + steps > DGA.OUTTER_RING - 1:
            if int(self.get_rnp_steps()) + steps >= DGA.GOAL_STEPS:
                # Reaching GOAL
                self.__board[DGA.GOAL_POS] = self.get_playing_rn()
                self.__board[str(pos)] = DGA.EMPTY if pos < DGA.OUTTER_RING else DGA.INNER_FIELD
                self.add_steps(str(steps))
                self.set_status(State.FINISHED)
            else:
                # INNER FIELD
                new_steps = int(self.get_rnp_steps()) + steps - DGA.OUTTER_RING
                self.__board[str(self.get_path_start() + new_steps)] = self.get_playing_rn()
                self.__board[str(pos)] = DGA.EMPTY if pos < DGA.OUTTER_RING else DGA.INNER_FIELD
                self.add_steps(str(steps))
        else:
            # OUTER RING steps
            new_pos = pos + steps
            if new_pos > DGA.OUTTER_RING:
                new_pos -= DGA.OUTTER_RING

            if self.__board[str(new_pos)] == DGA.EMPTY:
                self.__board[str(new_pos)] = self.get_playing_rn()
                self.__board[str(pos)] = DGA.EMPTY
                self.add_steps(str(steps))

            elif self.__board[str(new_pos)] == DGA.RED:
                self.__board[str(new_pos + 1)] = self.get_playing_rn()
                self.__board[str(pos)] = DGA.EMPTY
                self.__board[self.get_r_pos()] = DGA.EMPTY
                self.__board[DGA.R_START_POS] = DGA.RED
                self.set_r_steps('0')
                self.add_steps(str(steps + 1))

            elif self.__board[str(new_pos)] == DGA.BLUE:
                self.__board[str(new_pos + 1)] = self.get_playing_rn()
                self.__board[str(pos)] = DGA.EMPTY
                self.__board[self.get_b_pos()] = DGA.EMPTY
                self.__board[DGA.B_START_POS] = DGA.BLUE

                self.set_b_steps('0')
                self.add_steps(str(steps + 1))

            elif self.__board[str(new_pos)] == DGA.YELLOW:
                self.__board[str(new_pos + 1)] = self.get_playing_rn()
                self.__board[str(pos)] = DGA.EMPTY
                self.__board[self.get_y_pos()] = DGA.EMPTY

                self.__board[DGA.Y_START_POS] = DGA.YELLOW

                self.set_y_steps('0')
                self.add_steps(str(steps + 1))

        self.__change_playing_rn()

    def get_possible_outcomes(self) -> list:
        if self.get_status() != State.ONGOING:
            return []

        outcomes = []
        for steps in range(1, 7):
            tmp = copy.deepcopy(self)
            tmp.apply_move(str(steps))
            outcomes.append(tmp.get_board())

        return [dict(t) for t in {tuple(elem.items()) for elem in outcomes}]

    def get_board(self) -> dict:
        return self.__board

    def get_counter(self) -> dict:
        return self.__counter

    def p2_exists(self):
        return self.__p2 is not None

    def p3_exists(self):
        return self.__p3 is not None

    def get_mac(self):
        return self.__this_user_mac

    def game_is_initiated(self) -> bool:
        if not self.p2_exists():
            if self.__p1 == self.get_mac():
                print('You are already a player1. Wait for the others...')
                self.__can_i_update = False
                return False

            while True:
                inp = input('There is no 2nd player, would you like to play? (y/n)')
                if inp == 'y':
                    self.__p2 = gma()
                    return False
                elif inp == 'n':
                    sys.exit(0)
                else:
                    pass
        elif not self.p3_exists():
            if self.__p1 == self.get_mac() or self.__p2 == self.get_mac():
                print('You are already playing. Wait for the last player...')
                self.__can_i_update = False
                return False

            while True:
                inp = input('There is no 3rd player, would you like to play? (y/n)')
                if inp == 'y':
                    self.__p3 = gma()
                    break
                elif inp == 'n':
                    sys.exit(0)
                else:
                    pass

            self.assign_roles()
            print('Roles assigned')
            self.inc_seq()
            return False
        else:
            print('Game is loading..')
            return True

    def assemble(self) -> dict:
        return {'fen': self.get_board(),
                'counter': self.get_counter(),
                'status': self.get_status(),
                'turn': self.get_playing_rn(),
                'p1': self.__p1,
                'p2': self.__p2,
                'p3': self.__p3,
                'B': self.__B,
                'R': self.__R,
                'Y': self.__Y,
                'seq': self.__seq
                }

    def get_dic(self) -> dict:
        return self.assemble()

    def __str__(self):
        return json.dumps(self.assemble())

    def get_player(self, key: str):
        p = self.__B if key == DGA.BLUE else self.__R if key == DGA.RED else self.__Y if key == DGA.YELLOW else None
        return p

    def inc_seq(self):
        self.__seq += 1

    def get_seq(self) -> int:
        return self.__seq

    def can_i_update(self):
        return self.__can_i_update
