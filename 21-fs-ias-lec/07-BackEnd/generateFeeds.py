import sys
sys.path.append("lib")

from Feed import Feed
from FollowList import FollowList

# set a name to a feed
yasmin = Feed.Feed("yasmin")
esther = Feed.Feed("esther")
vera = Feed.Feed("vera")

# Feed erstellen
yasmin.generateOwnFeed()
esther.generateOwnFeed()
vera.generateOwnFeed()

#Folgen in Feed eintragen
yasmin.writeFollowToFeed("esther")
esther.writeFollowToFeed("yasmin")
yasmin.writeFollowToFeed("vera")

#yasmin.readFollowFromFeed()
#esther.readFollowFromFeed()
#vera.readFollowFromFeed()

#Followliste zum feed erstellen
yasminsList = FollowList.FollowList(yasmin)
esthersList = FollowList.FollowList(esther)
verasList = FollowList.FollowList(vera)

# Die Listen auslesen und anzeigen
yasminsList.getList()
esthersList.getList()
verasList.getList()

