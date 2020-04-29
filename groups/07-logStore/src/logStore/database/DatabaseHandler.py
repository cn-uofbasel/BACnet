from .ByteArrayHandler import ByteArrayHandler
from .EventHandler import EventHandler


class DatabaseHandler:

    def __init__(self):
        self.__byteArrayHandler = ByteArrayHandler()
        self.__eventHandler = EventHandler()

    def add_to_db(self, byteArray):
        pass

    def get_byte_array(self, hashref):
        pass

    def verify_byte_array(self, byteArray):
        return False

    def sync_database(self):
        return False

