import \
    json

class Blocksettings:
    NOBLOCK = 0
    SOFTBLOCK = 1
    HARDBLOCK = 2

    BLOCKSHARED = 3
    DONTBLOCKSHARED = 4

    def __init__(self, *args):
        self.settings = None
        self.blocklevel = None
        self.sharesetting = None

        if len(args) > 0:
            self.loadFromFile(args[0])

    def loadFromFile(self, path):
        file = open(path, "r")
        self.settings = json.load(file)

    def writeToFile(self, path):
        outfile = open(path, 'w')
        json.dump(self.settings, outfile)

    def valuesToJson(self):
        self.settings = {}
        self.settings["blocklevel"] = self.blocklevel
        self.settings["sharesetting"] = self.sharesetting

    def jsonToValues(self):
        self.blocklevel = self.settings["blocklevel"]
        self.sharesetting = self.settings["sharesetting"]

    def changeBlockLevel(self, newSetting):
        self.blocklevel = newSetting

    def changeShareSetting(self, newSetting):
        self.sharesetting = newSetting

    @staticmethod
    def getStandartSettings():
        bs = Blocksettings()
        bs.blocklevel = Blocksettings.SOFTBLOCK
        bs.sharesetting = Blocksettings.DONTBLOCKSHARED

        return bs

