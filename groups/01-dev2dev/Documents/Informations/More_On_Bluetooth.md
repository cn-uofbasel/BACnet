# More on Bluetooth Programming
(All this info is NOT update and only applies for Bluetooth 2.x)
## Radio Frequencies and Channel Hopping
Bluetooth devices never stay on the same channel.
An actively communicating Bluetooth device changes channels more than 1500 times per second.
Bluetooth devices that communicate together must hop channels together.
Newer devices also use adaptive frequency hopping (avoid channels that are noisy or have high interference).
## Bluetooth Networks
Most of this stuff is handled automatically by Bluetooth hardware and low-level device driver. As a programmer, we only have to make sure that a connection is made.
### Piconet
* Two devices that are communicating with each other form a "piconet".
* A piconet can have up to 8 devices in total
* One device in every piconet acts as "master" which has two roles
  * to tell other devices ("slaves") which frequencies to use
  * to make sure the devices communicate in an orderly fashion/take turns

### Scatternet
* It's theoretically possible for one Bluetooth device to be engaged in more than one piconet
* In this case, the two different piconets are called a scatternet
* It's just a name and doesn't give more extra functionality

## Security - PINs and Link Keys
* Two Bluetooth devices can verify their respective identities using an authentication procedure
* Once authenticated, they can encrypt all the data packets they exchange
* Authentication can also be performed without encryption
* The principle of authentication is the "shared secret", it's like a secret password/handshake
  * The shared secret in Bluetooth is known as the PIN: up to(!) 16 alphanumeric chars
  * The PIN can be hard-coded or can be entered by the user via prompt
  * Each devices uses the PIN to generate a "link key", which is saved on both devices.
  * During the pairing, the PIN is never actually transmitted over the air
* The first time 2 devices go through authentication or encryption is called "pairing"
* Encryption takes effect at the physical link level and is usually handles by the OS instead of by applications.
* Neither procedure is foolproof

* Bluetooth 2.1 introduced "Simple Pairing". In most situations:
  * Users will not need to enter a PIN
  * The PIN is automatically generated and the user is only prompted to accept or reject a pairing.
  * It also introduced stronger encrpytion techniques like SSH, IPSec, PGP, SSL

## Security modes
* Security Mode 1: The device never initiates authentication or encryption with a connected device, but will comply if the connected device requests either.
* Security Mode 2: The device initiates auth and encryption if requested by individual, local applications. This is the default mode
* Secutrity Mode 3: The device initiates authentication and encryption as soon as any connection is established AND refuses to communicate with unpaired devices.

## Bluetooth Profiles
Bluetooth Profiles are methods and specifications that define standardized ways to perform tasks such as:
* transferring files
* playing music
* using nearby printers
* and so on
Bluetooth Profiles are identical in nature to the Internet RFCs, but also complementary. Well-known and widely used BT Profiles are:
* OBEX Object Push: Allows devices to send and receive arbitrary data files. OBEX stands for "object exchange", which can be either pushed or pulled
* File Transfer: Allows one device to access the filesystem of another device to send and receive files. Different from OBEX Object Push
* Dial-Up Networking: Allows devices to use BT devices connected to a phone line as modems to make calls and connect to the Internet.
* Hands-Free Audio: Name says it all
* Advanced Audio Distribution:
* Personal Area Network: Allows Bluetooth devices to form IP networks to share one device's Internet connection with the other a.k.a Hotspot
* Human Interface Device: Allows peripheral devices to connect to the device.
* Serial Port Profile: Allows RFCOMM connections between two Bluetooth devices to be treated as serial cable connections.
* many more...


## Device Discovery further explained
* Bluetooth splits the 2.4GHz band into 79 channels with all devices in a piconet using exactly one of these channels at a time
* 32 of these channels are used for detecting nearby devices and establishing connections
* An Inquiring device sends inquiry messages on these channels and discoverable devices periodically listen on them
* The Inquiry process for a nearby device is very technical and at this point we refer back to the book
