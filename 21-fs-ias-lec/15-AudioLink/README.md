# README AudioLink

original git repository: https://github.com/kian-hunziker/audioLink

These python scripts can be used to transmit arbitrary data in byte format from one device to a second using sound.

## SETUP
### Prerequisites for Usage
In order to use this script, the sender device needs to be connected to a speaker and the receiving device needs 
hava an audio input e.g. a microphone.

The libraries which must be installed prior to usage are:

- Numpy (https://numpy.org/)
- Scipy (https://www.scipy.org/)
- SimpleAudio (https://pypi.org/project/simpleaudio/)
- Sounddevice (https://python-sounddevice.readthedocs.io/en/0.4.1/)

### Setup
Once the libraries, speakers and microphones are installed the receiver can be setup. 

The available audio devices (e.g. connected microphones) can be queried using getAvailableAudioDevices().
The preferred input device can then by set by passing the corresponding Device ID to setAudioInputDevice(ID)
```
from Receiver import Receiver

receiver = Receiver()
print(receiver.getAvailableAudioDevices())
receiver.setAudioInputDevice(4)

```

### Calibration
We can now calibrate the transmission amplitudes. To do so, run receiver.calibrate() on the receiving device. This 
will start a short recording. As soon as the recording started, run sender.sendCalibration() which will play the 
calibration tones.

```
from Receiver import Receiver

receiver = Receiver()
amp_sin_high, amp_sin_low = receiver.calibrate()
print(amp_sin_high, amp_sin_low)
```

```
from Sender import Sender

sender = Sender()
sender.sendCalibration()
```

The output generated by receiver.calibrate() represents the amplitudes of the high and the low modulation frequencies. 
These need to be passed to sender.setTransmissionAmplitudes() to finalise the calibration. For example:

```
from Sender import Sender

sender = Sender()
sender.setTransmitionAmplitudes(0.54213, 0.26384)

```

## Usage
Once setup and calibration are done, the usage is rather straight forward. Import both Sender and Receiver and create 
instances. Start a recording on the receiving side. As soon as the recording is started, start the transmission on 
the sender side

```
from Receiver import Receiver

receiver = Receiver()
recording_duration = 28
encoding_repetitions = 3
data = receiver.receiveRepencoded(recording_duration, encoding_repetitions)
```

```
from Sender import Sender

sender = Sender()
sender.setTransmitionAmplitudes(0.54213, 0.26384)
encoding_repetitions = 3
data = sender.readFromFile('testFiles/pacman2.bmp')
sender.sendDataRepencoded(data, encoding_repetitions)

```

As of now the recording duration must be known in advance. It does not have to be accurate but has to be longer than 
the duration of the transmission so that the full transmission can be recorded. 

To estimate the duration of a transmission (if the default parameters are used) use:

seconds = number_of_bytes * 8 * encoding_repetitions * 160 / 44100

If custom parameters are used, take:

seconds = number_of_bytes * 8 * encoding_repetitions * tauS / sample_rate