# BACnet Location Verification

This projects provides a system to verify a network users location.


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
| Microcontroller | [Arduino Uno WiFi REV2](https://www.conrad.ch/de/p/arduino-ag-entwicklungsboard-uno-wifi-rev2-1969870.html)   | CHF 44 |
| GPS Module      | [NEO-6M](https://www.berrybase.ch/audio-video/navigation/u-blox-neo-6m-gps-ttl-empf-228-nger-inkl.-antenne)        | CHF 8 |
| RFID Reader + Tag/Card | [RFID-RC522 Set](https://www.berrybase.ch/sensoren-module/rfid-nfc/rfid-leseger-228-t-mit-spi-schnittstelle-inkl.-karte-dongle)   | CHF 5|
| Display    | [Joy-it SBC-LCD 16x2](https://www.conrad.ch/de/p/joy-it-sbc-lcd16x2-display-modul-6-6-cm-2-6-zoll-16-x-2-pixel-passend-fuer-raspberry-pi-arduino-banana-pi-cubieboar-1503825.html)   | CHF 14|
|Shipping| - | CHF 18|
|||**CHF 89**|

## Authenticity

To ensure the truthfulness of the package sent to the feed, the package will be signed and sent to the network using another project in the same class [BACnetCore](https://github.com/RaphaelKreft/BACnet/tree/master/21-fs-ias-lec/3-BACnetCore).
