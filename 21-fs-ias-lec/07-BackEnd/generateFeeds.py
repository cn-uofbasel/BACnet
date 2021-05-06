import sys

sys.path.append("lib")

from Feed import Feed
from Person import Person


def main():

    # set a name to a feed
    yasminFeed = Feed.Feed("yasmin")
    esther = Feed.Feed("esther")
    vera = Feed.Feed("vera")

    # Feed erstellen
    yasminFeed.generateOwnFeed()
    esther.generateOwnFeed()
    vera.generateOwnFeed()

    # set person
    yasminPerson = Person.Person(yasminFeed.id, yasminFeed.name, yasminFeed)
    yasminPerson.follow(esther.id, esther.name)
    yasminPerson.follow(vera.id, vera.name)
    yasminPerson.printFollowList()
    yasminPerson.unfollow(vera.id)
    yasminPerson.printFollowList()


if __name__ == "__main__":
    main()
