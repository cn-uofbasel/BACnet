import os

class Dictionary:

    def removeAllUsers(self):
        os.remove('users.txt')
        file = open('users.txt', 'w+')
        file.close()

    # our userdictionary is a dictionary consisting of usernames as keys and dictionaries as values
    # the values are based on the dictionaries returned by logMerge when asked for the current status of feeds
    # this function reads the users.txt file to extract the userdictionary so that we can work with it
    # returns the read userdictionary
    def getUserDictionary(self):
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
    def writeUserDictionary(self, dict):
        self.removeAllUsers()
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

    def update_dict(self, dict):
        pass

        # from the userdictionary we calculate an overarching dictionary of feed_id: seq_no.
        # the keys are the smallest superset containing all feed_ids from all users in our userlog.
        # the values are the smallest seq_no among all users
        # if a user doesn't have the feed its value becomes 0. this means the feed will get exported next time a user that has it uses the drive
        # !!!this is a naive approach and may be subject to change based on how group 14s feed control comes along and how it may be integrated here!!!
        # !!!in essence we create our own feed control where every user using the same drive will get the same feeds!!!
        # returns the aforementioned overarching dictionary
    def getSequenceNumbers(self):
        dict = self.getUserDictionary()
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
