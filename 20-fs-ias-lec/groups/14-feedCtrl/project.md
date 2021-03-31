# Feed Controller

Our Project will be made in two parts. 
- A feedcontroller which will handle the feed, including following and the whitelist check and the possibility to create your own follow- and whitelist. 
- An application with which one can manage a follow- and whitelists.

We agreed to write this project in Python.

## Handler

The feedcontroller does automatically handle given packets.

The follow list and the whitelist can be activated and deactivated. The standard value will be false (deactivated). 
If the follow list and whitelist are deactivated the handler object will always return true.

Using the handler class you will have access to the following features:

```python

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
#a radius of 0 will make is_followed always return false
#a radius of 1 means is_followed will only return true if followed directly
#a radius >1 means is_followed will return true, as long as a given LogID is inside the radius
def set_radius(radius):

#checks if a LogID is followed
#returns 0 on success and -1 on error
def is_followed(LodID):

#checks if a LogID is whitelisted
#returns 0 on success and -1 on error
def is_whitelisted(LogID):

#checks if a LogID is inside the radius
#returns 0 on success and -1 on error
def in_radius(LogID):

#returns an array of LogIDs collected within a set radius
def get_radius_list():
```

### Radius

```Python
#set the social radius
def set_radius(int radius):
```

The radius defines how far the logs will be received. 
If the radius = 2 you'll receive all logs from the logs you are following plus the logs they are following (friends of friends). 

For example: If you're writing a chat application and set the radius to 1, you will only receive the messages from the users you are actively following but you won't receive the logs from the ones you are not following. By increasing the readius you will also be able to receive the message in a bigger radius. 

On runtime the FeedController will include a list of LogID's with the given Radius. This list will be create via reading the Log Database and filltering for the given tag.



### Receiving

This is an example of how to use the FeedController in an application for received packets.

```Python
#Input from network
#Check if followed
if fc.is_followed(LogID) or fc.in_radius(LogID):
    logDB.write(Log)
else:
    return
```

### Sending

This is an example of how to use the FeedController in an application for sending packets.

```Python
#check if whitelist = true
if fc.whitelist.state:
    #check if on whitelist
    if fc.is_whitelisted(logID):
        send(packet)
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
