import sys
import os
sys.path.append(os.path.abspath('../../04-logMerge/eventCreationTool'))
sys.path.append(os.path.abspath('../../07-logStore/src'))

import EventCreationTool
from logStore.appconn.feed_ctrl_connection import FeedCtrlConnection
from .eventCreationWrapper import EventCreationWrapper


class UiFunctionHandler:

    def __init__(self):
        self._dbConn = FeedCtrlConnection()
        lastEvent = self._dbConn.get_my_last_event()
        if lastEvent == None:
            _eventFactory = EventCreationTool.EventFactory()
        else:
            self._eventFactory = EventCreationTool.EventFactory(lastEvent)
        self._masterID = self._dbConn.get_host_masterID()
        self._eventCreationWrapper = EventCreationWrapper(self._eventFactory)


    def get_host_master_id(self):
        #returns the host masterID
        return self._masterID

    def get_master_ids(self):
        # return list of masterIDs from FeedCtrlConnection
        return self._dbConn.get_all_master_ids()

    def get_all_master_ids_feed_ids(self,masterID):
        # return a list of feedIDs which belong to the given masterID
        return self._dbConn.get_all_master_ids_feed_ids(masterID)

    def get_radius_list(self):
        # return a list of feedIDs which are inside the radius
        return self._dbConn.get_feed_ids_in_radius()

    def get_trusted(self):
        # return a list of trusted feedIDs
        return self._dbConn.get_trusted(self._masterID)

    def set_trusted(self, feedID, bool):
        # sets a feed to trusted or untrusted (event)
        if bool:
            newEvent = self._eventCreationWrapper.create_trust(feedID)
        else:
            newEvent = self._eventCreationWrapper.create_untrust(feedID)

        self._dbConn.add_event(newEvent)

    def get_blocked(self):
        # return a list of blocked feedIDs
        return self._dbConn.get_blocked(self._masterID)

    def set_blocked(self,feedID, bool):
        # sets a feed to blocked or unblocked
        if bool:
            newEvent = self._eventCreationWrapper.create_block(feedID)
            if feedID in self._dbConn.get_trusted(self._masterID):
                self._dbConn.add_event(self._eventCreationWrapper.create_untrust(feedID))
        else:
            newEvent = self._eventCreationWrapper.create_unblock(feedID)
        self._dbConn.add_event(newEvent)

    def get_radius(self):
        # return the current radius
        return self._dbConn.get_radius()

    def set_radius(self, radius):
        # sets the new radius
        # calls calcRadius() to recalculate the new Elements, which are in the radius
        newEvent = self._eventCreationWrapper.create_radius(radius)
        self._dbConn.add_event(newEvent)

    def get_username(self, masterID):
        # return username from given masterID
        return self._dbConn.get_username(masterID)

    def set_username(self, name):

        newEvent = self._eventCreationWrapper.create_name(name)
        self._dbConn.add_event(newEvent)

    def get_application(self, feedID):
        # return applicationname from given feedID
        return self._dbConn.get_application_name(feedID)