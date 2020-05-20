import sys
import os
sys.path.append(os.path.abspath('../../04-logMerge/eventCreationTool'))
import EventCreationTool
from enum import Enum

class Events(Enum):
    MASTER = "MASTER/MASTER"
    Trust = "MASTER/Trust"
    Untrust = "MASTER/Untrust"
    Name = "MASTER/Name"
    NewFeed = "MASTER/NewFeed"
    Block = "MASTER/Block"
    Unblock = "MASTER/Unblock"
    Radius = "MASTER/Radius"


class EventCreationWrapper:

    def __init__(self, eventFactory):
        _eventFactory = eventFactory

    def create_MASTER(self):
        return self._eventFactory.new_event(Events.MASTER)

    def create_trust(self, feedID):
        return self._eventFactory.new_event(Events.Trust, feedID)

    def create_untrust(self, feedID):
        return self._eventFactory.new_event(Events.Untrust, feedID)

    def create_name(self, name):
        return self._eventFactory.new_event(Events.Name, name)

    def create_newFeed(self, feedID):
        return self._eventFactory.new_event(Events.NewFeed, feedID)

    def create_block(self, feedID):
        return self._eventFactory.new_event(Events.Block, feedID)

    def create_unblock(self, feedID):
        return self._eventFactory.new_event(Events.Unblock, feedID)

    def create_radius(self, radius):
        return self._eventFactory.new_event(Events.Radius, radius)