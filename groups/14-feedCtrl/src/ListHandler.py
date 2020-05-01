from pathlib import Path

#helper class

class ListFile:
    
    def __init__(self, path):
        self._activated = True
        self._path = path
        self._cache = set()
        if Path(self._path).is_file():
            with open(self._path, "r") as f:
                self._cache = set(map(lambda x:x.rstrip("\n"), f.readlines()))

    def append(self, logID):
        #TODO: add log entry
        if not self.exists(logID):
            self._cache.add(logID)
            with open(self._path, "a") as f:
                f.write(logID + "\n")

    def remove(self, logID):
        #TODO: add log entry
        if self.exists(logID):
            self._cache.discard(logID)
            with open(self._path, "w") as f:
                f.writelines(self._cache)   

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


class FollowListFile(ListFile):
    def __init__(self, path):
        ListFile.__init__(self, path)
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



