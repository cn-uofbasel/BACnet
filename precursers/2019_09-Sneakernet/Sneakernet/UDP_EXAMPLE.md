# Example 2: syncing two peers via UDP (on the same machine)

## Start configuration

Alice has 9 events in her log, plus 7 from Bob in 2.pcap:

```text
alice$ for i in logs/*; do C=`../dump-log.py $i | grep "{ 'app" | wc | cut -c 5-10`; echo $C $i ; done
9 logs/1.pcap
7 logs/2.pcap
alice$
```

Bob has 7 events in his log, and none from Alice:

```text
bob$ for i in logs/*; do C=`../dump-log.py $i | grep "{ 'app" | wc | cut -c 5-10`; echo $C $i ; done
7 logs/1.pcap
bob$
```

## Alice starts UDP Peer-to-Peer replication, as a responder

```text
alice$ ../udp-peer.py 
Welcome to SneakerNet

** starting replication tool
** peer-to-peer responder
** waiting on UDP port 4097

```

## Bob starts UDP Peer-to-Peer replication, as a initiator

```text
bob$ ../udp-peer.py 127.0.0.1
Welcome to SneakerNet

** starting replication tool
** peer-to-peer initiator: connecting ...
** talking to ('127.0.0.1', 4097) (responder), my UDP push_port is 5000
-- incoming cmd: b'PORT 4098'
-- incoming cmd: b'HAVE +TOLr0m0rwAhop64A6RW4tn8bwKQFZrNgPUV4S4umCB4=:7 +SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:9'
-- incoming push: 269 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:1
-- incoming push: 270 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:2
-- incoming push: 270 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:3
-- incoming push: 270 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:4
-- incoming push: 270 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:5
-- incoming push: 270 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:6
-- incoming push: 270 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:7
-- incoming push: 271 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:8
-- incoming push: 271 bytes
-- ingested event SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:9
** peer_loop done
bob$ 
```
Explanation:
- 127.0.0.1 means that responder and initiator run on the same machine (for this demo). In a LAN, this should be replaced with the IP address of the responder machine
- the handshake was successful (not shown in output)
- Bob received a PORT command, saying where-to he should send events
- Bob received from Alice a HAVE list (which feeds and their max sequence)
- in the background, Bob saw that he is missing Alice's feed SPQMT3a...
- in the background, Bob tells Alice what he WANTs
- then 9 events arrive at Bob's push port
- after 5 seconds of silence, the initiator software ends

## Continuation of Alice's output, once Bob connected:

```text

** talking to ('127.0.0.1', 4099) (initiator), my UDP push_port is 4098
-- incoming cmd: b'PORT 5000'
-- incoming cmd: b'HAVE +TOLr0m0rwAhop64A6RW4tn8bwKQFZrNgPUV4S4umCB4=:7'
-- incoming cmd: b'WANT +SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:1'
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:1
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:2
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:3
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:4
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:5
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:6
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:7
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:8
-- enqueue outgoing push for SPQMT3aGl9QRDYZCzv8oKC0QYp62XP5DiFTDKIzsaH4=:9
** peer_loop done
** waiting on UDP port 4097

```

Explanation:
- the handshake was successful (not shown in output)
- Alice received a PORT command, saying where-to she should send events
- Alice received from Bob a HAVE list - boring because she already has it
- Bob says what he WANTs
- Alice prepares 9 events to be sent
- after 5 seconds of silence, she goes back into waiting mode

---
