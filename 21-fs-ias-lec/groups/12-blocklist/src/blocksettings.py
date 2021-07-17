import json
import time

class Blocksettings:
    """
    Blocksettings stores settings on how to filter content.
    """
    # Blocklevels
    NOBLOCK = 0  # No filters are applied
    SOFTBLOCK = 1  # Blocked words are censored, content of blocked authors are deleted
    HARDBLOCK = 2  # Content that contains blocked words or authors will be deleted

    # Sharesettings
    DONTBLOCKSHARED = 3
    BLOCKSHARED = 4

    USESUGBLOCK = 5 # uses the sugblock for content
    DONTUSESUGBLOCK = 6

    def __init__(self, *args):
        self.settings = None
        self.sugblock = None
        self.blocklevel = None
        self.sharesetting = None

        if len(args) > 0:
            self.loadFromFile(args[0])
        else:
            self.blocklevel = Blocksettings.SOFTBLOCK
            self.sharesetting = Blocksettings.DONTBLOCKSHARED
            self.valuesToJson()

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
        self.jsonToValues()

    def loadFromFeed(self, feed):
        """
        Loads settings from given feed.
        If there are no settings included in the feed, default settings are loaded.

        Parameters
        ----------
        feed : FEED
            The feed where the settings are stored
        """
        e = None
        for event in feed:
            if event.content()[0] == "bacnet/blocksettings":
                e = event
        if e:
            self.settings = e.content()[2]
            self.valuesToJson()

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

    def writeToFeed(self, feed):
        """
        Writes settings to given feed.

        Parameters
        ----------
        feed : FEED
            The feed where the settings should be saved.
        """
        feed.write(["bacnet/blocksettings", time.time(), self.settings])

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
        bs.valuesToJson()

        return bs

