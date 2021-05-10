import sys

sys.path.append("lib")

from Feed import Feed
from Person import Person


def main():

    # set a name to a feed
    yasmin = Feed.Feed("yasmin")
    esther = Feed.Feed("esther")
    vera = Feed.Feed("vera")

    # Feed erstellen
    yasmin.generateOwnFeed()
    esther.generateOwnFeed()
    vera.generateOwnFeed()

    # set person
    yasminPerson = Person.Person(yasmin.id, yasmin.name, yasmin)
    yasminPerson.follow(esther.id, esther.name)
    yasminPerson.follow(vera.id, vera.name)
    yasminPerson.printFollowList()
    yasminPerson.unfollow(vera.id)
    yasminPerson.printFollowList()

    veraPerson = Person.Person(vera.id, vera.name, vera)
    veraPerson.follow(esther.id, esther.name)
    veraPerson.follow(yasmin.id, yasmin.name)
    veraPerson.printFollowList()


if __name__ == "__main__":
    main()
