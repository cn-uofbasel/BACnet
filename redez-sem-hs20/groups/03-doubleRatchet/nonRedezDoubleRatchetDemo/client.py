import socket
import sys
#import time
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

def receiveMessage(clientSocket):
    try:
        messageHeader = clientSocket.recv(HEADER_LENGTH)
        if not len(messageHeader):
            return(False)
        messageLength = int(messageHeader.decode("utf-8"))
        return({"header":messageHeader, "data": clientSocket.recv(messageLength)})
    except OSError:
        return(False)


HEADER_LENGTH = 10
IP = "127.0.0.1"
PORT = 8888

#Initialization of the server socket, to which the other client connects
serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serverSocket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
hostName = socket.gethostname()
print(f"<Host name: {hostName}>")
serverSocket.bind( (IP, PORT) )

print("<Succefully bound to host and port>")
print("<Waiting for incoming connections>")

serverSocket.listen()
socketsList = [serverSocket]
clients = {}

"""
#connection, address = x.accept()
print(f"{address} has connected to the server")

while 1:
    enteredMessage = input(str("Say: ")).encode()
    try:
        connection.send(enteredMessage)
    except OSError:
        print("Operation could not be completed. OSError occured")
    receivedMessage = connection.recv(1024).decode()
    print(f"Received: {receivedMessage}")
"""


while True:
    readSockets, _, exceptionSockets = select.select(socketsList,[],socketsList)
    for notifiedSocket in readSockets:
        if notifiedSocket == serverSocket:
            clientSocket, clientAddress = serverSocket.accept()
            user = receiveMessage(clientSocket)
            if user is False:
                continue
            socketsList.append(clientSocket)
            clients[clientSocket] = user
            print(f"Accepted new connection from {clientAddress[0]}:{clientAddress[1]} username: {user['data'].decode('utf-8')}")
        else:
            message = receiveMessage(notifiedSocket)
            if message is False:
                print(f"Closed connection from {clients[notifiedSocket]['data'].decode('utf-8')}")
                socketsList.remove(notifiedSocket)
                del clients[notifiedSocket]
                continue
            user = clients[notifiedSocket]
            print(f"Received message from {user['data'].decode('utf-8')}: {message['data'].decode('utf-8')}")

            for clientSocket in clients:
                if clientSocket != notifiedSocket:
                    clientSocket.send(user['header'] + user['data'] + message['header'] + message['data'])

    for notifiedSocket in exceptionSockets:
        socketsList.remove(notifiedSocket)
        del clients[notifiedSocket]
