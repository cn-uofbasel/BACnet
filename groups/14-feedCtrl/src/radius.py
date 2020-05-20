import sys
import os
sys.path.append(os.path.abspath('../../07-logStore/src'))
from logStore.appconn.feed_ctrl_connection import FeedCtrlConnection

class Radius:

    def __init__(self):
        self._feedCtrlConnection = FeedCtrlConnection()
        self._radius = self._feedCtrlConnection.get_radius()
        self._hostID = self._feedCtrlConnection.get_host_master_id()
        self._trusted = self._feedCtrlConnection.get_trusted(self._hostID)