# BACnet Event Structure

```
event data structure (="log entry")

  +-event------------------------------------------------------------------+
  | +-meta---------------------------------------+                         |
  | | feed_id, seq_no, h_prev, sign_info, h_cont |, signature, opt_content |
  | +--------------------------------------------+                         |
  +------------------------------------------------------------------------+

  event :== cbor( [ meta, signature, opt_content ] )

  meta  :== cbor( [ feed_id, seq_no, h_prev, sign_info, h_cont ] )

  h_prev         :== [hash_info, "hash value of prev event's meta field"]
  signature      :== "signature of meta"
  h_cont         :== [hash_info, "hash value of opt_content"]

  sign_info:     enum (0=ed25519)
  hash_info:     enum (0=sha256)

  opt_content    :== cbor( data )  # must be bytes so we can compute a hash)
  
```

# The use of CBOR

CBOR (see RFC 7049) is a serialization format for structured data
types. In Python, serializing is achieved via the ```dumps``` method,
and deserialization with ```loads```:

```python
import cbor2

pkt = cbor2.dumps([123,'and a string'])
print( cbor2.loads(pkt) )
```

---
