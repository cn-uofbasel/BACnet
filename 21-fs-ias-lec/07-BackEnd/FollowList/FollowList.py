class FollowList(list):

    def __init__(self, feed):
        super().__init__()
        self.feed = feed
        self.name = feed.name

    def getList(self):
        print("build " + self.name + "'s list")
        followList = self.feed.readFollowFromFeed()
        print(self.name + "'s follow-list: ")
        for msg in followList:
            print(msg["Friend"])
            #print(msg["Root"] + " follows " + msg["Friend"])
        #print(self.name, ":", followList.__len__(), followList)

