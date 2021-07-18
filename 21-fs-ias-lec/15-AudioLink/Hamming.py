import numpy as np


class Hamming:
    def __init__(self):
        self.G = np.array([[1, 1, 0, 1], [1, 0, 1, 1], [1, 0, 0, 0], [0, 1, 1, 1], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]])
        self.H = np.array([[1, 0, 1, 0, 1, 0, 1], [0, 1, 1, 0, 0, 1, 1], [0, 0, 0, 1, 1, 1, 1]])
        self.R = np.array([[0, 0, 1, 0, 0, 0, 0], [0, 0, 0, 0, 1, 0, 0], [0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 1]])

    def encode(self, input):
        return np.dot(self.G, input) % 2

    def parityCheck(self, input):
        return np.sum(np.dot(self.H, input) % 2) == 0

    def errorPositionVector(self, input):
        return np.dot(self.H, input) % 2

    def decimalErrorPosition(self, input):
        errorVector = self.errorPositionVector(input)
        res = 4 * errorVector[2] + 2 * errorVector[1] + errorVector[0]
        return int(res - 1)

    def decode(self, input):
        return np.dot(self.R, input)

    def correct(self, input):
        if not self.parityCheck(input):
            errorPos = self.decimalErrorPosition(input)
            if input[errorPos] == 1:
                input[errorPos] = 0
            else:
                input[errorPos] = 1
        return input

    def encodeBitStream(self, input):
        if len(input) % 4 == 0:
            inputMatrix = np.reshape(input, (len(input) // 4, 4))
            encodedMatrix = np.transpose(self.encode(np.transpose(inputMatrix)))
            encodedStream = np.reshape(encodedMatrix, encodedMatrix.size)
            return encodedStream

    def decodeAndCorrectStream(self, data):
        if not len(data) % 7 == 0:
            data = data[:len(data) - len(data) % 7]
            print('truncating data for hamming decoding. Data not divisible by 7')

        inputMatrix = np.reshape(data, (len(data) // 7, 7))
        res = self.decode(self.correct(inputMatrix[0]))
        for i in range(len(data) // 7 - 1):
            #inputMatrix[i] = self.correct(inputMatrix[i])
            res = np.concatenate((res, self.decode(self.correct(inputMatrix[i + 1]))))

        #correctedStream = np.reshape(inputMatrix, inputMatrix.size)
        return res




