import numpy as np

import fountain
import utils
from utils import NUMBER_OF_ENCODED_BITS, Z, TransmissionPackage


class Encoder:
    def __init__(self, MAX_NUMBER_OF_PACKAGES=10000):  # data are the too be encoded bytes
        self._lt = fountain.LT()
        self.MAX_NUMBER_OF_PACKAGES = MAX_NUMBER_OF_PACKAGES  # Maximum number of packages generated per InputVector
        if len(Z) == 0:
            utils.calcZ()

    def _encodeBytes(self, data):  # transforms the bytes to a bit array
        arr = []  # new empty array
        for i in range(len(data)):  # iterate over every byte
            for j in range(8):  # iterate over every bit in a byte
                arr.append(self._getBitFromByte(data[i], j))  # append each bit to the new array
        return arr  # return bit array

    def _getBitFromByte(self, byte, index):  # gets the bit with an specific index from a byte
        shift = int((7 - index) % 8)  # get number of bits, which have to be shifted
        return (byte & (1 << shift)) >> shift  # returns that bit

    def _encode(self, data: bytes):  # encodes a byte "array"
        a, aCoefficient = self._lt.getVector()  # get a vector, to encode the data
        y = utils.xOrAllElements(
            np.multiply(aCoefficient, data))  # encode the data, y in span (x1, ..., xk, z1, ..., zk)
        return a, y  # return a representation of the Vector and the encoded data

    def encode(self, data: bytes):  # encode data ready to send --> generator
        # Format of outGoing Data:
        # ((informationID, chunkID, size), (a, y))
        if len(data) % (NUMBER_OF_ENCODED_BITS / 8) != 0:  # if data size is not supported
            print("Data input has a not supported size")  # print message and return
            return

        dataPackages = utils.splitInCorrectSize(data)  # data split into processable chunks
        # change dataPackages to BinaryVector
        for i in range(len(dataPackages)):
            dataPackages[i] = self._encodeBytes(dataPackages[i])
            dataPackages[i] = self._preCompute(dataPackages[i])

        informationID = np.random.randint(0, 2 ** 32)  # id of the different packages with random start
        size = len(dataPackages)
        for j in range(self.MAX_NUMBER_OF_PACKAGES):  # for a specified number of generated packages
            for chunkID in range(len(dataPackages)):  # for every different data chunk
                # idTupel = (informationID, chunkID, len(dataPackages))  # calculate the identification Tuple
                a, y = self._encode(dataPackages[chunkID])  # calculate the encoded data
                yield TransmissionPackage(informationID, chunkID, size,
                                          (a, y))  # idTupel, (a, y)  # yield the tuple of id, coeff vector and y
        return 1

    def _preCompute(self, xVector):
        temp = xVector.copy()
        for z in Z:
            temp.append(np.sum(np.multiply(z[0:NUMBER_OF_ENCODED_BITS], xVector)) % 2)
        return temp
