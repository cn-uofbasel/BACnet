# Feed Controller

Our Project will be made in two parts. 
- A wrapper which will handle the network communication, including following and the whitelist check and the possibility to create your own follow- and whitelist. 
- An application with which one can manage a follow- and whitelist which can be read by other applications.

We agreed to write this project in Python.

## Wrapper

The wrapper does automatically handle given packets. The function headers will be the same as we normaly use, the only difference from using the normal socket class will be, that you'd have to create a wrapper object, which will handle the socket for you. 

The follow list and the whitelist can be activated and deactivated. The standard value will be false (deactivated). 
If the follow list and whitelist are deactivated the wrapper object will behave like a normal socket.

Using the wrapper class you will have access to the following features:

```python
#socket wrapper constructor
#radius checks how big the readius of received log should be
def __init__(self , family, type, proto):

#Creates a new follow list
#returns 0 on success and -1 on error
def create_follow_list(path):

#Loads an existing follow list
#returns 0 on success and -1 on error
def load_follow_list(path):

#creates a new whitlist
#returns 0 on success and -1 on error
def create_whitelist(path):

#load an existing whitelist
#returns 0 on success and -1 on error
def load_whitelist(path):

#activates follow list usage
#returns 0 on success and -1 on error
def activate_follow_list():

#deactivates follow list usage
#returns 0 on success and -1 on error
def deactivate_follow_list():

#activates whitelist usage
#returns 0 on success and -1 on error
def activate_whitelist():

#deactivates whitelist usage
#returns 0 on success and -1 on error
def deactivate_whitelist():

#adds the given LogID to the follow list
#adds an entry to your own log "followed: LogID"
#returns 0 on success and -1 on error
def follow(LogID):

#removes the given LogID from the follow list
#returns 0 on success and -1 on error
def unfollow(LogID):

#adds the given LogID to the whitelist
#returns 0 on success and -1 on error
def add_to_whitelist(LogID):

#removes the given LogID from the whitelist
#returns 0 on success and -1 on error
def remove_from_whitelist(LogID):

#returns an array of the whitelist content
def get_whitelist():

#returns an array of the follow list content
def get_follow_list():

#set the social radius
def set_radius(radius):
```

### Example

This is an example of how a SocketWrapper could be implemented in (This does not include a following nor a whitelist system):

This wrapper class also includes functions for a TCP connection, which we will not need.
```c++
#pragma once

#include <sys/socket.h>
#include <sys/types.h>
#include <unistd.h>
#include <stdexcept>
#include "LinuxException.h"
#include <arpa/inet.h>

/*
	Wrapper class which handles the sockets
	Throws socket specific errors
*/
class SocketWrapper {
	int sockfd = -1; //socket fd, -1 = error
	int sockDomain; //domain type
	struct sockaddr_in con_addr; //describes socket connection address

public:
	SocketWrapper(int domain, int type, int protocol) { //constructor for a socket wrapper object
		sockDomain = domain; 
		sockfd = socket(domain, type, protocol); //IPV4, TCP, protocol = 0 (from man socket page)
		if (sockfd < 0) {
			throw LinuxException("Socket creation failed"); //self explanatory
		}
	}
	SocketWrapper(int domain, int sockfd) noexcept { //construct for ServerMode
		sockDomain = domain;
		this->sockfd = sockfd;
	}
	SocketWrapper(const SocketWrapper& other) = delete; //Deleting duplicates
	~SocketWrapper() { //Deconstructor of SocketWrapper Object
		if (sockfd != -1) {
			close(sockfd); //close socket if -1 (error)
		}
	}

	/*
	moving a SocketWrapper object
	Those next 3 blocks are needed, so I can use the returned object from the SocketWrapper.accept() function. Else it would be destroyed, as soon as we go out of scope
	other = SocketWrapper object to move
	*/
	SocketWrapper(SocketWrapper&& other) noexcept : sockfd(other.sockfd) {
		other.sockfd = -1;
	}

	SocketWrapper& operator=(const SocketWrapper& other) = delete;

	SocketWrapper& operator=(SocketWrapper&& other) noexcept {
		if (sockfd != -1)
			close(sockfd);

		sockfd = other.sockfd;
		other.sockfd = -1;
		return *this;
	}

	void connect(const struct sockaddr* addr, socklen_t len) { //connect with socket
		if (::connect(sockfd, addr, len) < 0) { //try to connect to the given socket fd 
			throw LinuxException("Connection failed");
		}
	}

	void connectWIP(const char* addr, uint16_t port) { //connect with socket to given IP, port
		con_addr.sin_family = sockDomain; //set domain
		con_addr.sin_port = htons(port);  //set port

		if (inet_pton(sockDomain, addr, &con_addr.sin_addr) <= 0) { //"translate" ip addres an add it to den con_addr object
			throw LinuxException("Invalid address");
		}
		connect((struct sockaddr*) & con_addr, sizeof(con_addr)); //call connect function, and try to connect with given IP and Port (located in con_addr object)
	}

	void bind(const struct sockaddr* addr, socklen_t len) { //Bind socket for server mode
		if (::bind(sockfd, addr, len) < 0) { //bind socket, addr includes domain, port & type
			throw LinuxException("Bind failed");
		}
	}

	void listen(int backlog = 1) { //listen for incoming connection requests, backlog = amount of allowed connections on the socket
		if(::listen(sockfd, backlog) < 0) { //listen on specific socket
			throw LinuxException("Listen failed");
		}
	}

	SocketWrapper accept(struct sockaddr* addr, socklen_t* len) { //accept incoming connection request
		int newSockfd = ::accept(sockfd, addr, len); //returns new socket for connection
		if (newSockfd < 0) { 
			throw LinuxException("Accept failed");
		}
		return { sockDomain, newSockfd }; //return new SocketWrapper object with the new Socket fd
	}

	int send(const void* buf, size_t n, int flags) { //send message
		int sendBytes = ::send(sockfd, buf, n, flags); //send message via this.sock, message, message size, flags
		if (sendBytes < 0) {
			throw LinuxException("Send failed");
		}
		return sendBytes; //return int for byte check
	}

	int read(void* buf, size_t nbytes){ //read incoming message
		int readBytes = ::read(sockfd, buf, nbytes); //read message into given buffer
		if (readBytes < 0) {
			throw LinuxException("Read failed");
		}
		return readBytes; //return int for byte chek
	}

	int recvfrom(void* buf, size_t len, int flags, struct sockaddr* src_addr, socklen_t* addrlen) { //receive via udp
		int n = ::recvfrom(sockfd, buf, len, flags, src_addr, addrlen); //receive from ip
		if (n < 0) {
			throw LinuxException("Recvfrom failed");
		}
		return n;//return int for byte check
	}

	int sendto(const void* buf, size_t n, int flags, struct sockaddr* addr, socklen_t addr_len) { //send via udp
		int sendBytes = ::sendto(sockfd, buf, n, flags, addr, addr_len); //send to ip
		if (sendBytes < 0) {
			throw LinuxException("Sendto failed");
		}
		return sendBytes; //return int for byte check
	}

	int getfd() { //sockfd getter
		return sockfd;
	}
};
```



### Radius

```Python
#set the social radius
def set_radius(int radius):
```

The radius defines how far the logs will be received. 
If the radius = 2 you'll receive all logs from the logs you are following plus the logs they are following (friends of friends). 

For example: If you're writing a chat application and set the radius to 1, you will only receive the messages from the users you are actively following but you won't receive the logs from the ones you are not following. By increasing the readius you will also be able to receive the message in a bigger radius. 

On runtime the Socketwrapper will include a list of LogID's with the given Radius. This list will be create via reading the Log Database and filltering for the given tag.



### Receiving

```Python
#Input from network
#Check if followed
if followed or inRadius:
    Save Log into Database
else:
    return
```

### Sending

```Python
#check if whitelist = true
if whiteliste:
    #check if on whitelist
    if onWhitelist:
        send packet
    else:
        return
```

## Application

The provided application can be used to manage follow- and whitelist. There is also the possibility to create a global follow- and whitelist which can be read by mutliple applications but they can not write into it. 

### Following

The application shows a list of received and disgarded Log-Identifiers since the last session. You then can follow or unfollow those Useres. 
The list of followed Users will be saved in a storage file.

### Whitelist

The whitelist work similary to the following function. The difference is, following is vor reading and the whitelist for sending.

The whitelist will only work, if an application uses the given send function from the feed-controller.

## Storage Files

In this section I'll describe the structure of the storage files for the Follow- and Whitelist.

Both files will have the same structure, as they don't differ in content, only in usage.

The files include a list of LogID's.

### Structure

```
LogID1,LogID2,LogID3,...,LogIDn
```

