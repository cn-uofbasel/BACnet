# Log File Creation and Parsing: basic demo

For all code examples on this page we assume
```
$ cd src/demo
```

Terminology: Note that 'feed' = 'log' = 'append-only log'


The following three library files contain Python class definitions for
BACnet that can be imported into a main program. Moreover, these files
also serve as standalone tools, as demonstrated on this page.

```
lib/crypto.py
lib/feed.py
lib/pcap.py
```

## Creating a new Feed Identifier

```
$ ./lib/crypto.py
{
  'type': 'ed25519',
  'public': '57e8ef8485c906e92c7376b8a1b4a9e0b1ad47b1e1d8df2091846452a21099db',
  'private': '79bea7ee00876b083741c5a42bea648a4e794102da02457fc7adc027d26047da'
}
```

A new random key pair is generated.

The public part is used as the identifier of a feed. The private part
must be kept secret and is used for digitally signing each event for
that feed. Verification of the signature can be done using the public
key only, and because each event contains the feed identifier (=public
key), an event's signature can be checked without additional data and
by everybody. Best is to pipe the output of the ```crypto.py``` tool
into a key file:

```
$ ./lib/crypto.py >alice-secret.key
```

Note that in BACnet we will use the public key as the identifier for a feed.


### Generating a HMAC_SHA256 shared secret instead of an ED25519 keypair

```
$ ./lib/crypto.py --hmac
# new HMAC_SHA256 key: share it ONLY with trusted peers
{
  'type': 'hmac_sha256',
  'feed_id': '3c8425dd67365ebc143eb83fb5908c9e63af747bd43db41fd6aeccf3f0798164',
  'private': 'dd320ace790c9c32ff9f401140aa3525'
}
```

For convenience we also create a random feed ID, although it has no
coupling with the generated shared secret.


## Creating a new Feed file (in pcap format)
```
$ ./lib/feed.py --keyfile alice-secret.key alice.pcap create
['nop', 'first event']
<CTRL-D>
$ 
```

This creates a new pcap file ```alice.pcap```. The first event's
payload is read from STDIN and must be written as a Python data type,
and terminated by typing ```CTRL-D``` on a new line. The ```create``` command
works for both key types (ed25519 or hmac), as found in the key file.


## Appending to an existing Feed file
```
$ ./lib/feed.py --keyfile alice-secret.key alice.pcap append
['chat/post', 'Hi Bob']
<CTRL-D>
$ 
```
The ```append``` command
works for both key types (ED25519 or HMAC), as found in the key file.
Note that (as a convention) we structure the event's payload as a list of two
strings: the first indicates the application, the second is a parameter.


## Checking the validity of a Feed (and also dumping the event payloads)

```
$ ./lib/feed.py alice.pcap check
Checking feed 57e8ef8485c906e92c7376b8a1b4a9e0b1ad47b1e1d8df2091846452a21099db
event 1 ok, content=['nop', 'first event']
event 2 ok, content=['chat/post', 'Hi Bob']
$
```

This tool verifies that in the given pcap file
- (a) all events have the same feed ID,
- (b) all events have consecutive sequence numbers,
- (c) each event contains a hash value pointing to the previous event,
- (d) each event has a valid cryptographic signature.

Note that the ```--keyfile``` parameter was not necessary for an
ED25519 keypair: signature validation can be done without having
access to the secret key.

In case of an HMAC signature, however, the corresponding keyfile MUST
be passed as a parameter:

```
$ ./lib/feed.py --keyfile sensor-hmac.key sensor.pcap check
Checking feed 143e3f5e85123f6e1ee43a041cc5b60d1ff04d8958917d7eab32b86d62f72bbb
event 1 ok, content=['nop', 'first event for humidity sensor']
...
```

## Dumping the content of a pcap file containing events from _many_ sources

```
# creating a pcap file with events from different feeds:
$ cat alice.pcap bob.pcap >mixed.pcap

# dumping the content (and the hash value of the meta field)
$ ./lib/pcap.py mixed.pcap
** fid=57e8ef..1099db, seq=1, 161 bytes
   hashref=9a804abf91f0c92b6458bca8e3db6bcc8a7222ed7d7618db594a395deb918df0
   content=['nop', 'first event']
** fid=57e8ef..1099db, seq=2, 195 bytes
   hashref=1a224ec93b1135722d9b760f32854a99e3a146ba85b0717b74bd7d93d5994fa3
   content=['chat/post', 'Hi Bob']
** fid=6ea8b5..323e9e, seq=1, 169 bytes
   hashref=824086b5d89cb80d59ac0487b157a60adc38ef703009a7a7087ceeac34720639
   content=['nop', 'first event of Bob']
```

The ```pcap.py``` tool does _not_ verify the consistency of the file nor
event signatures etc.

---