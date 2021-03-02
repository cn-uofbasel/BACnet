
# Secure Chat

Secure Chat is an application intended to extend BACnet. It allows two parties to have a Signal-like secure chat that follows the the double ratchet algorithm,
thus guaranteeing Perfect Forward Secrecy and Backward Security. The protocol for starting a chat is quite sensitive.

## Limitations
- Only one conversation at a time is permitted. Delete old conversation (as described below at "Resetting") before starting a new conversation.
- Old messages can not be seen, only new ones.
- For chat\_over\_rsync.py, both sides have to have another way of communicating in order to guarantee the correct sequence in the protocol.

## Installing dependencies ( The code has been tested on Unix[Linux/macOS] )
### Packages required:
- cmake (required for XedDSA)
```
Different for each OS, please consult google.
```
- XedDSA
```
pip3 install xeddsa
```
- pycrypto
```
pip3 install cryptography==2.8 pycrypto
```

# Usage
## 1. Chat over TCP
Navigate to the _src_ folder.  
1. Bob starts TCP chat:  
```python3 TCP_chat.py localhost 1234```  
Then an ip address and port will be shown, for example:  
server started with: ip 192.168.1.106 port 62953  
2. Alice starts TCP chat:  
```python3 TCP_chat.py 192.168.1.106 62953```  
3. Alice writes and sends an initial message

Both parties are now free to go and can communicate freely and securely over TCP. To ensure that there is no man in the middle, they can compare their shared secret offline. This shared key is shown the first time they establish contact.


## 2. Chat over BACnet with USB stick
Navigate to the _src_ folder.
1. Bob starts chat:  
```python3 BACnet_local_chat.py Bob```
Then a file "cborDatabase.sqlite" will be generated. Share it with Alice (via USB for example).  
2. Alice starts chat:  
```python3 BACnet_local_chat.py Alice```  
3. Alice writes at least one message.   
4. Alice writes "quit" to close the program.  
5. Transfer the file cborDatabase.sqlite back to Bobs directory.  
6. Bob starts chat to write his answer:  
```python3 BACnet_local_chat.py Bob```  
7. Bob writes "quit" to close the program.  

## 3. Chat over BACnet with rsync
Navigate to the _src_ folder.
1. Bob starts chat:  
```python3 chat_over_rsync.py Bob```  
The first time this is run, 2 files will be generated. In "other\_directory.txt" the user should write the absolute path to the log file from the other party. After that, Bob has to rerun the command from above.  
2. Alice starts chat:  
```python3 chat_over_rsync.py Alice```  
The first time this is run, 2 files will be generated. In "other\_directory.txt" the user should write the absolute path to the log file from the other party.  
(In a local setup, the path specified in "my\_directory.txt" of Alice should be copied into "other\_directory.txt" of Bob, and vice versa.)  
After that, Alice has to rerun the command from above.
3. Bob starts the chat again:  
```python3 chat_over_rsync.py Bob```  
4. Both parties can now send and retrieve messages. To retrieve new messages, write "rsync" in the chat. To exit the chat, write "quit" in the chat.

To ensure that there is no man in the middle, they can compare their shared keys offline. The shared key is shown the first time they establish contact.

## Resetting
To delete all conversations, run ```python3 reset.py```.


## Features that are missing:
- A more robust chat-initiation protocol
- Ask user for password every time he starts the program (it is set to "pw" at the moment)
- Reopen a chat (or trying to read a chat) when no new message have arrived. This will currently cause the algorithm to break completely.
- (GUI)
