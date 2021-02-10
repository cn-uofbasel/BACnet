import copy
import json

import State


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

    def __init__(self, game_info: dict):
        self.__board = game_info['fen']
        self.__counter = game_info['counter']
        self.__status = game_info['status']
        self.__B_pos = self.__get_pos_of(DGA.BLUE)
        self.__R_pos = self.__get_pos_of(DGA.RED)
        self.__Y_pos = self.__get_pos_of(DGA.YELLOW)

        self.__playing_rn = game_info['turn']

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
        steps = int(steps)
        curr = int(self.get_b_steps())
        self.__counter[DGA.BLUE] = str(curr + steps)

    def get_r_steps(self):
        return self.__counter[DGA.RED]

    def set_r_steps(self, steps: str):
        steps = int(steps)
        curr = int(self.get_r_steps())
        self.__counter[DGA.RED] = str(curr + steps)

    def get_y_steps(self):
        return self.__counter[DGA.YELLOW]

    def set_y_steps(self, steps: str):
        steps = int(steps)
        curr = int(self.get_y_steps())
        self.__counter[DGA.YELLOW] = str(curr + steps)

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

    def __str__(self):
        return json.dumps({'fen': self.get_board(), 'counter': self.get_counter(), 'turn': self.get_playing_rn()})