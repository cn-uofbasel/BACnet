import json
from lib.event import serialize
from lib.feed import FEED
from blocksettings import Blocksettings
import time


class Blocklist:
    """
    Instance of a blocklist.
    Implements functions to load, change, and save a blocklist.
    """

    def __init__(self, *args):
        """
        Constructor of Blocklist.

        Parameters
        ----------
        path : string
            path of json file that is used to initialise.
        """
        self.blocklist = None

        if len(args) > 0:
            self.loadFromFile(args[0])
        else:
            self.blocklist = {
                "words": [],
                "authors": []
            }

    def getBlockedWords(self):
        """
        Returns
        -------
        [string]
            The list of all blocked words.
        """
        return self.blocklist["words"]

    def getBlockedAuthors(self):
        """
       Returns
       -------
       [string]
           The list of public keys of blocked authors.
       """
        return self.blocklist["authors"]

    def loadFromFile(self, path):
        """
        Loads blocklist from json file.

        Parameters
        ----------
        path : string
            path of json file that is used to initialise.
        """
        file = open(path, "r")
        self.blocklist = json.load(file)

    def loadFromFeed(self, feed):
        """
        Loads blocklist from given feed.

        Parameters
        ----------
        feed : FEED
            feed that is used to initialise.
        """
        e = None
        for event in feed:
            if event.content()[0] == "bacnet/blocklist":
                e = event
        if e:
            self.loadFromEvent(e)

    def loadFromEvent(self, event):
        """
        Loads blocklist from given feed.

        Parameters
        ----------
        feed : FEED
            feed that is used to initialise.
        """
        self.blocklist = event.content()[2]

    def writeToFile(self, path):
        """
        Writes blocklist to json file.

        Parameters
        ----------
        path : string
            path where json file should be stored.
        """
        outfile = open(path, 'w')
        json.dump(self.blocklist, outfile)

    def writeToFeed(self, feed):
        """
        Writes blocklist to feed.

        Parameters
        ----------
        feed : FEED
            feed where the blocklist should be stored.
        """
        feed.write(["bacnet/blocklist", time.time(), self.blocklist])

    def loadFromString(self, s):
        """
        Loads a blocklist from a string.

        Parameters
        ----------
        s : string
            The string.
        """
        self.blocklist = json.load(s)

    def getBlocklist(self):
        """
        Returns
        -------
        jsondata
            The blocklist saved by this instance.
        """
        return self.blocklist

    def blockWord(self, word):
        """
        Adds a word to the blocklist if word is not already in list.

        Parameters
        ----------
        word : string
            The word that should be blocked.
             Returns
        -------
        bool
            true if a change to the list was made.
        """
        if word.lower() not in self.getBlockedWords():
            self.blocklist["words"].append(word.lower())
            return True
        return False

    def unblockWord(self, word):
        """
        Removes a word from the blocklist if word is in list.

        Parameters
        ----------
        word : string
              The word that should be unblocked.
        -------
        bool
            true if a change to the list was made.
        """
        if word.lower() in self.getBlockedWords():
            self.blocklist["words"].remove(word.lower())
            return True
        return False

    def blockAuthor(self, authorkey):
        """
        Adds an authorkey to the blocklist if author is not in list.

        Parameters
        ----------
        authorkey : string
              The author's publickey as a string that should be added to list.
        -------
        bool
            true if a change to the list was made.
        """
        if authorkey not in self.getBlockedAuthors():
            self.blocklist["authors"].append(authorkey)
            return True
        return False

    def unblockAuthor(self, authorkey):
        """
        Removes an authorkey from the blocklist if author is in list.

        Parameters
        ----------
        authorkey : string
              The author's publickey as a string that should be removed from the list.
        -------
        bool
            true if a change to the list was made.
        """
        if authorkey in self.getBlockedAuthors():
            self.blocklist["authors"].remove(authorkey)

    def combineBlockListsFromFeed(self, own_feed, share_feed):
        """
        Combines two Blocklists from two different feeds.

        Parameters
        ----------
        own_feed : FEED
            The own feed containing a blocklist
        share_feed : FEED
            The feed conataining a blocklist which will be inserted in the other blocklist
        """
        e = None
        for event in share_feed:
            if event.content()[0] == "bacnet/blocklist":
                e = event
        if e:
            self.blocklist = self.combineBlockLists(self.blocklist, e.content()[2])
            self.writeToFeed(own_feed)

    @staticmethod
    def combineBlockLists(blocklist1, blocklist2):
        """
        Combines two Blocklists.

        Parameters
        ----------
        blocklist1 : Blocklist
            First blocklist.
        blocklist2 : Blocklist
            First blocklist.

        Returns
        -------
        Blocklist
            The new blocklist that combines both lists.

        """
        newBlocklist = blocklist1
        for w in blocklist2["words"]:
            if w not in newBlocklist["words"]:
                newBlocklist["words"].append(w)

        for a in blocklist2["authors"]:
            if a not in newBlocklist["authors"]:
                newBlocklist["authors"].append(a)

        return newBlocklist

    # TODO filter methods could be in own class
    @staticmethod
    def filterFeed(blocklist, blocksettings, feed):
        """
        Applies filters to the content of all events, that are included in the given feed,
        according to the given blocksettings.

        Parameters
        ----------
        blocklist : Blocklist
            The blocklist that is used to filter the event.
        blocksettings : Blocksettings
            The settings that are applied to filter the event.
        feed : FEED
            The feed that get's filtered.

        Returns
        -------
        FEED
            The filtered feed.
        """
        if blocksettings.blocklevel == blocksettings.NOBLOCK:
            return feed
        feed = list(feed)
        for i in range(len(feed)):
            feed[i] = blocklist.filterEvent(blocklist, blocksettings, feed[i])
        return feed

    def getBlockedEvents(self, feed):
        """
        Iterates over all events of the given feed and stores its seq_no if the content of the event includes a blocked word.
        If the author of the feed is on the blocklist, the sequence numbers of all events are stored.

        Parameters
        ----------
        feed : FEED
            The feed that contains the events.

        Returns
        -------
        [int]
            List of all sequence numbers of events that are blocked.
        """
        if feed.fid in self.getBlockedAuthors():
            return list(range(0, len(feed)))

        seqNumList = []

        for event in feed:
            if "bacnet/blocklist" not in event.content()[0] or "bacnet/blocksettings" not in event.content()[0]:
                if str(event.content()[2]).lower() in self.getBlockedWords():
                    seqNumList.append(event.seq - 1)

        return seqNumList

    @staticmethod
    def getSuggestedBlockSeqNum(suggblockfeed, feedId):
        """
        Iterates over all events in the given feed and returns the sequence number of all events from feed_id which are marked as "suggested block" by the owner
        of suggblockfeed.

        Parameters
        ----------
        suggblockfeed : FEED
            The feed that contains the events.
        feedId:  int
            The id of the feed to which the blocked sequence numbers belong.
        Returns
        -------
        [int]
            List of all sequence numbers of events for which it was recommended to block them
        """
        seqnumList = []
        e = None
        for event in suggblockfeed:
            if event.content()[0] == "bacnet/blocklist_suggblock":
                e = event
        if e:
            if feedId in e.content()[2]:
                seqnumList += e.content()[2][feedId]
            #print(seqnumList)
            return seqnumList
        return []

    @staticmethod
    def getFilteredContentFromFeed(blocklist, blocksettings, feed, feed_suggblock, seq_num):
        """
        Filters the content of the event with the given sequence number  according to the given blocksettings and block suggestions from another feed.

        Parameters
        ----------
        blocklist : Blocklist
            The blocklist that is used to filter the event.
        blocksettings : Blocksettings
            The settings that are applied to filter the event.
        feed : FEED
            The feed that contains the events.
        feed_suggblock:
            (optional)
            The feed that should be used to get block suggestions
        seq_num : int
            The sequence number of the feed
        Returns
        -------
        string
            Filtered Content
        """
        newFeed = list(feed)
        if "bacnet/blocklist" in newFeed[seq_num].content()[0] or "bacnet/blocksettings" in newFeed[seq_num].content()[0]:
            return newFeed[seq_num][2]
        if feed_suggblock and blocksettings.getSuggBlock() == blocksettings.USESUGGBLOCK:
            seqnumList = Blocklist.getSuggestedBlockSeqNum(feed_suggblock, feed.fid)

            if seq_num in seqnumList:
                return ""
        if feed.fid not in blocklist.getBlockedAuthors():
            return Blocklist.filterString(blocklist, blocksettings, newFeed[seq_num].content()[2])
        return ""

    @staticmethod
    def getFilteredFeed(blocklist, blocksettings, feed, feed_suggblock = None):
        """
        Filters the content all events of the given feed according to the given blocksettings and block suggestions from another feed.
        The returned list should only be used to display the contents and should not be used for any other purpose, otherwise the Scuttlebutt protocol will be violated.


        Parameters
        ----------
        blocklist : Blocklist
            The blocklist that is used to filter the event.
        blocksettings : Blocksettings
            The settings that are applied to filter the event.
        feed : FEED
            The feed that get's filtered.
        feed_suggblock:
            (optional)
            The feed that should be used to get block suggestions
        Returns
        -------
        [EVENT]
            List of filtered events of the given feed. This list should only be used to display the contents and should not be used for any other purpose, otherwise the Scuttlebutt protocol will be violated.
        """
        newFeed = list(feed)
        for i in range(len(feed)):
            newContent = newFeed[i].content()
            newContent[2] = Blocklist.getFilteredContentFromFeed(blocklist, blocksettings, feed, feed_suggblock, i)
            #print(i)
            newFeed[i].contbits = serialize(newContent)
        return newFeed

    def addBlockSuggestionEvent(self, feed, feed_id, seqNumList):
        """
        Updates the suggested Block entries for the given feed_id with the given sequence number list and writes it to the given feed.


        Parameters
        ----------
        feed : FEED
            The feed where the suggested Block entries should be updated
        feed_id : int
            The feed id to which the sequence numbers belong
        seqNumList : [int]
            the sequence numbers to be added to the list
        """
        e = None
        for event in feed:
            if event.content()[0] == "bacnet/blocklist_suggblock":
                e = event

        suggDict = {feed_id: []}
        if e:
            suggDict = e.content()[2]
        newSeqNum = []
        for seqNum in seqNumList:
            if seqNum not in suggDict[feed_id]:
                newSeqNum.append(seqNum)
        suggDict[feed_id] = suggDict[feed_id] + newSeqNum
        print(suggDict)
        feed.write(["bacnet/blocklist_suggblock", time.time(), suggDict])

    # Example
    @staticmethod
    def filterString(blocklist, blocksettings, s):
        """
        Applies filter to a string.

        Parameters
        ----------
        blocklist : Blocklist
            The blocklist that is used to filter the string.
        blocksettings : Blocksettings
            The settings that are applied to filter the string.
        s : str
            The string that get's filtered.

        Returns
        -------
        str
            The filtered string.
        """
        splitString = str(s).split()

        for i in range(len(splitString)):
            for b in blocklist.blocklist["words"]:
                if b.lower() in splitString[i].lower():
                    if blocksettings.getBlocklevel() == Blocksettings.SOFTBLOCK:
                        splitString[i] = len(splitString[i]) * "*"
                        break
                    elif blocksettings.getBlocklevel() == Blocksettings.HARDBLOCK:
                        splitString[i] = ""
                        break
        return ' '.join(splitString)
