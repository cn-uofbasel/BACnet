from unittest import TestCase
from logStore_pkg.Database import Database


def main():
    db = Database()
    db.create_database('TestDatabase')



if __name__ == '__main__':
    main()