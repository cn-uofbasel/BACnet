from . import Feed
from .. import FollowList


def main():
    yasmin = Feed("yasmin")
    esther = Feed("esther")
    vera = Feed("vera")

    yasmin.generate()
    esther.generate()
    vera.generate()

    yasmin.writeFollowToFeed("esther")
    esther.writeFollowToFeed("yasmin")

    yasmin.readFollowFromFeed()
    esther.readFollowFromFeed()
    vera.readFollowFromFeed()

    yList = FollowList(yasmin)
    yList.getList()

