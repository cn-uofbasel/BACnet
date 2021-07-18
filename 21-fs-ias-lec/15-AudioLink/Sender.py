import numpy as np
import simpleaudio as sa
import scipy.io
import scipy.io.wavfile
from Hamming import Hamming
import hashlib



class Sender:

    def __init__(self, tauS=160, tau0=20, tau1=80, sample_rate=44100):
        '''
        :param tauS: determines how many samples are used to modulate one bit
        tauS must be multiple of both tau0 and tau1
        :param tau0: determines the frequency of the high modulation note
        :param tau1: determines the frequency of the low modulation
        :param sample_rate: determines how many audio samples are used per second
        '''

        # sanity check to see if tauS is indeed a multiple of tau0 and tau1
        checkTau0 = tauS // tau0
        checkTau1 = tauS // tau1

        if not (checkTau0 * tau0 == tauS and checkTau1 * tau1 == tauS):
            print('tauS must be multiple of both tau0 and tau1')
            return

        self.fs = 1/tauS
        self.rate = tauS
        self.freq_high = 1 / tau0
        self.freq_low = 1 / tau1

        self.weight_high = 1
        self.weight_low = 1

        # could be used for double modulation. Not in use as of now
        self.f3 = 1 / 40
        self.f4 = 1 / 16

        self.audioSampleRate = sample_rate

        self.hamming = Hamming()

        # start sequence to sync transmissions
        self.pilot1 = np.array([1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1, 0, 1, 1,
        1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1, 0, 1, 1,
        0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0, 0, 1, 1,
        0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 0, 1, 0, 1, 1, 0, 0, 0, 0, 1, 0,
        0, 1, 1, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1], dtype=np.uint8)

        # end sequence to mark end of transmission
        self.pilot2 = np.array([0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0, 0, 0, 1,
        0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1, 0, 1, 0,
        0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1, 1, 0, 1,
        0, 1, 0, 0, 0, 1, 0, 1, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1, 0, 1, 1, 1,
        1, 0, 1, 0, 1, 0, 0, 0, 1, 0, 1, 0, 0], dtype=np.uint8)

    def playAudio(self, data):
        audio = data * (2 ** 15 - 1) / np.max(np.abs(data))
        audio = audio.astype(np.int16)
        play_onj = sa.play_buffer(audio, 1, 2, self.audioSampleRate)
        play_onj.wait_done()

    def getTestTone(self):
        frequency = 440
        seconds = 3
        t = np.linspace(0, seconds, seconds * self.fs, False)
        note = np.sin(frequency * t * 2 * np.pi)
        return note

    def getCalibrationTones(self):
        t = np.linspace(0, 2 * self.audioSampleRate, 2 * self.audioSampleRate)
        high = self.weight_high * np.sin(self.freq_high * t * 2 * np.pi)
        low = self.weight_low * np.sin(self.freq_low * t * 2 * np.pi)
        pause = np.zeros(self.audioSampleRate // 2)
        return np.concatenate((high, pause, low))

    def sendCalibration(self):
        self.playAudio(self.getCalibrationTones())

    def setTransmitionAmplitudes(self, amp_high, amp_low):
        if amp_high > amp_low:
            self.weight_high = amp_low / amp_high
        else:
            self.weight_low = amp_high / amp_low
        #self.weight_high = amp_high
        #self.weight_low = amp_low

    def getTestDataAsBits(self, repetitions):
        #s = np.array([1, 0, 1, 1, 0, 0, 1, 0, 0, 0, 1], dtype=np.uint8)
        s = np.tile(np.array([1,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,0,0,0,1,1,0,0,1,0,1,0,1,0,1,0], dtype=np.uint8), repetitions)
        return s

    def repencode(self, data, n):
        encoded = np.repeat(data, n)
        return encoded

    def addPilots(self, data):
        return np.concatenate((self.pilot1, data, self.pilot2))

    def addModulatedPilots(self, data):
        modPilot1 = self.modulate(self.repencode(self.pilot1, self.rate))
        modPilot2 = self.modulate(self.repencode(self.pilot2, self.rate))
        return np.concatenate((modPilot1, data, modPilot2))

    def modulate(self, data):
        length = len(data)
        t = np.linspace(0, length, length)
        mod_high = self.weight_high * np.multiply(np.sin(self.freq_high * t * 2 * np.pi), data)
        mod_low = self.weight_low * np.multiply(np.sin(self.freq_low * t * 2 * np.pi), 1 - data)
        return mod_high + mod_low

    def doubleModulate(self, data):
        if not (len(data) % 2 == 0):
            print('we need padding or something of the sort')
            return
        length = len(data) // 2
        dataPart1 = data[0:length]
        dataPart2 = data[length:]

        t = np.linspace(0, length, length)
        mod_1 = np.multiply(np.sin(self.freq_high * t * 2 * np.pi), dataPart1)
        mod_2 = np.multiply(np.sin(self.freq_low * t * 2 * np.pi), 1 - dataPart1)
        mod_3 = np.multiply(np.sin(self.f3 * t * 2 * np.pi), dataPart2)
        mod_4 = np.multiply(np.sin(self.f4 * t * 2 * np.pi), 1 - dataPart2)

        return mod_1 + mod_2 + mod_3 + mod_4

    def writeToWav(self, data, file_name):
        if not file_name.endswith('.wav'):
            file_name = file_name + '.wav'
        scipy.io.wavfile.write(file_name, self.audioSampleRate, data.astype(np.float32))

    def readFromFile(self, path):
        file = open(path, "rb")
        data = file.read()
        file.close()
        return data

    def writeToFile(self, path, data):
        file = open(path, "wb")
        file.write(data)
        file.close()

    def test(self):
        hamming = Hamming()
        #by = self.readFromFile('pacman2.bmp')
        #bits = self.bytesToBits(by)
        #data = self.addPilots(self.repencode(bits, 10))
        testbits = self.repencode(hamming.encodeBitStream(self.getTestDataAsBits()), 4)
        data = self.addPilots(self.repencode(hamming.encodeBitStream(testbits), 1))
        #dataBytes = self.readFromFile('penguin.png')
        #data = self.bytesToBits(dataBytes)
        #data = self.addPilots(self.repencode(data, 5))
        encoded = self.repencode(data, self.rate)
        modulated = self.modulate(encoded)
        #self.writeToWav(np.concatenate((np.zeros(3*44100), modulated)))
        #demodulated = self.doubleDemodulate(modulated)
        #demodulated = self.doubleDemodulate(modulated)
        print('data and pilots')
        #print(demodulated)
        print('data only')
        print(self.getTestDataAsBits())
        #b = self.bitsToBytes(demodulated.astype(np.uint8))
        #self.writeToFile("pinguuuu.png", b)
        self.writeToWav(modulated)
        self.playAudio(self.modulate(encoded))

    def bytesToBits(self, data):
        dataAsInts = np.fromstring(data, dtype=np.uint8)
        bits = np.unpackbits(dataAsInts)
        return bits

    def bitsToBytes(self, bits):
        binaryBites = np.reshape(bits, ((len(bits) // 8), 8))
        dataAsBytes = np.packbits(binaryBites, axis=1).flatten().tobytes()
        return dataAsBytes

    def addHash(self, data):
        hash = hashlib.sha256(data).digest()
        print('calculated hash', hash)
        return data + hash

    def testConversion(self):
        data = self.readFromFile('testFiles/penguin.png')
        bits = self.bytesToBits(data)
        res = self.bitsToBytes(bits)
        passed = data == res

    def testDoubleModulation(self):
        data = self.repencode(self.getTestDataAsBits(), 3)
        encoded = self.repencode(data, self.rate)
        modulatedData = self.doubleModulate(encoded)
        dataWithPilots = self.addModulatedPilots(modulatedData)
        self.writeToWav(dataWithPilots)
        self.playAudio(dataWithPilots)

    def sendDataRepencoded(self, data, repetitions=3, bits=False):
        '''
        Encodes, modulates and plays data
        :param data: data to be transmitted, either np.array with bits or bytes
        :param repetitions: number of repetitions per bit
        :param bits: if false the data will be interpreted as bytes
        '''
        if not bits:
            data = self.bytesToBits(self.addHash(data))

        repencoded = self.repencode(data, repetitions)
        with_Pilots = self.addPilots(repencoded)
        readyToMod = self.repencode(with_Pilots, self.rate)
        modulated = self.modulate(readyToMod)

        self.playAudio(modulated)

    def sendDataHamming(self, data, repetitions=3, bits=False):
        '''
        Encodes, modulates and plays data. Data will first be encoded using Hamming(7,4) and then
        every bit will be repeated n times (n = repetitions)
        :param data: data to be transmitted, either np.array with bits or bytes
        :param repetitions: number of repetitions per bit
        :param bits: if false the data will be interpreted as bytes
        '''
        if not bits:
            data = self.bytesToBits(self.addHash(data))

        hamming_encoded = self.hamming.encodeBitStream(data)
        rep_encoded = self.repencode(hamming_encoded, repetitions)
        with_pilots = self.addPilots(rep_encoded)
        readyToMod = self.repencode(with_pilots, self.rate)
        modulated = self.modulate(readyToMod)

        self.playAudio(modulated)
