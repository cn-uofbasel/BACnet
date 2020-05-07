from functions.Singleton import Singleton
from .SqlAlchemyConnector import SqLiteDatabase
from functions.Constants import SQLITE


class EventHandler(metaclass=Singleton):

    def __init__(self):
        # self.__sqlAlchemyConnector = SqLiteDatabase(SQLITE, dbname='cborDatabase.sqlite')
        # self.__sqlAlchemyConnector.create_db_tables()
        pass

    def init_event_table(self):
        return False

    def add_event(self, byteArray):
        return False

    def get_event(self, hashref):
        pass

    def create_table_for_feed(self, feedId):
        pass

    def read_data_from_event(self, byteArray):
        pass