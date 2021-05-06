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
    yasminPerson.follow(0, esther.name)
    yasminPerson.follow(1, vera.name)
    yasminPerson.printFollowList()


if __name__ == "__main__":
    main()
