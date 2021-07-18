# Project Introduction to Internet and Security: Group 13 - Raptor Code

## Content

* [About](#About)
* [How to Use](#How-to-Use)
* [About the Demo](#About-the-Demo)
* [Members](#Members)

## About

Raptor codes are a subgenre of fountain codes and are used to transmit data over a medium with high probability of errors.
The encoder therefore generates multiple data packages which with a decoder can try to decode the original data.
The decoder doesn't care about which packages it receives and which not. At one point it has enough packages to decode the original data.

A more detailed overview of what a Raptor code is can be seen in our Report.

## How to Use

Our code can be found in the /src folder.
There are to main classes which on needs to use, to access our functionality:

### encoder.py

In the /src/encoder.py file there is the Encoder class. On the side of the sender there needs to be an encoder to encode the to be transmitted data.
```
from encoder import Encoder

encoder = Encoder()
for transmissionData in encoder.encode(data):
    send(transmissionData)
```
The Encoder::encode() function takes bytes as input and creates packages to transmit. Since the encoder does not know, 
at which point the decoder has enough information, it just keeps generating data to transmit until a certain number has been reached.
The input data must be a multiple of 32bits in size, since the encoder will split it in such chunks.
In general the encode function will generate for each 32bit chunk of the input data 10'000 such transmission packages.
This number can be changed by a number in the constructor:

```
encoder = Encoder(500)  # this encoder will only generate 500 packages for each 32 bit chunk.
```

The data which should be transmitted is of the form:
```
# As can be found in /src/utils.py
class TransmissionData:
    Integer
    Integer
    Integer
    (Integer, Integer)  # Tupel
```

### decoder.py
In the /src/decoder.py file there is the Decoder class. In the side of the receiver there needs to be an decoder to decode the received massages.

```
from decoder import Decoder

decoder = Decoder()
for reveivedData in receive():
    decoded = decoder.decode(receivedData)
    if decoded is not None:
        useData(decoded)
```

The Decoder::decode() returns either None if it couldn't decode the data with the until now received data,
or returns bytes once it could decode information. The decoder can work with multiple different encoded Data at the same time,
but once it has decoded information it will forget, that it has decoded that information and once there comes more data packages about it,
it starts over for that information and once it has again enough information to decode it will return that information again.

The decoder takes the same input as is described as output in [encoder.py](#How-to-Use)

---

## About the Demo

You can find a demo in the file /src/demo.py
To use it, try:
```
python demo.py  
```

The demo simulates a sender and receiver. It also offers some additional settings such as a possibility to activate data loss
and the probability of that data loss. You can steer this with the values HAS_PACKAGE_LOSS and PROBABILITY_OF_LOSS.
You can also set, whether the sender stops sending packages once the receiver could decode the information via the variable: STOP_ENCODER_ON_DECODING.
Lastly you can activate/deactivated the output of the statistic via the PRINT_STATISTICS variable.

---

## Members

* **Ken Walzer** 
* **Cyrill Imahorn**