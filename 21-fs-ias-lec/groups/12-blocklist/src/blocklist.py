import sys

sys.path.append("./lib")
import json
import lib.feed as feed
import lib.event as event
from lib.event import serialize
from blocksettings import Blocksettings


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

    # TODO
    def loadFromEvent(self, event):
        self.blocklist = json.loads(event.content()[1])
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

    # TODO
    def writeToEvent(self, feed):
        # feed.write(["bacnet/blocklist", blocklist])
        return feed

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
        if word not in self.blocklist["words"]:
            self.blocklist["words"].append(word)
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
        if word in self.blocklist["words"]:
            self.blocklist["words"].remove(word)
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
                newBlocklist.blockWord(w)

        for a in blocklist2["authors"]:
            if a not in newBlocklist["authors"]:
                newBlocklist.blockAuthor(a)

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
        if blocksettings.blocklevel == blocksettings.NOBLOCK:
            return feed
        for event in feed:
            event = blocklist.filterEvent(blocklist, blocksettings, event)
        filteredfeed = None
        return filteredfeed

    @staticmethod
    def filterEvent(blocklist, blocksettings, event):
        """
                Applies filters to the content of the given event according to the given blocksettings.

                Parameters
                ----------
                blocklist : Blocklist
                    The blocklist that is used to filter the event.
                blocksettings : Blocksettings
                    The settings that are applied to filter the event.
                event : EVENT
                    The event that get's filtered.

                Returns
                -------
                EVENT
                    The filtered Event.
                """
        blockLevel = blocksettings.blocklevel
        if blockLevel == blocksettings.NOBLOCK:
            return event
        elif blockLevel == blocksettings.SOFTBLOCK or blockLevel == blocksettings.HARDBLOCK:
            newContent = []
            if event.fid in blocklist.blocklist["authors"]:  # if author of event is in blocklist
                event.contbits = serialize(["" for c in event.content()])
                return event
            for content in event.content():
                newContent.append(content)
                content = str(content)
                for blockedWord in blocklist.blocklist["words"]:
                    if blockedWord in content:
                        if blockLevel == blocksettings.SOFTBLOCK:  # blocked word get censored
                            censored = blocklist.filterString(blocklist, blocksettings, content)
                            newContent[-1] = censored
                            break
                        elif blockLevel == blocksettings.HARDBLOCK:  # whole content gets deleted
                            event.contbits = serialize(["" for c in event.content()])
                            return event

            event.contbits = serialize(newContent)
        return event

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
                if b in splitString[i]:
                    if blocksettings.blocklevel == Blocksettings.SOFTBLOCK:
                        splitString[i] = len(splitString[i]) * "*"
                        break
                    elif blocksettings.blocklevel == Blocksettings.HARDBLOCK:
                        splitString[i] = ""
                        break
        return ' '.join(splitString)