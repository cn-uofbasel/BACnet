import sys

sys.path.append("lib")

from Feed import Feed
from FollowList import FollowList


def main():
    # set a name to a feed
    yasmin = Feed.Feed("yasmin")
    esther = Feed.Feed("esther")
    vera = Feed.Feed("vera")

    # Feed erstellen
    yasmin.generateOwnFeed()
    esther.generateOwnFeed()
    vera.generateOwnFeed()

    # Folgen in Feed eintragen
    yasmin.writeFollowToFeed("esther", 1)
    esther.writeFollowToFeed("yasmin", 2)
    yasmin.writeFollowToFeed("vera", 3)

    # yasmin.readFollowFromFeed()
    # esther.readFollowFromFeed()
    # vera.readFollowFromFeed()

    # Followliste zum feed erstellen
    yasminsList = FollowList.FollowList(yasmin)
    esthersList = FollowList.FollowList(esther)
    verasList = FollowList.FollowList(vera)

    # Die Listen auslesen und anzeigen
    yasminsList.getList()
    esthersList.getList()
    verasList.getList()

if __name__ == "__main__":
    main()
