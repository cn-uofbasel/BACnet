from .. import Feed

class FollowList:

    def __init__(self, feed):
        self.feed = feed

    def getList(self):
        list = []
        list = self.feed.readFollowFromFeed()
        print(list)