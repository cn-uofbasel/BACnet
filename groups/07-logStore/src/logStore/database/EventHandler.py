from .SqLiteConnector import SqLiteConnector
from functions.Singleton import Singleton


class EventHandler(metaclass=Singleton):

    def __init__(self):
        self.__connector = SqLiteConnector()

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