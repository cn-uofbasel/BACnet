from .SqLiteConnector import SqLiteConnector, ConnectorNotOpenError
from functions.log import create_logger
from functions.Singleton import Singleton
from cbor2 import dumps, loads
import hashlib

logger = create_logger('ByteArrayHandler')


class ByteArrayHandler(metaclass=Singleton):
    __dbname = 'byteArrayDatabase'
    __tname = 'byteArrayTable'
    __initiated = False

    def __init__(self):
        self.__connector = SqLiteConnector()
        self.__connector.name_database(self.__dbname)
        self.__connector.start_database_connection()
        self.__connector.close_database_connection()
        self.__initiated = self.init_byte_obj_table()

    def init_byte_obj_table(self):
        try:
            self.__connector.start_database_connection()
            if not self.__connector.create_table(self.__tname, 'href text PRIMARY KEY', 'byteArray blob'):
                return False
            self.__connector.close_database_connection()
        except ConnectorNotOpenError:
            logger.error('Could not open the connection')
            return False
        return True

    def retrieve_byte_array(self, hashref):
        try:
            self.__connector.start_database_connection()
            result = self.__connector.search_in_table(self.__tname, 'href', hashref)
            self.__connector.close_database_connection()
            return result
        except ConnectorNotOpenError:
            return None

# TODO: change that byteArray will be saved by hash reference of previous object
    def insert_byte_array(self, byteArray):
        try:
            self.__connector.start_database_connection()
            e = loads(byteArray)
            href = hashlib.sha256(e[0].encode()).hexdigest()
            self.__connector.insert_byte_array(self.__tname, href, byteArray)
            self.__connector.commit_changes()
            self.__connector.close_database_connection()
        except ConnectorNotOpenError:
            return False
        return True

    def is_init(self):
        return self.__initiated