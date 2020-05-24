import os
from .BACnetstuff import *

#### TODO: MAIN METHOD SHOULD BE IN UI SKELETON AND SAVE THE DICTIONARIES THERE. ANYTHING THAT USES getUsersDictionary()
#### TODO: SHOULD TAKE IT AS A PARAMETER INSTEAD TO AVOID READING THE SAME FILE OVER AND OVER
#### TODO: MAIN METHOD SHOULD CALL getUsersDictionary AND THEN CREATE A USER OBJECT

# this path part is pretty fucked and needs to be revisited
pcapDumpPath = ""
def setPath(str):
    pcapDumpPath = str

# our usersdictionary is a dictionary consisting of usernames as keys and dictionaries as values
# the values are based on the dictionaries returned by logMerge when asked for the current status of feeds

# this function reads the users.txt file to extract the userdictionary so that we can work with it
# returns the read userdictionary
def getUsersDictionary():
    dict = {}
    file = open('users.txt', 'r')
    users = file.read().split('+')
    for user in users:
        name, feedids = user.split(";")
        feedidlist = feedids.split(",")
        dictoffeeds = {}
        for pair in feedidlist:
            fid, seqno = pair.split(":")
            fid = bytes.hex(fid.encode())
            dictoffeeds[fid] = int(seqno)
        dict[name] = dictoffeeds
    file.close()
    return dict

# this function writes the userdictionary to the user.txt file
# no return
# TODO: do we have to remove all users every time?
def writeUsersDictionary(dict):
    removeAllUsers()
    file = open('users.txt', 'w')
    first = True
    try:
        for name, feeds in dict.items():
            user = ""
            user = "" + name + ";"
            firstfeed = True
            for feed, seqno in feeds.items():
                if first:
                    if firstfeed:
                        feed = bytes.fromhex(feed)
                        user = user+feed.decode()+":"+str(seqno)
                        firstfeed=False
                    else:
                        feed = bytes.fromhex(feed)
                        user = user+","+feed.decode()+":"+str(seqno)
                else:
                    if firstfeed:
                        feed = bytes.fromhex(feed)
                        user = user + feed.decode() + ":" + str(seqno)
                        firstfeed = False
                    else:
                        feed = bytes.fromhex(feed)
                        user = user + "," + feed.decode() + ":" + str(seqno)
            if first:
                user=user+"+"
                first = False
            file.write(user)
    except KeyError:
        print("keyerror?")

# empties the user.txt file
# no return
def removeAllUsers():
    os.remove('users.txt')
    file = open('users.txt', 'w+')
    file.close()

# removes one specified user identified by their username from the user.txt file
# takes username, no return
# TODO: save the dictionary once on starting the program
def removeOneUser(username):
    dictionary = getUsersDictionary()
    if username in dictionary:
        print("Deleted ", username)
        del dictionary[username]
    else:
        print(username, " not found.")
    writeUsersDictionary(dictionary)

# add a new user to our userdictionary.
# this function should call getCurrentUserDictionary() and writeUserDictionary()
# takes the username of the new user and returns nothing
# dict = {name1:dict_1,name2:dict2} where dict_1 = {feedID_1:seqNo_1}
# TODO: Create a feed, .key file and add the user to the dictionary.. how to add them to BACNet?
def newUser(name):
    #h = HMAC()
    #h.create()
    # after creating a new key and feed, set all SeqNo in dictionary to 0
    pass

# this function returns a dictionary containing information about what events are stored on the device. key is feed id, value is tuple marking from which to which seq_no is stored
# TODO: implement and call where needed (should be only when exporting)
def getStickStatus():
    pass

# class to represent the user that is currently using the software
class User:
    # username is given from the ui
    # usersdictionary is saved between running the program and called via getUsersDictionary
    # currentuserdictionary contains feed_id's as key and latest seq_no's as corresponding values
    def __init__(self, name):
        self.username = name
        self.usersDictionary = getUsersDictionary()
        #TODO: check if the user is new
        if name in self.usersDictionary:
            pass
        else:
            pass
        self.currentUserDictionary = self.getCurrentUserDictionary()

    # this calls the as of now unimplemented function provided by group 4
    # returns a dictionary of feed_id: seq_no for the current user
    # TODO: insert group 4's method
    def getCurrentUserDictionary(self):
        pass

    # This method imports events from the folder on the drive that holds the pcap files created by the export function.
    # returns nothing
    # TODO: update sequencenumbers after import -> call getCurrentUserDictionary, apply changes, call writeUserDictionary, update pcap to delete old events
    def importing(self):
        if pcapDumpPath != "":
            logMerge.import_logs(pcapDumpPath)
        else:
            print("insert setPath() method properly here")
            pass
        new_dict = getUsersDictionary()

        # does this happen here or in exporting()? i forgot. happens here
        self.update_pcap(new_dict)

    # this method calls the export_logs() function provided by group 4.
    # takes an int specifying the maximum number of events dumped per feed
    # returns nothing
    # TODO: update it to the newest version we were forced to do in a short time lolwut?
    def exporting(self, maxEvents):
        logMerge.export_logs(pcapDumpPath, getStickStatus(), maxEvents)

    # TODO: implement as follows:
    # read every feed and save its sequence number in a dictionary of {feedID:seqNo}
    # then compare it to our sequence numbers getSequenceNumbers() which is also {feedID:seqNo}
    # delete any event that has a lower seqNo than our getSequenceNumbers() returns
    # returns nothing
    def update_pcap(self, dictionary):
        pass
