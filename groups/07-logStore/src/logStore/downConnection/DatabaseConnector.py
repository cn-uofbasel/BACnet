from database.DatabaseHandler import DatabaseHandler as dh


class DatabaseConnector:

    def __init__(self):
        self.__handler = dh()

    def add_byte_array(self, byteArray):
        if self.__handler.add_to_db(byteArray):
            return True

    def get_byte_array(self, hashref):
        return self.__handler.get_byte_array(hashref)