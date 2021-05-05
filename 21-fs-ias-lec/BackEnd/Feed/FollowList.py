class FollowList(list):
    followList = dict({})

    def __init__(self, feed):
        super().__init__()
        self.feed = feed
        self.name = feed.name

    def getList(self):
        list = self.feed.readFollowFromFeed()
        print(self.name, ":", self.getSize(), list, '\n')

    # def alreadyFollowFriend(self, friendsName):
    #    namelist =
    #    for all names in
    #    return True

    # gibt immer 56 aus.. noch nicht korrekt
    def getSize(self):
        return list.__sizeof__(self)
