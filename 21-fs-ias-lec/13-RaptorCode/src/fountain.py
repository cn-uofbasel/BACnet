import math
import random

import numpy as np

import utils
from utils import VECTORLENGTH


class LT:
    def __init__(self):  # Initialize member fields
        self._weights = []  # holds probability of the weights
        self._setWeights()  # sets the probability of the weights

        """if not LT._isBinomCalculated:
            self.initArrayOfBinom()"""

    def _setWeights(self):  # set the probability for the weights and save it in self.weights
        self.weights = []  # clear Array
        self._weights.append(1 / VECTORLENGTH)
        for i in range(1, VECTORLENGTH):  # for every variable:
            w = 1 / (i * (i + 1))  # calculate Probability
            self._weights.append(w)  # write it in Array

    def _getWeight(self):  # get a weight, accordingly to its probability
        randomNum = random.random()  # get a random float between 0 and 1
        index = 0  # set the index to 0
        while True:                             # while randomNum > 0:
            randomNum -= self._weights[index]        # subtract probability of weight at index
            if randomNum <= 0:                      # if randomNum <= 0 break.
                break
            index += 1                              # else increase index by one.
        return index + 1                            # return index == weight

    def getVector(self):                                # returns a vector based on the weight
        weight = self._getWeight()  # get a random weight
        vector = self._getVector(weight)
        binaryVector = utils.intToBin(vector, VECTORLENGTH)

        # binaryVector = BinaryVector.intToBin(weight, self._vectorSize)
        return vector, binaryVector  # return array with binary representation of weight of given lengt

    def _getVector(self, weight: int):
        arr = np.arange(VECTORLENGTH)
        np.random.shuffle(arr)
        a = 0
        for i in range(weight):
            a += int(math.pow(2, arr[i]))
        return a
