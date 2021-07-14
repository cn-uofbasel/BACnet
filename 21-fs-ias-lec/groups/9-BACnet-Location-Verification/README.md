# BACnet Location Verification

This projects provides a system to verify a network users location using RFID and GPS technology.


## Idea / Motivation

For tracking or information purposes, members of the network should be able to verify their positions and send them to the network.

## How it works

At the core, the system consists of two entities:

* RFID Chip
* Reader

The chip contains information of the owner and can interact with a reader by transmitting its stored information to the reader.

The reader is an arduino with various modules including LCD screen, GPS module and an RFID reader. It takes information of a RFID chip and processes it with the information gathered by the GPS module. The compiled information package is then sent to a network feed via its protocol.

Possible part list:

| Type            | Model         | Price  |
| --------------- |:-------------:| :------:|
| Microcontroller | [Arduino Uno](https://www.digitec.ch/de/s1/product/arduino-uno-atmega328-entwicklungsboard-kit-5764177)   | CHF 34 |
| GPS Module      | [NEO-6M](https://www.berrybase.ch/audio-video/navigation/u-blox-neo-6m-gps-ttl-empf-228-nger-inkl.-antenne)        | CHF 8 |
| RFID Reader + Tag/Card | [RFID-RC522 Set](https://www.berrybase.ch/sensoren-module/rfid-nfc/rfid-leseger-228-t-mit-spi-schnittstelle-inkl.-karte-dongle)   | CHF 5|
| Display    | [Joy-it SBC-LCD 16x2](https://www.conrad.ch/de/p/joy-it-sbc-lcd16x2-display-modul-6-6-cm-2-6-zoll-16-x-2-pixel-passend-fuer-raspberry-pi-arduino-banana-pi-cubieboar-1503825.html)   | CHF 14|
|Shipping| - | CHF 29|
|||**CHF 90**|
## Prerequisites
### Python
<ul>
<li>Python 3 environment</li>
<li>Python packages:</li>
	<ul>
	<li>pySerial</li>	
	<li>cbor2</li>
	<li>pyNaCl</li>
	<li>sqlalchemy</li>
	<li>testfixtures</li>
	</ul>
</ul>

cbor2 and pyNaCl (and to further extent, sqlalchemy and testfixtures) are used by [EventCreationTool](https://github.com/cn-uofbasel/BACnet/tree/master/20-fs-ias-lec/groups/04-logMerge/eventCreationTool) and [LogMerge](https://github.com/cn-uofbasel/BACnet/tree/master/20-fs-ias-lec/groups/04-logMerge/logMerge) created by another group's project from spring semester 2020.

The python packages can be installed using pip:
```
> pip install pyserial
> pip install cbor2
> pip install pynacl
> pip install sqlalchemy
> pip install testfixtures
```

### Arduino
<ul>
	<li>Arduino IDE</li>
	<li>Arduino libraries:</li>
	<ul>
		<li>MFRC522</li>
		<li>LiquidCrystal_I2C</li>
		<li>TinyGPS++</li>
	</ul>
</ul>

MFRC522 and LiquidCrystal_I2C can be installed using the Arduino IDE Library Manager.

TinyGPS++ must be added in the Arduino IDE through *Sketch -> Include Library -> Add .ZIP Library...* and either using the .zip file from the repository or obtaining the newest version from the [website](https://github.com/mikalhart/TinyGPSPlus/releases)

## Setup and Run
Connect the hardware modules to the Arduino Uno using following pins:

|                  | Module Pin | Arduino Uno Pin |
|------------------|------------|-----------------|
| RFID-RC522       | 3.3V       | 3.3V            |
|                  | RST        | 9               |
|                  | GND        | GND             |
|                  | IRQ        | 2               |
|                  | MISO       | 12              |
|                  | MOSI       | 11              |
|                  | SCK        | 13              |
|                  | SDA        | 10              |
| 16x2 LCD Display | GND        | GND             |
|                  | VCC        | 5V              |
|                  | SDA        | SDA             |
|                  | SCL        | SCL             |
| NEO-6M           | VCC        | 5V              |
|                  | RX         | 3               |
|                  | TX         | 4               |
|                  | GND        | GND             |

Compile and upload the *BasicFunctionality.ino* to the Arduino Uno (remember the COM port used!)

Run the *ArduinoGPS.py* script with
```
> python3 /path/to/ArduinoGPS.py
```


## Authenticity

To ensure the truthfulness of the package sent to the feed, the package will be signed and sent to the network using SHA256 and a private-key.
