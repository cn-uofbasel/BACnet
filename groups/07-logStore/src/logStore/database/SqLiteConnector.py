import sqlite3
from functions.log import create_logger

logger = create_logger('SqLiteConnector')


class SqLiteConnector:

    def __init__(self):
        self.dn = 'stData'
        self.__connector = None
        self.__cursor = None

    def name_database(self, dname):
        self.dn = dname

    def start_database_connection(self):
        message = ('%s.db' % self.dn)
        self.__connector = sqlite3.connect(message)
        self.__cursor = self.__connector.cursor()

    def create_table(self, tname, *argv):
        if not self.__connector:
            raise ConnectorNotOpenError('while creating a table.')
        message = ('CREATE TABLE IF NOT EXISTS %s (' % tname)
        for arg in argv:
            if not isinstance(arg, str):
                logger.error('% is not a string' % arg)
                return False
            message += arg
            message += ', '
        message = message[:-2]
        message += ');'
        self.__cursor.execute(message)
        return True

    def insert_to_table(self, tname, *argv):
        if not self.__connector:
            raise ConnectorNotOpenError('while inserting into a table.')
        message = ('INSERT INTO %s VALUES(' % tname)
        for arg in argv:
            message += arg
            message += ', '
        message = message[:-2]
        message += ')'
        self.__cursor.execute(message)

    def commit_changes(self):
        if self.__connector:
            self.__connector.commit()

    def close_database_connection(self):
        if self.__connector:
            self.__connector.close()

    def remove_table(self, tname):
        self.__connector.execute('DROP TABLE IF EXISTS %s; ' % tname)

    def get_all_from_table(self, tname):
        self.__cursor.execute('SELECT * FROM %s;' % tname)

    def search_in_table(self, tname, typ, name):
        self.__cursor.execute('SELECT * FROM %s WHERE %s=%s;' % (tname, typ, name))
        return self.__cursor.fetchall()


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
