# I&S Group #3: Cryptochat

This implementation is based on the SubjectiveChat,
which was implemented by Group #3 in the spring semester
of 2020. It adds asymmetric encryption to that implementation,
such that the cleartext messages neither get saved in the feed,
nor on the USB-sticks used within the Sneakernet. This implementation
additionally builds upon the functionality of the following implementations:

1. Sneakernet
2. LogMerge
3. LogStore
4. FeedControl

For a detailed description of the functionality of the aforementioned
implementations, please refer to their respective READMEs, which 
can also be found in this repository.

Our implementation has been tested on devices running Linux,
but it should also work on other operating systems. Python 3.8 was used 
for implementation and testing.

**Table of Contents:**

1. Dependencies
2. How to Use
   1. Initiation of a Chat Session
   2. Actual Conversation
3. Encryption
    1. Method
    2. Key Exchange
    3. Problems
4. Contributors
   

## 1. Dependencies
Because this implementation builds upon the projects SubjectiveChat,
Sneakernet, LogMerge, LogStore and FeedControl, their dependencies are required
for our implementation to work. Please note that their READMEs
are outdated in regard to certain dependencies, because they
use outdated versions. Therefore, the following dependencies
should be downgraded as such in July 2021:

`$ pip3 install sqlAlchemy==1.3.23`

`$ pip3 install pyglet==1.5.3`

Our implementation additionally requires the following dependencies:

`$ sudo apt-get install python3-tk`

`$ sudo apt-get install python3-pyglet`

`$ sudo apt-get install python-pil.imagetk`

`$ pip3 install pyDH`

`$ pip3 install pycryptodome`

`$ pip install pybase64`

## 2. How to use

The usage of our implementation requires the interplay between multiple
different implementations. For a more detailed dissection of the SubjectiveChat's interface and
functionality we kindly ask the reader to consult the relevant README.
This README concerns itself primarily with demonstrating what we have
actively contributed to the BACnet.

### i. Initiation of a Chat Session

We assume two Clients, Client 1 and Client 2, who want to establish a
chat, such that messages can be passed between them confidentially.
This is done as follows:

Client 1 needs to create a Masterfeed by starting FeedControl.
That is done by running the following command:

`$ python3 feed_control.py ui`

A window will open, which can be immediately closed. The SubjectiveChat
can be started by running the following command:

`$ python3 subjective_chat.py`

A window will open. In there a private chat can be created by clicking
**create** and then **Private Chat**. A random string of characters will
show, which can be edited and which will represent the chat's ID. By clicking
**OK** the chat can be created.

This all happens locally. In order to export this information (the newly
started chat) the Sneakernet needs to be started, which is done by running
the following command:

`$ python3 guiSneakernet.py`

There, the USB-stick used for the Sneakernet needs to be chosen, and an Update
needs to be performed, in order to export Client 1's Masterfeed
onto the USB-stick.

Thereafter, the USB-stick needs to be transferred to Client 2. They first
have to create a Masterfeed by starting FeedControl. Then they need to 
start Sneakernet and perform an update. Thereby, their Masterfeed is exported
onto the USB-stick.

The stick then needs to be transferred back to Client 1, who again starts
Sneakernet in order to get Client 2's Masterfeed and to gain knowledge
that a second user exists. After transferring the stick back to Client 2, they need
to again start Sneakernet to get that information.

Then the Client 2 needs to trust Client 1's Chat Feed by starting
FeedControl, clicking **Update FeedIDs**, clicking on the arrow
on the left of *Anon* (representing Client 1's Masterfeed), and then 
clicking on *chat* (representing Client 1's Chat Feed). The button
**Trust** needs to be clicked, whereafter Client 2 trusts Client 1's
Chat Feed. After again starting Sneakernet and performing an update
with the USB-stick, the SubjectiveChat can be started.

Therein the button **join** needs to be pressed. After entering the chat
ID specified by Client 1, we have successfully started a chat. (Tip: the
chat ID gets printed to the console when a client creates a chat.)

As previously  mentioned, starting a group chat works in an almost identical manner,
only trivially different to starting a private chat.

### ii. Actual Conversation

In order to continue chatting, the Client 1 must first trust the Client 2's
Chat Feed and both clients must im- and export using Sneakernet after 
receiving and before passing on the USB-stick.

## 3. Encryption

### i. Method

This implementation uses *Cipher Block Chaining* (CBC) for encryption.
CBC is a block cipher which works by XORing the previously encrypted
block with the next plaintext block before encryption. Thereby patterns
in the plaintext aren't recognizable in the ciphertext, which is especially
useful for images (which can also be encrypted with our implementation).
The first block is encrypted with the *Initialisation Vector* (IV), which is 
different for every encrypted message and is attached to the ciphertext in the 
Chat Feed.

![Alt text](https://www.researchgate.net/profile/Rhouma-Rhouma/publication/215783767/figure/fig1/AS:394138559238144@1470981363092/Cipher-block-chaining-CBC-mode-encryption.png "CBC")

### ii. Key Exchange

Our implementation encrypts the messages asymmetrically, which is achieved
with a Diffie-Hellman-Merkle key exchange. The implementation uses a 32-byte
private key, which is obtained by both parties sharing a public key. After every 
cycle of messages the shared private key is changed, therefore providing 
forward secrecy and backward secrecy. The public key always gets attached to the first message of
a new cycle. This way the participants can establish the new shared private key whenever
a new cycle has begun. If there are multiple messages per cycle the public key is only
attached to the very first message of this cycle, in order to minimize the workload on 
the transport layer.

### iii. Problems

In order to minimise seemingly redundant transportation of the USB-stick, we decided to
implement the key exchange as part of the first chat messages of every cycle. Because the program
needs both public keys to generate the common private key, the first cycle of messages
is only encrypted with a temporary symmetric key, which is also encrypted and then 
transmitted as part of the Chat Event. Consequently, the first cycle of messages is not
securely encrypted, because the symmetric key is transmitted together with the ciphertext 
which it encrypted (in order to at least make the message seem encrypted at first glance).
Only the replying messages and all thereafter are encrypted securely with a
truly private key.

On a more advanced level, our implementation delivers perfect backward- and forward-secrecy
for every cycle of messages. Meaning that if somehow an intruder would gain access to a 
private key, the intruder could decrypt all the messages (by all clients) of this cycle, but
he would not be able to decipher past or future messages. In conclusion our implementation that
originally aimed to implement the double ratchet algorithm is not exactly as secure as the 
DR-Algorithm. In an implementation that is secured with the DR-Algorithm, if an intruder obtained
a private key, they could only decrypt at most one message and not a whole cylce of messages.
We'd be pleased to hear if someone would integrate such an algorithm into our
implementation at some future point in time, which would allow for even better
encryption within the BACnet.

## 4. Contributors

Colin Saladin (colin.saladin@unibas.ch), Noah Müller (noah.mueller@stud.unibas.ch)
and Max Jappert (max.jappert@unibas.ch)