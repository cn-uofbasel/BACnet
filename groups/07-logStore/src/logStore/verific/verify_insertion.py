from ..appconn.feed_ctrl_connection import FeedCtrlConnection

class Verification:
    def __init__(self):
        self._fcc = FeedCtrlConnection()
        self._hostid = self._fcc.get_host_master_id()

    def check_incoming(self, feed_id, app_name):
        # If the given feed is a master feed we will always accept it.
        if app_name == 'MASTER':
            return True
        else:
            trusted = set(self._fcc.get_trusted(self._hostid))
            blocked = set(self._fcc.get_blocked(self._hostid))
            # check if the feedID is trusted and not blocked
            if feed_id in trusted and feed_id not in blocked:
                return True
            return self._check_in_radius(feed_id, app_name)


    def check_outgoing(self, feed_id):
        # check if the feed_id is a master id.
        master = set(self._fcc.get_all_master_ids())
        blocked = set(self._fcc.get_blocked(self._hostid))
        if feed_id in master:
            return True
        # check if the feed_id is not blocked
        if feed_id in blocked:
            return False
        else:
            # check if the feed_id is trusted
            trusted = set(self._fcc.get_trusted(self._hostid))
            if feed_id in trusted:
                return True
            return self._check_in_radius(feed_id, self._fcc.get_application_name(feed_id))

    def _check_in_radius(self, feed_id, app_name):
        masterInRadius = set(self._fcc.get_feed_ids_in_radius())
        # check if the feed_id is inside the social radius
        for master in masterInRadius:
            feedIDs = set(self._fcc.get_trusted(master))
            for __feedID in feedIDs:
                if app_name == self._fcc.get_application_name(__feedID):
                    return True
        return False