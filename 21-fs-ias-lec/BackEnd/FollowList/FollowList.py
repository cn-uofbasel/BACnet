import sys
sys.path.append("BACnet/21-fs-ias-lec/BackEnd/Feed")
import Feed

class FollowList:

    def __init__(self, feed):
        self.feed = feed

    def getList(self):
        list = []
        list = self.feed.readFollowFromFeed()
        print(list)