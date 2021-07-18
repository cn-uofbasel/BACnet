import sounddevice as sd
import scipy.io.wavfile
from scipy import signal
import numpy as np
import simpleaudio as sa
import sounddevice as sd
from Sender import Sender
from scipy.io.wavfile import write
from Hamming import Hamming
from matplotlib import pyplot as plt
import hashlib

class Receiver:
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

        self.fs = 1 / tauS
        self.rate = tauS
        self.freq_high = 1 / tau0
        self.freq_low = 1 / tau1

        self.weight_high = 1
        self.weight_low = 1

        # could be used for double modulation. Not in use as of now
        self.f3 = 1 / 40
        self.f4 = 1 / 16

        self.audioSampleRate = sample_rate
        self.audioDeviceId = 0

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


    def getTestBits(self, repetitions):
        return np.tile(np.array([1,1,1,1,1,0,0,0,0,0,1,1,1,1,0,0,0,0,1,1,1,0,0,0,1,1,0,0,1,0,1,0,1,0,1,0]), repetitions)


    def calibrate(self, plot=False):
        calibration_input = self.recordAudio(10)
        #calibration_input = self.readWav('calibration.wav')

        sin_high = self.modulate(self.repencode(np.array([1,1,1,1,1]), self.rate))
        sin_low = self.modulate(self.repencode(np.array([0,0,0,0,0]), self.rate))

        offset_sin_high = self.calculateOffsetToTransmission(sin_high, calibration_input)
        offset_sin_low = self.calculateOffsetToTransmission(sin_low, calibration_input)

        peak_sin_high = 0
        peak_sin_low = 0

        for i in range(20):
            start_high = int(offset_sin_high + i * 1 // self.freq_high)
            end_high = int(offset_sin_high + (i + 1) * 1 // self.freq_high)
            peak_sin_high += np.max(calibration_input[start_high:end_high])

            start_low = int(offset_sin_low + i * 1 // self.freq_low)
            end_low = int(offset_sin_low + (i + 1) * 1 // self.freq_low)
            peak_sin_low += np.max(calibration_input[start_low:end_low])

        peak_sin_high /= 20
        peak_sin_low /= 20

        if plot:
            plt.plot(calibration_input)
            plt.show()

        return peak_sin_high, peak_sin_low


    def readWav(self, file_name) -> np.ndarray:
        rate, data = scipy.io.wavfile.read(file_name)

        if data.dtype == np.int16:
            return data.astype(np.float32, order='C') / 32768.0
        return data

    def repencode(self, data, n):
        encoded = np.repeat(data, n)
        return encoded

    def repdecode(self, data, n):
        try:
            padding = len(data) % n
            if padding > 0:
                print('len', len(data))
                print('padding:', padding)
                data = np.concatenate((data, np.zeros(n - padding)))
            averaged = np.mean(data.reshape(-1, n), axis=1)
            return np.where(averaged > 0.5, 1, 0)
        except:
            print('not divisible by ', n)

    def modulate(self, data):
        length = len(data)
        t = np.linspace(0, length, length)
        mod_high = self.weight_high * np.multiply(np.sin(self.freq_high * t * 2 * np.pi), data)
        mod_low = self.weight_low * np.multiply(np.sin(self.freq_low * t * 2 * np.pi), 1 - data)
        return mod_high + mod_low

    def demodulate(self, data, freq_high, freq_low):
        t = np.linspace(0, 1 / self.fs, self.rate)

        sin_high = np.sin(freq_high * t * 2 * np.pi)
        sin_low = np.sin(freq_low * t * 2 * np.pi)

        data_matrix = np.reshape(data, (len(data) // self.rate, self.rate))
        sol_high = np.abs(np.dot(sin_high, np.transpose(data_matrix)))
        sol_low = np.abs(np.dot(sin_low, np.transpose(data_matrix)))

        diff = sol_high - sol_low
        demodulated = np.abs(np.ceil(diff / self.rate))

        starts = np.transpose(data_matrix)
        starts[0] = np.repeat(np.array([1]), data_matrix.shape[0])
        testStart = 410030

        markedStarts = np.transpose(starts)
        '''
        plt.plot(np.reshape(markedStarts[testStart//160:testStart//160 +6], 6*160))
        plt.show()
        plt.plot(sin_high)
        plt.show()
        plt.plot(sin_low)
        plt.show()
        plt.plot(np.dot(sin_high, np.transpose(data_matrix[testStart // 160:testStart // 160 + 6])))
        plt.show()
        plt.plot(np.dot(sin_low, np.transpose(data_matrix[testStart // 160:testStart // 160 + 6])))
        plt.show()
    
        plt.plot(np.dot(sin_low, np.transpose(data_matrix)))
        plt.show()
    
        plt.plot(np.dot(sin_high, np.transpose(data_matrix)))
        plt.xlabel('bits')
        plt.ylabel('integral sine high square')
        plt.show()
        '''

        return demodulated

    def doubleDemodulate(self, data):
        part1 = self.demodulate(data, self.freq_high, self.freq_low)
        part2 = self.demodulate(data, self.f3, self.f4)
        return np.concatenate((part1, part2))

    def calculateOffsetToTransmission(self, zeroOne, data):
        testCorr = signal.correlate(data, zeroOne, mode="same")

        # TODO improve this offset calculation
        indices = np.where(testCorr > np.max(testCorr) - 2)
        if len(indices) > 0 and len(indices[0] > 0):
            return indices[0][0]
        else:
            return indices

    def truncateToTauS(self, data, offset):
        truncated_start = data[(offset % self.rate):]
        res = truncated_start[:len(truncated_start) - (len(truncated_start) % self.rate)]
        return res

    def convertToOneMinusOne(self, data):
        return 2 * data - 1

    def removePilots(self, data):
        pilot_1_converted = self.convertToOneMinusOne(self.pilot1.astype(np.float32))
        pilot_2_converted = self.convertToOneMinusOne(self.pilot2.astype(np.float32))

        offset_1 = self.calculateOffsetToTransmission(pilot_1_converted, self.convertToOneMinusOne(data)) - len(self.pilot1) // 2
        trunc_1 = data[offset_1 + len(self.pilot1):]
        offset_2 = self.calculateOffsetToTransmission(pilot_2_converted, self.convertToOneMinusOne(trunc_1)) - len(self.pilot2) // 2
        trunc_2 = trunc_1[:offset_2]
        return trunc_2

    def removeDoubleModPilots(self, singleDemod, originalData):
        pilot_1_converted = self.convertToOneMinusOne(self.pilot1.astype(np.float32))
        pilot_2_converted = self.convertToOneMinusOne(self.pilot2.astype(np.float32))

        offset_1 = self.calculateOffsetToTransmission(pilot_1_converted, self.convertToOneMinusOne(singleDemod)) - len(self.pilot1) // 2
        trunc_1 = singleDemod[offset_1 + len(self.pilot1):]
        offset_2 = self.calculateOffsetToTransmission(pilot_2_converted, self.convertToOneMinusOne(trunc_1)) - len(self.pilot2) // 2

        result = originalData[self.rate * (offset_1 + len(self.pilot1)):]
        return result[:self.rate * offset_2]

    def findOffsetToFirstChange(self, data):
        firstChange = self.modulate(self.repencode(np.array([1, 0]), self.rate))
        return self.calculateOffsetToTransmission(firstChange, data)

    def bitsToBytes(self, bits):
        binaryBites = np.reshape(bits, ((len(bits) // 8), 8))
        dataAsBytes = np.packbits(binaryBites, axis=1).flatten().tobytes()
        return dataAsBytes

    def writeToFile(self, path, data):
        file = open(path, "wb")
        file.write(data)
        file.close()

    def recordAudio(self, duration, save_recording=False, recording_name=None):
        seconds = duration
        myrecording = sd.rec(int(seconds * self.audioSampleRate), samplerate=self.audioSampleRate, channels=1)
        sd.wait()  # Wait until recording is finished

        recording = np.reshape(myrecording, myrecording.shape[0])

        if save_recording:
            file_name = recording_name
            if not recording_name.endswith('.wav'):
                file_name = recording_name + '.wav'

            scipy.io.wavfile.write(file_name, self.audioSampleRate, recording.astype(np.float32))

        return recording

    def getAvailableAudioDevices(self):
        return sd.query_devices(device=None, kind=None)

    def setAudioInputDevice(self, device_id):
        self.audioDeviceId = device_id
        sd.default.device = device_id

    def gateInput(self, data):
        thresh = 2 * np.max(data[:self.audioSampleRate//2])
        return np.where(np.abs(data) < thresh, 0, data)

    def integrityCheck(self, data):
        expected_hash = data[-32:]
        received_hash = hashlib.sha256(data[:len(data) - 32]).digest()
        print('calculated hash:', received_hash)
        return expected_hash == received_hash


    def test(self, rec_duration, testBitRepetitions, encodeRepetitions, hamming):
        expected = self.getTestBits(testBitRepetitions)

        if hamming:
            actual = self.receiveHammingEncoded(rec_duration, repetitions=encodeRepetitions, bits=True,
                                                save_file=True, recording_name='lastTransmission.wav')
        else:
            actual = self.receiveRepencoded(rec_duration, repetitions=encodeRepetitions, bits=True,
                                            save_file=True, recording_name='lastTransmission.wav')

        print('actual: ', actual)
        print('length of actual:', len(actual))

        diff = expected - actual[:len(expected)]
        error_sum = np.sum(np.abs(diff))

        print('error sum ', error_sum)
        print('error weight', np.sum(diff))
        print('error percentage', error_sum / len(expected) * 100)

    def receiveRepencoded(self, duration, repetitions=3, bits=False, from_file=False, file_path=None,
                          save_file=False, recording_name=None, plot=False):
        '''
        Starts a recording or reads audio from a wav file. Then demodulates the input and decodes it
        :param duration: Number of seconds that should be recorded
        :param repetitions: Number of repetitions used to encode each bit. Must be the same as in the sender
        :param bits: If true, the method will return a np.array containing the decoded bits. Else it will return bytes
        :param from_file: If True the input will be read from a wav file and no recording will be started
        :param file_path: Path to the input wav file
        :param save_file: if True the recording will be saved to a wav file
        :param recording_name: Name and path of the file the recording should be saved to
        :param plot: If True the recording will be shown in a plot
        :return: Demodulated and decoded data as bytes or as bits depending on parameter bits.
        '''
        data_in = None
        if from_file:
            data_in = self.readWav(file_path)
        else:
            data_in = self.recordAudio(duration, save_file, recording_name)

        off = self.findOffsetToFirstChange(data_in)

        if off > self.audioSampleRate // 2 + self.rate // 2:
            data_in = self.gateInput(data_in)

        res = np.zeros(len(data_in) // self.rate - 1)
        for i in range(self.rate // 32):
            data_in2 = np.copy(data_in)
            offset = self.findOffsetToFirstChange(data_in2) + 16 * i
            truncated = self.truncateToTauS(data_in2, offset)
            demodulated = self.demodulate(truncated, self.freq_high, self.freq_low)
            res = np.add(res, demodulated[:len(data_in) // self.rate - 1])

        demodulated = np.where(res > self.rate // 64, 1, 0)
        '''
        plt.plot(res[2500:3000])
        plt.xlabel('bits')
        plt.ylabel('aggregated demodulation')
        plt.show()
        '''
        no_pilots = self.removePilots(demodulated)
        decoded = self.repdecode(no_pilots, repetitions)

        if plot:
            plt.plot(data_in)
            plt.show()

        if bits:
            return decoded
        else:
            try:
                data_as_bytes = self.bitsToBytes(decoded)
                if self.integrityCheck(data_as_bytes):
                    print('Data received correctly, hashs matched')
                    return data_as_bytes[:-32]
                else:
                    print('Data seems to be corrupted, the hashs did not match')
            except:
                print('could not convert bits to bytes. \nData might not be divisible by eight')

    def receiveHammingEncoded(self, duration, repetitions=3, bits=False, from_file=False, file_path=None,
                          save_file=False, recording_name=None, plot=False):
        '''
        Starts a recording or reads audio from a wav file. Then demodulates the input and decodes it
        Use this method to receive data, if the sender is using Hamming encoding
        :param duration: Number of seconds that should be recorded
        :param repetitions: Number of repetitions used to encode each bit. Must be the same as in the sender
        :param bits: If true, the method will return a np.array containing the decoded bits. Else it will return bytes
        :param from_file: If True the input will be read from a wav file and no recording will be started
        :param file_path: Path to the input wav file
        :param save_file: if True the recording will be saved to a wav file
        :param recording_name: Name and path of the file the recording should be saved to
        :param plot: If True the recording will be shown in a plot
        :return: Demodulated and decoded data as bytes or as bits depending on parameter bits.
        '''
        data_in = None
        if from_file:
            data_in = self.readWav(file_path)
        else:
            data_in = self.recordAudio(duration, save_file, recording_name)

        off = self.findOffsetToFirstChange(data_in)

        if off > self.audioSampleRate // 2 + self.rate // 2:
            data_in = self.gateInput(data_in)

        res = np.zeros(len(data_in) // self.rate - 1)
        for i in range(self.rate // 32):
            data_in2 = np.copy(data_in)
            offset = self.findOffsetToFirstChange(data_in2) + 16 * i
            truncated = self.truncateToTauS(data_in2, offset)
            demodulated = self.demodulate(truncated, self.freq_high, self.freq_low)
            res = np.add(res, demodulated[:len(data_in) // self.rate - 1])

        demodulated = np.where(res > self.rate // 64, 1, 0)
        no_pilots = self.removePilots(demodulated)
        rep_decoded = self.repdecode(no_pilots, repetitions)
        decoded = self.hamming.decodeAndCorrectStream(rep_decoded)

        if plot:
            plt.plot(data_in)
            plt.show()

        if bits:
            return decoded
        else:
            try:
                data_as_bytes = self.bitsToBytes(decoded)
                if self.integrityCheck(data_as_bytes):
                    print('Data received correctly, hashs matched')
                    return data_as_bytes[:-32]
                else:
                    print('Data seems to be corrupted, the hashs did not match')
            except:
                print('could not convert bits to bytes. \nData might not be divisible by eight')


    def testDoubleDecode(self):
        #input = self.readWav('test_double.wav')
        input = self.recordAudio()
        truncated = self.truncateToTauS(input, self.findOffsetToFirstChange(input))
        singleDecoded = self.demodulate(truncated, self.freq_high, self.freq_low)
        noPilots = self.removeDoubleModPilots(singleDecoded, truncated)
        doubleDemod = self.doubleDemodulate(noPilots)
        actual = self.repdecode(doubleDemod, 3)

        print('actual: ', actual)

    def testDecode(self):
        a = self.repdecode(np.array([1,1,1,0,0,1,0,0,1,0,1,1]), 4)
        print(a)