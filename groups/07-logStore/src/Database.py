from .SqLiteConnector import SqLiteConnector
from.constants import DEFAULT_TABLE

class Database:

    def __init__(self):
        self.connector = SqLiteConnector()
        self.dn = 'stData'

    def create_database(self, dname):
        self.dn = dname
        self.connector.name_database(self.dn)
        self.connector.start_database_connection()
        self.connector.create_table('init_table', DEFAULT_TABLE)
        self.connector.close_database_connection()

    def insert_to_database(self, id, data):


