from numpy import random  # only used to simulate data loss

from decoder import Decoder  # necessary for the functionality
from encoder import Encoder  # necessary for the functionality
from utils import NUMBER_OF_ENCODED_BITS  # only used for statistic

# showcase steering elements:
STOP_ENCODER_ON_DECODING = True  # this variable sets whether the encoder stops generating packages once the decoding
# was successful. (This can in IRL only occur, when the sender can be informed)
HAS_PACKAGE_LOSS = False  # sets whether the loss of packages is simulated
PROBABILITY_OF_LOSS = 0.5  # Probability that a package is lost (when package loss is activated)
PRINT_STATISTICS = True  # this variable sets, whether the statistic will be printed or not

# necessary variables
encoder = Encoder(500)  # the Number set how many packages the encoder maximally generates (optional)
decoder = Decoder()
# the following is an example of transmitted data. (Since it takes bytes the string has to be encoded).
# the input has to have a multiple length of 32 bits (4 bytes) or it will not be processed
exampleTransmissionData = "Lorem ipsum dolor sit amet, consectetur adipisici elit, sed diam nonumy.".encode('utf8')

# variables for the statistic   (not relevant)
numberOfPackages = 0  # counts how many packages were sent for every decoded Data
temp_numberOfPackages = 0  # help variable for same task
numberOfDecodedInformation = 0  # counts number of successfully decoding data

# demo code
for package in encoder.encode(exampleTransmissionData):  # the encode function of the decoder acts as a generator
    # which yields utils.TransmissionPackage.
    temp_numberOfPackages += 1  # counter for statistic (not relevant)

    # simulation of package loss
    if random.random() < PROBABILITY_OF_LOSS:
        continue

    txt = decoder.decode(package)  # decoder.decode(TransmissionPackage) tries to decode the information. If there is
    # not enough information it returns None, else it returns the decoded bytes
    if txt is not None:  # check whether the decoder was successful
        numberOfDecodedInformation += 1  # counter for statistics (not relevant)
        numberOfPackages += temp_numberOfPackages  # counter for statistics (not relevant)
        temp_numberOfPackages = 0  # counter for statistics (not relevant)
        print(numberOfDecodedInformation, txt.decode('utf8'))  # the decoded data gets printed (has to be decoded,
        # since its bytes and we want a string.
        if STOP_ENCODER_ON_DECODING:  # steering structure for demo (not relevant)
            break

# statistics
if numberOfDecodedInformation == 0:  # check if there was a successful decoding
    print("Ran out of packages before first successful decoding!")  # if not print that it wasn't successful


elif PRINT_STATISTICS:  # also check if printing of the statistic is activated
    # calculate how many chunks there are for the data
    numberOfChunks = int(len(exampleTransmissionData) / (NUMBER_OF_ENCODED_BITS / 8))
    print("Number of Chunks:\t\t" + str(numberOfChunks))  # print that number
    # number of encoded packages for sending
    print("avg. Number of Packages Needed:\t" + str(numberOfPackages / numberOfDecodedInformation))
    # number of encoded packages for sending per chunk
    print("avg. per chunk:\t\t\t" + str(int(numberOfPackages / numberOfChunks) / numberOfDecodedInformation))
