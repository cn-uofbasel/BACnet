import \
    json

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

    #TODO
    def loadFromEvent(self, event):
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

    #TODO
    def writeToEvent(self, feed):
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
    def combineBlockLists(blocklist1, blocklist2, comment = None):
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

        for a in blocklist2["author"]:
            if a not in newBlocklist["author"]:
                newBlocklist.blockAuthor(a)

        if comment is None:
            comment1 = blocklist1["comment"]
            comment2 = blocklist2["comment"]

            newBlocklist["comment"] = "This blocklist was combined.\nComment 1:\n" + comment1 + "\nComment 2:\n" + comment2
        else:
            newBlocklist["comment"] = comment

        return newBlocklist

    #TODO filter methods could be in own class
    #TODO feed filter
    @staticmethod
    def filterFeed(blocklist, blocksettings, feed):
        filteredfeed = None
        return filteredfeed

    #TODO event filter
    @staticmethod
    def filterEvent(blocklist, blocksettings, event):
        filteredevent = None
        return filteredevent

    #Example
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
        splitString = s.split(' ')
        for b in blocklist["words"]:
            for i in len(splitString):
                if blocksettings.blocklevel == Blocksettings.SOFTBLOCK:
                    splitString[i] = len(splitString[i]) * "*"
                elif blocksettings.blocklevel == Blocksettings.HARDBLOCK:
                    if splitString[i] == b:
                        return ""
        return splitString.toString()
