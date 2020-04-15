import sqlite3


class SqLiteConnector:

    def __init__(self):
        self.dn = 'stData'
        self.connector = None
        self.cursor = None

    def name_database(self, dname):
        self.dn = dname

    def start_database_connection(self):
        self.connector = sqlite3.connect('{}.db'.format(self.dn))
        self.cursor = self.connector.cursor()

    def create_table(self, tname, table_formats):
        if not self.connector:
            raise ConnectorNotOpenError('while creating a table.')
        self.cursor.execute('CREATE TABLE IF NOT EXISTS {} {}'.format(tname, table_formats))

    def insert_to_table(self, tname, data):
        if not self.connector:
            raise ConnectorNotOpenError('while creating a table.')
        self.cursor.execute('INSERT INTO {} VALUES'.format(tname, data))

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
