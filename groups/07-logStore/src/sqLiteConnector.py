import sqlite3


class SqliteConnector:

    def __init__(self, dname):
        self.dn = dname
        self.connector = None
        self.cursor = None

    def start_database_connection(self):
        self.connector = sqlite3.connect('{}.db'.format(self.dn))
        self.cursor = self.connector.cursor()

    def create_table(self, tname, table_format):
        if not self.connector:
            raise ConnectorNotOpenError('while creating a table.')
        table_format = (tname, table_format)
        self.cursor.execute('CREATE TABLE ? ?)', table_format)

    def insert_to_table(self, tname, data):
        if not self.connector:
            raise ConnectorNotOpenError('while creating a table.')
        self.cursor.execute('INSERT INTO ? VALUES',(tname, data))

    def commit_changes(self):
        if self.connector:
            self.connector.commit()

    def close_database_connection(self):
        if self.connector:
            self.connector.close()


class ConnectorNotOpenError(Exception):
    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None

    def __str__(self):
        if self.message:
            return 'Connector to Database not open, {0}'.format(self.message)
        else:
            return 'Connector to Database not open'
