from Sender import Sender
from Receiver import Receiver
import scipy
import numpy as np
import scipy.io
import scipy.io.wavfile
import matplotlib.pyplot as plt
from scipy import signal


def readFromFile(path):
    file = open(path, "rb")
    data = file.read()
    file.close()
    return data

def readWav(file_name) -> np.ndarray:
    rate, data = scipy.io.wavfile.read(file_name)

    if data.dtype == np.int16:
        return data.astype(np.float32, order='C') / 32768.0
    return data


testData = readWav('testbitsnopilots.wav')
subset = readWav('wrongbitstest.wav')


r = Receiver()
rate = 160

corr = 235292


offset = r.findOffsetToFirstChange(testData)
truncated = r.truncateToTauS(testData, offset)

plt.plot(testData[corr - len(subset)//2:corr + len(subset)//2])
plt.show()

plt.plot(subset)
plt.show()

plt.plot(truncated)
plt.show()
demod = r.demodulate(truncated, 1/16, 1/40)

result = []
start = 0
for i in range(20):
    if i == 2:
        a = 5
        plt.plot(truncated[start: start + 10 * 36 * 160])
        plt.show
        a = 6
    #part_demod = r.demodulate(truncated[start: start + 10*36 * 160], 1/16, 1/40)
    #result.append(list(r.repdecode(part_demod, 10)))
    start = start + 10*36*160


print('result', result)
print(demod)
print(len(demod[1:]))
print(repdecode(demod[1:], 10))

sender = Sender()
demod = repdecode(demod, 10)
expected = sender.getTestDataAsBits()
error_sum = np.sum(np.abs(expected - demod))
print('error sum', error_sum)
print('error weight', np.sum(expected - demod))
print('error percentage', error_sum / len(expected) * 100)