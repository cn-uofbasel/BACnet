import \
    json

class Blocksettings:
    """
    Blocksettings stores settings on how to filter content.
    """
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
        """
        Loads settings from a json file.

        Parameters
        ----------
        path : str
            path of the file
        """
        file = open(path, "r")
        self.settings = json.load(file)

    def writeToFile(self, path):
        """
        Writes settings to a json file.

        Parameters
        ----------
        path : str
            The path where the file is stored.
        """
        outfile = open(path, 'w')
        json.dump(self.settings, outfile)

    def valuesToJson(self):
        """
        Translates setting values to json format.
        """
        self.settings = {}
        self.settings["blocklevel"] = self.blocklevel
        self.settings["sharesetting"] = self.sharesetting

    def jsonToValues(self):
        """
        Translates json values to settings format.
        """
        self.blocklevel = self.settings["blocklevel"]
        self.sharesetting = self.settings["sharesetting"]

    def changeBlockLevel(self, newSetting):
        """
        Changes Blocklevel.

        Parameters
        ----------
        newSetting : int
            New Setting that should be stored.

        Returns
        -------
        bool
            false if setting was already the same.

        """
        if (self.blocklevel == newSetting):
            return False

        self.blocklevel = newSetting
        return True

    def changeShareSetting(self, newSetting):
        """
        Changes Sharesettings.

        Parameters
        ----------
        newSetting : int
            New Setting that should be stored.

        Returns
        -------
        bool
            false if setting was already the same.

        """
        if (self.sharesetting == newSetting):
            return False
        self.sharesetting = newSetting
        return True

    @staticmethod
    def getStandartSettings():
        """
        Constructs a blocksettings object with standart settings.

        Returns
        -------
        Blocksettings
            The blocksettings object.

        """
        bs = Blocksettings()
        bs.blocklevel = Blocksettings.SOFTBLOCK
        bs.sharesetting = Blocksettings.DONTBLOCKSHARED

        return bs

