class FollowList(list):

    def __init__(self, feed):
        super().__init__()
        self.feed = feed
        self.name = feed.name

    def getList(self):
        followList = self.feed.readFollowFromFeed()
        print(self.name, ":", followList.__len__(), followList, '\n')

