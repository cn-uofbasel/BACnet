import sys
import os
sys.path.append(os.path.abspath('../../04-logMerge/eventCreationTool'))
import EventCreationTool
from enum import Enum

class Events(Enum):
    MASTER = "MASTER/MASTER" # {}
    Trust = "MASTER/Trust" # {'feed_id": feedID}
    Untrust = "MASTER/Untrust" # {'feed_id', feedID}
    Name = "MASTER/Name" # {'name', name}
    NewFeed = "MASTER/NewFeed" # {'feed_id': feedID, 'app_name': 'TestApp'}
    Block = "MASTER/Block" # {'feed_id': feedID}
    Unblock = "MASTER/Unblock" # {'feed_id': feedID}
    Radius = "MASTER/Radius" # {'radius', radius}


class EventCreationWrapper:

    def __init__(self, eventFactory):
        _eventFactory = eventFactory

    def create_MASTER(self):
        return self._eventFactory.new_event(Events.MASTER, {})

    def create_trust(self, feedID):
        return self._eventFactory.new_event(Events.Trust, {'feed_id': feedID})

    def create_untrust(self, feedID):
        return self._eventFactory.new_event(Events.Untrust, {'feed_id': feedID})

    def create_name(self, name):
        return self._eventFactory.new_event(Events.Name, {'name', name})

    def create_newFeed(self, feedID, appName):
        return self._eventFactory.new_event(Events.NewFeed, {'feed_id': feedID, 'app_name': appName})

    def create_block(self, feedID):
        return self._eventFactory.new_event(Events.Block, {'feed_id': feedID})

    def create_unblock(self, feedID):
        return self._eventFactory.new_event(Events.Unblock, {'feed_id': feedID})

    def create_radius(self, radius):
        return self._eventFactory.new_event(Events.Radius, {'radius', radius})