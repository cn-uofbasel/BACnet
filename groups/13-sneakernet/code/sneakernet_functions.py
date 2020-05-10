import os
from .logMerge import LogMerge

# TODO: arguments to call functions reliably from gui
# TODO: startup method. make this a class?

# logmerge is currently still a class. we need an object to access its functions
logM = LogMerge()
# this here is the path of the directory that holds the events that are stored on the drive for distribution.
# This should be a relative path that does not change neither during runtime and ideally nor during use
pcapDumpPath = ""

# This method imports events from the folder on the drive that holds the pcap files created by the export function.
# returns nothing
# TODO: update sequencenumber list after successful import -> call getCurrentUserDictionary, overwrite programs held entry and call writeUserDictionary
def importing():
    logM.import_logs(pcapDumpPath)

# this method calls the export_logs() function provided by group 4.
# takes an int specifying the maximum number of events dumped per feed
# returns nothing
# TODO: empty folder at pcapDumpPath before export to avoid duplicate events on drive !!!ONLY WORKS IF IMPORTED BEFORE EXPORTING!!! maybe hardcode an import
def exporting(maxEvents):
    logM.export_logs(pcapDumpPath, getSequenceNumbers(), maxEvents)

# this function updates the pcapDumpPath
def getPath():
    ### TO DO ### insert automatic path logic
    pass

# this calls the as of now unimplemented function provided by group 4
# returns a dictionary of feed_id: seq_no for the current user
def getCurrentUserDictionary():
   pass
   #TO DO

# determines the maximum amount of extractable events. use get current and get abs of it with getsequencenumbers
# returns an integer
# TODO: implement
def maxNumberofEvents():
    pass

# from the userdictionary we calculate an overarching dictionary of feed_id: seq_no.
#the keys are the smallest superset containing all feed_ids from all users in our userlog.
# the values are the smallest seq_no among all users
# if a user doesn't have the feed its value becomes 0. this means the feed will get exported next time a user that has it uses the drive
# !!!this is a naive approach and may be subject to change based on how group 14s feed control comes along and how it may be integrated here!!!
# !!!in essence we create our own feed control where every user using the same drive will get the same feeds!!!
# returns the aforementioned overarching dictionary
def getSequenceNumbers():
    dict = getUserDictionary()
    dict_ = {}
    for user in dict:
        feeds = dict[user]
        for feed in feeds:
            if feed in dict_:
                if dict_[feed] > feeds[feed]:
                    dict_[feed] = feeds[feed]
            else:
                dict_[feed] = feeds[feed]
    return dict_

# our userdictionary is a dictionary consisting of usernames as keys and dictionaries as values
# the values are based on the dictionaries returned by logMerge when asked for the current status of feeds
# this function reads the users.txt file to extract the userdictionary so that we can work with it
# returns the read userdictionary
def getUserDictionary():
    dict = {}
    file = open('users.txt', 'r')
    users = file.read().split('+')
    for user in users:
        name, feedids = user.split(";")
        feedidlist = feedids.split(",")
        dictoffeeds = {}
        for pair in feedidlist:
            fid, seqno = pair.split(":")
            dictoffeeds[fid] = int(seqno)
        dict[name] = dictoffeeds
    file.close()
    return dict

# this function writes the userdictionary to the user.txt file
# no return
def writeUserDictionary(dict):
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
                        user = user+feed+":"+str(seqno)
                        firstfeed=False
                    else:
                        user = user+","+feed+":"+str(seqno)
                else:
                    if firstfeed:
                        user = user + feed + ":" + str(seqno)
                        firstfeed = False
                    else:
                        user = user + "," + feed + ":" + str(seqno)
            if first:
                user=user+"+"
                first = False
            file.write(user)
    except NotImplementedError:
        print("ups i don't know what error it would throw")

# empties the user.txt file
# no return
def removeAllUsers():
    os.remove('users.txt')
    file = open('users.txt', 'w+')
    file.close()

# removes one specified user identified by their username from the user.txt file
# takes username, no return
def removeOneUser(username):
    dict = getUserDictionary()
    if username in dict:
        del dict[username]
    writeUserDictionary(dict)

# add a new user to our userdictionary.
# this function should call getCurrentUserDictionary() and writeUserDictionary()
# takes the username of the new user and returns nothing
# dict = name1,dict_1;name2,dict2
def newUser(name):
    try:
        file = open('users.txt', 'a')
        check = open('users.txt', 'r')
    except FileNotFoundError:
        file = open('users.txt', 'w+')
        check = open('users.txt', 'r')
    users = check.read().split(' ')
    if len(users) > 0:
        file.write(' ' + name)
        file.close()
        check.close()
    else:
        file.write(name)
        file.close()
        check.close()
