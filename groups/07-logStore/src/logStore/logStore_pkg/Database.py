from .SqLiteConnector import SqLiteConnector
from .constants import DEFAULT_TABLE


class Database:
    __connector = None

    def __init__(self):
        self.__connector = SqLiteConnector()
        self.dn = 'stData'

    def create_database(self, dname):
        self.dn = dname
        self.__connector.name_database(self.dn)
        self.__connector.start_database_connection()
        self.__connector.create_table('init_table')
        self.__connector.close_database_connection()

    def insert_to_database(self, id, data):
        pass

