import json
from lib.event import serialize, EVENT
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
        self.owner = None
        self.version = None
        self.comment = None

        if len(args) > 0:
            self.loadFromFile(args[0])
        else:
            self.blocklist = {
                "owner": None,
                "version": 1.0,
                "comment": "",
                "words": [],
                "authors": []
            }
            self.owner = self.blocklist["owner"]
            self.version = self.blocklist["version"]
            self.comment = self.blocklist["comment"]

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
        try:
            self.owner = self.blocklist["owner"]
            self.version = self.blocklist["version"]
            self.comment = self.blocklist["comment"]
        except:
            pass

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
        else:
            self.blocklist = {
                "owner": feed.fid,
                "version": 1.0,
                "comment": "",
                "words": [],
                "authors": []
            }

    def loadFromEvent(self, event):
        """
        Loads blocklist from given feed.

        Parameters
        ----------
        feed : FEED
            feed that is used to initialise.
        """
        self.blocklist = event.content()[2]
        try:
            self.owner = self.blocklist["owner"]
            self.version = self.blocklist["version"]
            self.comment = self.blocklist["comment"]
        except:
            pass

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

    def isEmpty(self):
        """
        Returns
        -------
        bool
            true if no blocklist data loaded.
        """
        return self.blocklist is None

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
        if word.lower() not in self.blocklist["words"]:
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
        if word.lower() in self.blocklist["words"]:
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
        if authorkey not in self.blocklist["authors"]:
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
        if authorkey in self.blocklist["authors"]:
            self.blocklist["authors"].remove(authorkey)

    def combineBlockListsFromFeed(self, own_feed, share_feed, comment=None):
        """
        Combines two Blocklists from two different feeds.

        Parameters
        ----------
        own_feed : FEED
            The own feed containing a blocklist
        share_feed : FEED
            The feed conataining a blocklist which will be inserted in the other blocklist
        comment : str
            (optional)
            Comment of new blocklist.
            If none is given comment will be combined from both lists.
        """
        e = None
        for event in share_feed:
            if event.content()[0] == "bacnet/blocklist":
                e = event
        if e:
            self.blocklist = self.combineBlockLists(self.blocklist, e.content()[2], comment)
            self.writeToFeed(own_feed)


    @staticmethod
    def combineBlockLists(blocklist1, blocklist2, comment=None):
        """
        Combines two Blocklists.

        Parameters
        ----------
        blocklist1 : Blocklist
            First blocklist.
        blocklist2 : Blocklist
            First blocklist.
        comment : str
            (optional)
            Comment of new blocklist.
            If none is given comment will be combined from both lists.

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

        if comment is None:
            comment1 = blocklist1["comment"]
            comment2 = blocklist2["comment"]

            newBlocklist[
                "comment"] = "This blocklist was combined.\nComment 1:\n" + comment1 + "\nComment 2:\n" + comment2
        else:
            newBlocklist["comment"] = comment

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

    def getBlockedEvents(feed):

    def getSuggestedBlockSeqNum(self, sugblockfeed, feedId):
        seqnumList = []
        e = None
        for event in sugblockfeed:
            if event.content()[0] == "bacnet/blocklist_sugblock":
                e = event
                if feedId in e.content()[2]:
                    seqnumList += e.content()[2][feedId]
        return seqnumList

    def getFilteredContentFromFeed(self, blocklist, blocksettings, feed, feedsugblocklist, seq_num):
        if blocksettings.sugblock == blocksettings.USESUGBLOCK:
            seqnumList = []
            for sugblockfeed in feedsugblocklist:
                seqnumList += self.getSuggestedBlockSeqNum(sugblockfeed, feed.fid)

            if seq_num in seqnumList:
                return ""
        if feed.fid not in blocklist.blocklist["authors"]:
            return self.filterString(blocklist, blocksettings, feed[seq_num].content()[2])
        return ""

    def addBlockSuggestionEvent(feed):


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
                    if blocksettings.blocklevel == Blocksettings.SOFTBLOCK:
                        splitString[i] = len(splitString[i]) * "*"
                        break
                    elif blocksettings.blocklevel == Blocksettings.HARDBLOCK:
                        splitString[i] = ""
                        break
        return ' '.join(splitString)