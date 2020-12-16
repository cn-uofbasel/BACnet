import socket
import sys
#import time
import errno
import select #Gives us OS level socket functionality

"""
To implement for Double Ratchet:
    KDF-Chain
        KDF key for root chain
        KDF key for sending chain
        KDF key for receiving chain
Parts of code from:
https://stackoverflow.com/questions/58192247/how-to-use-non-blocking-sockets
https://pythonprogramming.net/server-chatroom-sockets-tutorial-python-3/
https://pythonprogramming.net/client-chatroom-sockets-tutorial-python-3/
"""

HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8888

clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
hostName = input("Enter the hostname of the active client: ")
clientSocket.connect( (IP,PORT) )
clientSocket.setblocking(False)
encodedHostName = hostName.encode('utf-8')
hostNameHeader = f"{len(encodedHostName):<{HEADER_LENGTH}}".encode('utf-8')
clientSocket.send(hostNameHeader + encodedHostName)
print("Connected to other client")

while True:
    #Sending messages. If no message is entered before 'Enter', we go to the receiving part
    #Currently, this is the only way of being able to receive input without using more specific select() functionality
    outgoingMessage = input( str("Say: ") ).encode('utf-8')
    if outgoingMessage:
        outgoingMessageHeader = f"{len(outgoingMessage):<{HEADER_LENGTH}}".encode('utf-8')
        clientSocket.send(outgoingMessageHeader + outgoingMessage)
    try:
        while True:
            #Receive messages
            usernameHeader = clientSocket.recv(HEADER_LENGTH)
            if not len(usernameHeader):
                print("Connection terminated by other client")
                sys.exit()
            usernameLength = int(usernameHeader.decode('utf-8').strip())
            username = clientSocket.recv(usernameLength).decode('utf-8')
            incomingMessageHeader = clientSocket.recv(HEADER_LENGTH)
            incomingMessageLength = int(incomingMessageHeader.decode('utf-8').strip())
            incomingMessage = clientSocket.recv(incomingMessageLength).decode('utf-8')
            print(f"{username}: {incomingMessage}")
    except IOError as xcpt:
        #These errors are related to select() and input()
        if xcpt.errno != errno.EAGAIN and xcpt.errno != errno.EWOULDBLOCK:
            print(f"Encountered IO error: {str(xcpt)}")
            sys.exit()
        continue
    except OSError as err:
        #These errors are mostly related to the socket() i.e. invalid host or connection
        print(f"Encountered OS error: {str(err)}")
        sys.exit()
        continue
    except Exception as xcpt:
        print(f"Encountered exception: {str(xcpt)}")
        sys.exit()
