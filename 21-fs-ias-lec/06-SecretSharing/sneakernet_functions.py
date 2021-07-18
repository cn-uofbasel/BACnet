import os
import LogMerge

#### TODO: SHOULD TAKE IT AS A PARAMETER INSTEAD TO AVOID READING THE SAME FILE OVER AND OVER
#### TODO: MAIN METHOD SHOULD CALL getUsersDictionary AND THEN CREATE A USER OBJECT

# our usersdictionary is a dictionary consisting of usernames as keys and dictionaries as values
# the values are based on the dictionaries returned by logMerge when asked for the current status of feeds

# this function reads the users.txt file to extract the userdictionary so that we can work with it
# returns the read userdictionary
def getUsersDictionary(path):
    dict = {}
    if not os.path.exists(path + '/users.txt'):
        open(path + '/users.txt', 'w')
    file = open(path + '/users.txt', 'r')
    users = file.read().split('+')
    try:
        for user in users:
            feedids = user.split(";")
            dictoffeeds = {}
            for feedid in feedids[1].split(","):
                fid_seqNo = feedid.split(":")
                fid = bytes.fromhex(fid_seqNo[0])
                dictoffeeds[fid] = int(fid_seqNo[1])
            dict[feedids[0]] = dictoffeeds
    except:
        file.close()
        return {}
    file.close()
    return dict

# this function writes the userdictionary to the user.txt file
# naive implementation always deleting all users before dumping the dictionary again
# no return
def writeUsersDictionary(dict, path):
    removeAllUsers(path)
    if not os.path.exists(path + '/users.txt'):
        open(path + '/users.txt', 'w')
    file = open(path + '/users.txt', 'a')
    first = True
    try:
        for name, feed in dict.items():
            user = "" + name + ";"
            firstfeed = True
            for feedID, seqno in feed.items():
                if first:
                    if firstfeed:
                        feedID = feedID.hex()
                        user = user+feedID+":"+str(seqno)
                        firstfeed=False
                    else:
                        feedID = feedID.hex()
                        user = user+","+feedID+":"+str(seqno)
                else:
                    if firstfeed:
                        feedID = feedID.hex()
                        user = user + feedID + ":" + str(seqno)
                        firstfeed = False
                    else:
                        feedID = feedID.hex()
                        user = user + "," + feedID + ":" + str(seqno)
            if not first:
                user="+" + user
            first = False
            file.write(user)
    except KeyError:
        print("keyerror?")

# empties the user.txt file
# no return
def removeAllUsers(path):
    os.remove(path+'/users.txt')
    file = open(path+'/users.txt', 'w+')
    file.close()

def removeAllPCAP(path):
    for file in os.listdir(path):
        try:
            if file.endswith('.pcap'):
                os.remove(file)
        except OSError as e:
            pass

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

# this function returns a dictionary containing information about what events are stored on the device. key is feed id, value is tuple marking from which to which seq_no is stored
# TODO: implement and call where needed (should be only when exporting)
def getStickStatus():
    pass

# class to represent the user that is currently using the software
class User:
    # username is given from the ui
    # usersdictionary is saved between running the program and called via getUsersDictionary
    # currentuserdictionary contains feed_id's as key and latest seq_no's as corresponding values
    def __init__(self, name, path):
        self.log = LogMerge.LogMerge()
        self.username = name
        self.pcapDumpPath = path
        self.usersDictionary = getUsersDictionary(path)
        self.readDict()


    def readDict(self):
        self.currentUserDictionary = {}
        for user, dict in self.usersDictionary.items():
            for feed_id, seq_no in dict.items():
                self.currentUserDictionary[feed_id] = -1
        self.updateUsersDictionary()

    # this calls the function provided by group 4
    # returns a dictionary of feed_id: seq_no for the current user
    def updateUsersDictionary(self):
        currentUserStatus = self.log.get_database_status()
        for feed_id, seq_no in currentUserStatus.items():
            self.currentUserDictionary[feed_id] = seq_no
        self.usersDictionary[self.username] = self.currentUserDictionary
        for user, dict in self.usersDictionary.items():
            if user != self.username:
                for feed_id, seq_no in currentUserStatus.items():
                    if feed_id not in dict:
                        dict[feed_id] = -1
        writeUsersDictionary(self.usersDictionary, self.pcapDumpPath)

    def getSequenceNumbers(self):
        dict = self.usersDictionary
        dict_ = {}
        for user in dict:
            feeds = dict[user]
            for feed in feeds:
                try:
                    if feed in dict_:
                        if dict_[feed] > feeds[feed]:
                            dict_[feed] = feeds[feed]
                    else:
                            dict_[feed] = feeds[feed]
                except KeyError:
                    dict_[feed] = 0
        return dict_

    # This method imports events from the folder on the drive that holds the pcap files created by the export function.
    # returns nothing
    def importing(self):
        self.log.import_logs(self.pcapDumpPath)
        self.updateUsersDictionary()

    # this method calls the export_logs() function provided by group 4.
    # takes an int specifying the maximum number of events dumped per feed
    # returns nothing
    def exporting(self, maxEvents=30):
        self.importing()
        removeAllPCAP(self.pcapDumpPath)
        self.log.export_logs(self.pcapDumpPath, self.getSequenceNumbers(), maxEvents)


    # TODO: implement as follows:
    # read every feed and save its sequence number in a dictionary of {feedID:seqNo}
    # then compare it to our sequence numbers getSequenceNumbers() which is also {feedID:seqNo}
    # delete any event that has a lower seqNo than our getSequenceNumbers() returns
    # returns nothing
    def update_dict(self, dictionary):
        pass
