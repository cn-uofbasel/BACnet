import sqlite3
from pathlib import Path

class WLDataBridge:

    def __init__(self, db, listname="whitelist"):
        self._activated = True
        self._db = db
        self._cache = set()
        self._list = listname
        
        if not Path(self._db).is_file():
            self._conn = sqlite3.connect(db)
            self._querry = self._conn.cursor()
            sql_comm = "CREATE TABLE " + self._list + " (LogID text, Name text, UNIQUE(LogID))"
            self._querry.execute(sql_comm)
        else:
            self._conn = sqlite3.connect(db)
            self._querry = self._conn.cursor()

        sql_comm = "SELECT LogID FROM " + self._list
        self._querry.execute(sql_comm)
        records = self._querry.fetchall()
        for row in records:
            self._cache.add(row[0])

    def append(self, logID, name=""):
        #TODO: add log entry
        if not self.exists(logID):
            if name == "":
                name = "u_"+logID
            params = (logID, name)
            sql_comm = "INSERT INTO " + self._list + " (LogID, Name) VALUES (?,?);"
            self._cache.add(logID)
            self._querry.execute(sql_comm, params)
            self._conn.commit()

    def remove(self, logID):
        #TODO: add log entry
        if self.exists(logID):
            self._cache.discard(logID)
            params = tuple([logID])
            sql_comm = "DELETE FROM " + self._list + " WHERE logID LIKE ?"
            self._querry.execute(sql_comm, params)
            self._conn.commit()

    def exists(self, logID):
        return logID in self._cache

    def set_state(self, state):
        self._activated = state

    def get_state(self):
        return self._activated

    def exists_or_ignored(self, logID):
        return not self._activated or self.exists(logID)
    
    def get_data(self):
        return list(self._cache)

class FLDataBridge(WLDataBridge):
    def __init__(self, db):
        WLDataBridge.__init__(self, db, "followlist")
        self._radius = 1
        self._rad_cache = set()

    def set_radius(self, radius):
        self._radius = radius

    def get_radius(self):
        return self._radius

    def update_radius_list(self):
        #TODO: check log entries
        pass

    def exists_in_radius_or_ignored(self, logID):
        return logID in self._rad_cache or self.exists_or_ignored(logID)

    def get_radius_data(self):
        return list(self._rad_cache)

