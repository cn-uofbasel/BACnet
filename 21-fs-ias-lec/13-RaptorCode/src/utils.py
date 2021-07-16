import numpy as np

NUMBER_OF_ENCODED_BITS = 32  # Number of bits per Vector
NUMBER_OF_Z = 2  # Number of redundant bits --> RAPTOR
VECTORLENGTH = NUMBER_OF_ENCODED_BITS + NUMBER_OF_Z  # Number of Xj ( and Zl)
Z = []


# Datastructure for the transmission between sender and reciver
class TransmissionPackage:
    def __init__(self, informationID, chunkID, size, ayTuple):
        self.informationID = informationID  # identifying number, to which information it belongs
        self.chunkID = chunkID  # identifying number to which part of the information it belongs
        self.size = size  # number of chunks/pieces the whole information has
        self.ayTuple = ayTuple  # Tuple that contains the coefficient vector a and the solution y


def calcZ():  # calculates coeff vectors of all z variables and saves them in Z
    z0 = _fillVector(False, 0, [0])  # [1,0,0,..,0,0,1,0]
    Z.append(z0)  # |at this position is ak
    z1 = _fillVector(True, 1, [])  # [1,1,....,1,1,0,1]
    Z.append(z1)
    return Z


def intToBin(integer, vectorSize):
    arr = [int(digit) for digit in bin(integer)[2:]]  # translate it in binary into an array
    vector = []  # create new array
    for i in range(vectorSize - len(arr)):  # for every missing dimension add a new zero to temp
        vector.append(0)
    for i in range(len(arr)):  # append the binary representation to the temp array
        vector.append(arr[i])
    return vector


def findFirstNumber(vector, number):  # This Methode returns the index of the first occurrences of a a Number in a Array
    for i in range(len(vector)):    # for every element in the vector
        if vector[i] == number:     # if the entry at index i is equals to the searched number
            return i                    # return this index
    return -1                       # if there is no such number in the Array return -1


def checkNumberAtPosition(vector, number, position):  # checks if there is a specific number at a specific position
    if vector[position] == number:      # if the entry at a given index is equals to the searched number
        return True                         # return True
    return False                        # else return False


def xOrAllElements(vector):     # This method is equals to a folding xor over a binary vector
    return np.sum(vector) % 2   # returns whether the number of ones in the vector are even (0) or odd (1).


def splitInCorrectSize(data: bytes):    # splits dataInput into correctly sized chunks for the fountain code
    numberOfBytes = len(data)  # number of bytes in inputData
    stepSize = int(NUMBER_OF_ENCODED_BITS / 8)  # targeted number of bytes
    dataArray = []  # new Array, which will contain the data in the correctly sized chunks
    # split data in number of correct sized chunks
    for i in range(0, numberOfBytes, stepSize):
        temp = []
        # fill a new array, with all the corresponding bytes
        for j in range(stepSize):
            temp.append(data[i + j])
        dataArray.append(bytes(temp))  # append the arrays as bytes to the dataArray
    return dataArray


def bitArrayToBytes(bitArray):  # takes a bit array and decodes it into bytes
    byteArr = []  # create new array
    for j in range(int(len(bitArray) / 8)):  # for each 8 bits
        byte = 0  # create number 0
        for i in range(8):  # for each bit
            byte += bitArray[i + 8 * j] * 2 ** (7 - i)  # get value of bit according to place and add it to number
        byteArr.append(byte)  # append value of byte array
    return bytes(byteArr)  # transform number array into bytes


def _fillVector(fillWithOnes, indexOfZ, others):
    # generates coeff Vectors for Z for given specs:
    # if fillWithOnes = True: all a1,...,ak are filled with ones
    # else with zeros
    # idexOfZ, sets the corresponding a(k+index) to 1
    # others is a list of all indexs in a1,..., ak which should be the
    # oposite of fillWithOnes
    temp = []
    if fillWithOnes:
        for i in range(NUMBER_OF_ENCODED_BITS):
            temp.append(1)
        for i in range(VECTORLENGTH - NUMBER_OF_ENCODED_BITS):
            temp.append(0)
    else:
        for i in range(VECTORLENGTH):
            temp.append(0)
    temp[NUMBER_OF_ENCODED_BITS + indexOfZ] = 1

    if fillWithOnes:
        for i in range(len(others)):
            temp[others[i]] = 0
    else:
        for i in range(len(others)):
            temp[others[i]] = 1

    return temp
