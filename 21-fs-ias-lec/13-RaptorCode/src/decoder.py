import numpy as np

import utils
from utils import NUMBER_OF_ENCODED_BITS, VECTORLENGTH, Z, TransmissionPackage


class Decoder:
    def __init__(self):
        self._inputData = []  # [(informationID, [[(a, y)]] )] <-- Format, place in second Array is chunkID
        self._decodedData = []  # [(informationID, [decodedBinaryVector] )] <-- Format, place in second Array is chunkID
        self._positionsInCoefVector = []  # [(informationID, [[ys with element in this position]] )]
        # self._Z = self._calcZ() # calculate the Z vectors
        self._counter = 0
        if len(Z) == 0:
            utils.calcZ()

    def _decode(self, data, coeffPositions):
        # x is encoded source code:
        x = np.empty(VECTORLENGTH)
        x.fill(-1)
        x = x.astype(int)
        # y is solution vector
        y = []
        # building of Matrix and x Vector
        allCoefficients = []  # temporary array to build Matrix
        for i in range(len(data)):
            allCoefficients.append(data[i][0])
            y.append(data[i][1])

        # add Raptor idea of additional precoded coeff vectors
        for z in Z:
            allCoefficients.append(z)
            y.append(0)

        matrix = np.array(allCoefficients)

        if len(data) < NUMBER_OF_ENCODED_BITS:
            print("Not enough Information")
            return

        for j in range(VECTORLENGTH):
            # Step one
            # find an entry which has exactly on unknown
            numberOfCoefficient = np.sum(matrix, 1)  # number of coefficient per row
            indexOfYi = utils.findFirstNumber(numberOfCoefficient, 1)  # index of first row with one coef.
            if indexOfYi == -1:  # catch if there is no such row
                return

            indexOfXj = utils.findFirstNumber(matrix[indexOfYi], 1)  # index of element with 1

            # step two
            # decode xj since yi is of degree one
            x[indexOfXj] = y[indexOfYi]

            # step three
            # check all coefficient vectors, if they contain xj and remove them from there and yi
            for i in coeffPositions[indexOfXj]:
                matrix[i, indexOfXj] = 0
                y[i] = np.bitwise_xor(y[i], x[indexOfXj])
            coeffPositions[indexOfXj] = []
            """for i in range(len(y)):
                if BinaryVector.checkNumberAtPosition(matrix[i], 1, indexOfXj):
                    matrix[i, indexOfXj] = 0
                    y[i] = np.bitwise_xor(y[i], x[indexOfXj])"""

            # step 4
            # repeat until done

            if utils.findFirstNumber(x, -1) == -1:
                return x

    def decode(self, tp: TransmissionPackage):
        # get the information from the package
        informationID = tp.informationID
        chunkID = tp.chunkID
        size = tp.size
        ayTuple = (utils.intToBin(tp.ayTuple[0], VECTORLENGTH), tp.ayTuple[1])  # also decode a to binVector

        # check if this chunk of information already has been decoded
        decodedID = -1
        for i in range(len(self._decodedData)):
            if self._decodedData[i][0] == informationID:
                decodedID = i
                if len(self._decodedData[i][1][chunkID]) != 0:
                    return

        self._counter += 1
        # check if this information is already in processing
        index = -1
        for i in range(len(self._inputData)):
            if self._inputData[i][0] == informationID:
                index = i
                break

        # when not, create entry's
        if index == -1:
            packages = []
            decoded = []
            coeff = []

            for i in range(size):
                packages.append([])
                decoded.append([])
                temp = []
                for i in range(VECTORLENGTH):
                    temp.append([])
                coeff.append(temp)
            self._inputData.append((informationID, packages))
            self._decodedData.append((informationID, decoded))
            self._positionsInCoefVector.append((informationID, coeff))

        # add it to the input
        self._inputData[index][1][chunkID].append(ayTuple)

        # register positions in coeffvector
        yLen = len(self._inputData[index][1][chunkID])
        for i in range(VECTORLENGTH):
            if ayTuple[0][i] == 1:
                self._positionsInCoefVector[index][1][chunkID][i].append(yLen - 1)

        # check if there are enough information to decode
        # print(self._inputData)
        if len(self._inputData[index][1][chunkID]) < NUMBER_OF_ENCODED_BITS:
            return

        # try to decode data
        decoded = self._decode(self._inputData[index][1][chunkID],
                               self._positionsInCoefVector[index][1][chunkID].copy())

        # check if decoding was successful
        if decoded is None:
            return

        # safe decoded chunk
        self._decodedData[decodedID][1][chunkID] = decoded

        # check if all chunks are decoded
        for i in range(size):
            if len(self._decodedData[decodedID][1][i]) == 0:
                return

        # cut decoded to correct size
        xVector = self._decodedData[decodedID][1][0][0:NUMBER_OF_ENCODED_BITS]
        # bring decoded data in byte form
        byte = utils.bitArrayToBytes(xVector)
        for i in range(1, size):
            xVector = self._decodedData[decodedID][1][i][0:NUMBER_OF_ENCODED_BITS]
            byte += utils.bitArrayToBytes(xVector)

        # remove informationSlot from the memory
        self._inputData.pop(index)
        self._decodedData.pop(decodedID)
        self._positionsInCoefVector.pop(index)

        # return the data
        return byte


