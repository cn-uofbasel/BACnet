import sqlite3
from functions.log import create_logger

logger = create_logger('SqLiteConnector')


class SqLiteConnector:

    def __init__(self):
        self.dn = 'stData'
        self.__connector = None
        self.__cursor = None
        # Note to Moritz: Add here the tables you need:
        self.__legal_tables = {
            'byteArrayTable': True
        }

    def name_database(self, dname):
        self.dn = dname

    def start_database_connection(self):
        message = ('%s.db' % self.dn)
        self.__connector = sqlite3.connect(message)
        self.__cursor = self.__connector.cursor()

    def create_table(self, tname, *argv):
        if not self.__legal_tables.get(tname):
            return False
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
        self.__connector.execute(message)
        return True

# TODO: Implement custom insert method for event handler
    def insert_to_table(self, tname, *argv):
        if not self.__connector:
            raise ConnectorNotOpenError('while inserting into a table.')
        message = ('INSERT INTO %s VALUES(' % tname)
        for arg in argv:
            if isinstance(arg, bytes):
                arg = arg.decode('utf-8', errors='replace')
            message += '\'' + arg + '\''
            message += ', '
        message = message[:-2]
        message += ')'
        self.__connector.execute(message)

    def insert_byte_array(self, tname, href, byteArray):
        if not self.__legal_tables.get(tname):
            return False
        if not self.__connector:
            raise ConnectorNotOpenError('while inserting into a table.')
        sql = ''' INSERT INTO %s(href,byteArray)
                      VALUES(?,?); ''' % tname
        try:
            self.__connector.execute(sql, (href, memoryview(byteArray)))
        except sqlite3.IntegrityError:
            logger.error('Already in the database')
            return False
        return True

    def commit_changes(self):
        if self.__connector:
            self.__connector.commit()

    def close_database_connection(self):
        if self.__connector:
            self.__connector.close()

    def remove_table(self, tname):
        if not self.__legal_tables.get(tname):
            return False
        self.__connector.execute('DROP TABLE IF EXISTS %s; ' % tname)
        return True

    def get_all_from_table(self, tname):
        if not self.__legal_tables.get(tname):
            return None
        return self.__cursor.execute('SELECT * FROM %s;' % tname)

    def search_in_table(self, tname, typ, name):
        if not self.__legal_tables.get(tname):
            return None
        self.__cursor.execute("SELECT * from %s WHERE %s = ?" % (tname, typ), (name,))
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
