from Feed import Feed
from FollowList import FollowList

# set a name to a feed
yasmin = Feed("yasmin")
esther = Feed("esther")
vera = Feed("vera")

yasmin.generateOwnFeed()
esther.generateOwnFeed()
vera.generateOwnFeed()

yasmin.writeFollowToFeed("esther")
esther.writeFollowToFeed("yasmin")

yasmin.readFollowFromFeed()
esther.readFollowFromFeed()
vera.readFollowFromFeed()

yasminsList = FollowList(yasmin)
esthersList = FollowList(esther)
verasList = FollowList(vera)

yasminsList.getList()
esthersList.getList()
verasList.getList()

