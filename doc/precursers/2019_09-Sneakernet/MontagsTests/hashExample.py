import nacl.hash
import nacl.encoding
from nacl.public import PrivateKey

message = 'Hallo, ich mag Kuchen.'
message2 = 'Kuchen.'

hash_function = nacl.hash.sha256
hash_function2 = nacl.hash.sha512

output = hash_function(message.encode(), nacl.encoding.HexEncoder)
output2 = hash_function2(message.encode(), nacl.encoding.HexEncoder)

print(output)
print(output2)
