import secrets
import nacl.signing
import hashlib
import nacl.encoding
from BACnetstuff import Event
from BACnetstuff import Content
from BACnetstuff import Meta
from BACnetstuff import pcap
SIGN_INFO = {'ed25519': 0, 'hmac_sha256': 1}
HASH_INFO = {'sha256': 0}

# Only save private key, get signing_key again and then get the public key
private_key = secrets.token_bytes(32)
signing_key = nacl.signing.SigningKey(private_key)
public_key = signing_key.verify_key.encode()
# public key == feedID

# Create any Event
content = Content('chat/post', 'hello matilda')

# Get Hash Values of content and of previous, first message = previous_hack is None
hash_of_content = hashlib.sha256(content.get_as_cbor()).digest()
hash_of_prev = None

# Build header, 0 = sequence number
meta = Meta(public_key, 0, hash_of_prev, SIGN_INFO['ed25519'], [HASH_INFO['sha256'], hash_of_content])

# Sign the header
signature = signing_key.sign(meta.get_as_cbor()).signature

# Combine header, signature and content to one cbor encoded Event and create a list
event = Event(meta, signature, content).get_as_cbor()
list1 = [event]

# more events and appending them to the list
content = Content('chat/post', 'hello Emma, how are you?')

hash_of_content = hashlib.sha256(content.get_as_cbor()).digest()
hash_of_prev = hashlib.sha256(meta.get_as_cbor()).digest()

meta = Meta(public_key, 1, hash_of_prev, SIGN_INFO['ed25519'], [HASH_INFO['sha256'], hash_of_content])

signature = signing_key.sign(meta.get_as_cbor()).signature

event = Event(meta, signature, content)
event = event.get_as_cbor()
list1.append(event)


content = Content('chat/post', 'Im good, thanks! How are you and the kids?')

hash_of_content = hashlib.sha256(content.get_as_cbor()).digest()
hash_of_prev = hashlib.sha256(meta.get_as_cbor()).digest()

meta = Meta(public_key, 2, hash_of_prev, SIGN_INFO['ed25519'], [HASH_INFO['sha256'], hash_of_content])

signature = signing_key.sign(meta.get_as_cbor()).signature

event = Event(meta, signature, content).get_as_cbor()
list1.append(event)

###NEW FEED
# Only save private key, get signing_key again and then get the public key
private_key = secrets.token_bytes(32)
signing_key = nacl.signing.SigningKey(private_key)
public_key = signing_key.verify_key.encode()
# public key == feedID

# Create any Event
content = Content('chat/post', 'hello matilda2')

# Get Hash Values of content and of previous, first message = previous_hack is None
hash_of_content = hashlib.sha256(content.get_as_cbor()).digest()
hash_of_prev = None

# Build header, 0 = sequence number
meta = Meta(public_key, 0, hash_of_prev, SIGN_INFO['ed25519'], [HASH_INFO['sha256'], hash_of_content])

# Sign the header
signature = signing_key.sign(meta.get_as_cbor()).signature

# Combine header, signature and content to one cbor encoded Event and create a list
event = Event(meta, signature, content).get_as_cbor()
list1.append(event)

# more events and appending them to the list
content = Content('chat/post', 'hello Emma, how are you?2')

hash_of_content = hashlib.sha256(content.get_as_cbor()).digest()
hash_of_prev = hashlib.sha256(meta.get_as_cbor()).digest()

meta = Meta(public_key, 1, hash_of_prev, SIGN_INFO['ed25519'], [HASH_INFO['sha256'], hash_of_content])

signature = signing_key.sign(meta.get_as_cbor()).signature

event = Event(meta, signature, content)
event = event.get_as_cbor()
list1.append(event)


content = Content('chat/post', 'Im good, thanks! How are you and the kids?2')

hash_of_content = hashlib.sha256(content.get_as_cbor()).digest()
hash_of_prev = hashlib.sha256(meta.get_as_cbor()).digest()

meta = Meta(public_key, 2, hash_of_prev, SIGN_INFO['ed25519'], [HASH_INFO['sha256'], hash_of_content])

signature = signing_key.sign(meta.get_as_cbor()).signature

event = Event(meta, signature, content).get_as_cbor()


if __name__ == "__main__":
    pcap.write_pcap('lessfulldatabase', list1)
