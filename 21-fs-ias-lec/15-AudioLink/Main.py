from Sender import Sender
from Receiver import Receiver
import scipy.io.wavfile
import numpy as np
from Hamming import Hamming

'''
Adjust these values for your input device and calibration for your setup
'''
#print(Receiver.getAvailableAudioDevices())
input_device_id = 4
amplitude_high = 0.54213
amplitude_low = 0.26384


def sendCalibration():
    sender = Sender()
    sender.sendCalibration()

def testReceiverFromFile():
    receiver = Receiver()
    sender = Sender()
    testBytes = sender.readFromFile('testFiles/pacman2.bmp')
    actual = receiver.receiveRepencoded(10, 3, plot=True, from_file=True, file_path='testFiles/pacmanAudioNew.wav')

    testBits = sender.bytesToBits(testBytes)
    actualBits = sender.bytesToBits(actual)

    print('Error sum', np.sum(np.abs(testBits - actualBits)))

def receiveLongTestRepencoded():
    receiver = Receiver()
    print(receiver.getAvailableAudioDevices())
    receiver.setAudioInputDevice(input_device_id)
    sender = Sender()
    testBytes = sender.readFromFile('testFiles/pacman2.bmp')
    actual = receiver.receiveRepencoded(28, 3, plot=True)

    testBits = sender.bytesToBits(testBytes)
    actualBits = sender.bytesToBits(actual)

    print('Error sum', np.sum(np.abs(testBits - actualBits)))

def receiveLongTestHamming():
    receiver = Receiver()
    print(receiver.getAvailableAudioDevices())
    receiver.setAudioInputDevice(input_device_id)
    sender = Sender()
    testBytes = sender.readFromFile('testFiles/pacman2.bmp')
    actual = receiver.receiveHammingEncoded(50, 3, plot=True)

    testBits = sender.bytesToBits(testBytes)
    actualBits = sender.bytesToBits(actual)

    print('Error sum', np.sum(np.abs(testBits - actualBits)))

def sendShortTestRepencoded():
    sender = Sender()
    sender.setTransmitionAmplitudes(amplitude_high, amplitude_low)
    testBits = sender.getTestDataAsBits(5)
    sender.sendDataRepencoded(testBits, 3, bits=True)

def sendShortTestHammingEncoded():
    sender = Sender()
    sender.setTransmitionAmplitudes(amplitude_high, amplitude_low)
    testBits = sender.getTestDataAsBits(5)
    sender.sendDataHamming(testBits, 3, bits=True)

def sendLongTestRepencoded():
    sender = Sender()
    sender.setTransmitionAmplitudes(amplitude_high, amplitude_low)
    data = sender.readFromFile('testFiles/pacman2.bmp')
    sender.sendDataRepencoded(data, 3)

def sendLongTestHamming():
    sender = Sender()
    sender.setTransmitionAmplitudes(amplitude_high, amplitude_low)
    data = sender.readFromFile('testFiles/pacman2.bmp')
    sender.sendDataHamming(data, 3)


def receiveShortTestRepencoded():
    receiver = Receiver()
    print(receiver.getAvailableAudioDevices())
    receiver.setAudioInputDevice(input_device_id)
    sender = Sender()
    actual = receiver.receiveRepencoded(10, 3, plot=True)

    testBits = sender.getTestDataAsBits(5)
    actualBits = sender.bytesToBits(actual)

    print('Error sum', np.sum(np.abs(testBits - actualBits)))

def receiveShortTestHamming():
    receiver = Receiver()
    print(receiver.getAvailableAudioDevices())
    receiver.setAudioInputDevice(input_device_id)
    sender = Sender()
    actual = receiver.receiveHammingEncoded(10, 3, plot=True)

    testBits = sender.getTestDataAsBits(5)
    actualBits = sender.bytesToBits(actual)

    print('Error sum', np.sum(np.abs(testBits - actualBits)))

def testHamming():
    sender = Sender()
    receiver = Receiver()
    hamming = Hamming()

    testBits = sender.getTestDataAsBits(5)
    hammEncoded = hamming.encodeBitStream(testBits)
    rependcoded = sender.repencode(hammEncoded, 3)
    withPilots = sender.addPilots(rependcoded)

    noPilots = receiver.removePilots(withPilots)
    repdec = receiver.repdecode(noPilots, 3)
    actual = hamming.decodeAndCorrectStream(repdec)

    errorSum = np.sum(np.abs(sender.getTestDataAsBits(5) - actual))
    print('errorSum hamming', errorSum)



sendLongTestHamming()