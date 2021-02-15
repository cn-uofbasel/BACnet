#ratChat

ratChat is an application intended to extend BACnet. It allows two parties (Bob and Alice) have Signal-like secure chats that follow the the double ratchet algorithm,
thus guaranteeing forward-secure and backward-secure chats. The current state, the protocol for starting a chat is still quite sensible.

##Features that are currently missing:
- Management of out-of-order messages
- 
- (GUI)

##Installing dependencies ( The code has been tested on Unix[Linux/macOS] )
### Packages required:
- cmake (required for XedDSA)
```
Different for each OS, please consult google.
```
- XedDSA
```
pip install xeddsa
```
- pycrypto
```
pip3 install cryptography==2.8 pycrypto
```

#Usage
