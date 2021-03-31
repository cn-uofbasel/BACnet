class Board:

    def __init__(self, board):
        self.board = board

    def __str__(self) -> str:
        output: str = '   A B C D E F G H \n'
        board = self.board.split('/')
        for i, row in enumerate(board):
            output += str(8 - i) + ' |'
            for elem in row:
                try:
                    elem = int(elem)
                    for n in range(elem):
                        output += ' |'
                except ValueError:
                    output += elem + '|'
            output += '\n'

        return output
