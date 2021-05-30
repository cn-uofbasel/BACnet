import \
    json

from blocksettings import Blocksettings

class Blocklist:

    def __init__(self, *args):
        self.blocklist = None
        self.owner = None
        self.version = None
        self.comment = None

        if len(args) > 0:
            self.loadFromFile(args[0])

    def loadFromFile(self, path):
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
        outfile = open(path, 'w')
        json.dump(self.blocklist, outfile)

    #TODO
    def writeToEvent(self, feed):
        return feed

    def loadFromString(self, string):
        self.blocklist = json.load(string)

    def getBlocklist(self):
        return self.blocklist

    def isEmpty(self):
        return self.blocklist is None

    def blockWord(self, word):
        if word not in self.blocklist["words"]:
            self.blocklist["words"].append(word)

    def unblockWord(self, word):
        if word in self.blocklist["words"]:
            self.blocklist["words"].remove(word)

    def blockAuthor(self, authorkey):
        if authorkey not in self.blocklist["authors"]:
            self.blocklist["authors"].append(authorkey)

    def unblockAuthor(self, authorkey):
        if authorkey in self.blocklist["authors"]:
            self.blocklist["authors"].remove(authorkey)

    @staticmethod
    def combineBlockLists(blocklist1, blocklist2, comment = None):
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
    def filterString(blocklist, blocksettings, string):
        splitString = string.split(' ')
        for b in blocklist["words"]:
            for i in len(splitString):
                if blocksettings.blocklevel == Blocksettings.SOFTBLOCK:
                    splitString[i] = len(splitString[i]) * "*"
                elif blocksettings.blocklevel == Blocksettings.HARDBLOCK:
                    if splitString[i] == b:
                        return ""
        return splitString.toString()


