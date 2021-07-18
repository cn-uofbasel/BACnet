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

    # Suggested Block Settings
    DONTUSESUGGBLOCK = 5 # uses the suggblock for content
    USESUGGBLOCK = 6

    def __init__(self, *args):
        self.settings = {
            "blocklevel": Blocksettings.NOBLOCK,
            "suggblock": Blocksettings.DONTUSESUGGBLOCK,
        }

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

    def getBlocklevel(self):
        """
        Returns
        -------
        int
           The current blocklevel.
        """
        return self.settings["blocklevel"]

    def getSuggBlock(self):
        """
        Returns
        -------
        int
            The current "Suggestion Block" settings.

        """
        return self.settings["suggblock"]

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
        if (self.getBlocklevel() == newSetting):
            return False

        self.settings["blocklevel"] = newSetting
        return True

    def changeSuggBlockSettings(self, newSetting):
        """
        Changes Suggested Block settings.

        Parameters
        ----------
        newSetting : int
            New Setting that should be stored.

        Returns
        -------
        bool
            false if setting was already the same.

        """
        if (self.getSuggBlock() == newSetting):
            return False
        self.settings["suggblock"] = newSetting
        return True

    def defaultSettings(self):
        self.settings = {
            "blocklevel": Blocksettings.NOBLOCK,
            "suggblock": Blocksettings.DONTUSESUGGBLOCK,
        }



