from .SqLiteConnector import SqLiteConnector, ConnectorNotOpenError
from functions.log import create_logger
from functions.Singleton import Singleton
from functions.Event import Event, Meta

logger = create_logger('ByteArrayHandler')


class ByteArrayHandler(metaclass=Singleton):
    __dbname = 'cborFilesDatabase'
    __tname = 'cborTable'
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
            if not self.__connector.create_table(self.__tname, 'feed_id text', 'seq_no integer NOT NULL', 'event_as_cbor blob'):
                return False
            self.__connector.close_database_connection()
        except ConnectorNotOpenError:
            logger.error('Could not open the connection')
            return False
        return True

    def get_current_seq_no(self, feed_id):
        try:
            self.__connector.start_database_connection()
            result = self.__connector.get_current_seq_no(self.__tname, feed_id)
            self.__connector.close_database_connection()
            return result
        except ConnectorNotOpenError:
            return None

    def get_event(self, feed_id, seq_no):
        try:
            self.__connector.start_database_connection()
            result = self.__connector.get_event(self.__tname, feed_id, seq_no)
            self.__connector.close_database_connection()
            return result
        except ConnectorNotOpenError:
            return None

    def get_current_event_as_cbor(self, feed_id):
        try:
            self.__connector.start_database_connection()
            result = self.__connector.get_current_event_as_cbor(self.__tname, feed_id)
            if len(result) < 1:
                return None
            self.__connector.close_database_connection()

            self.__connector.start_database_connection()
            result = self.__connector.get_all_from_table(self.__tname)
            logger.debug(result)
            self.__connector.close_database_connection()
            return result[0]
        except ConnectorNotOpenError:
            return None

    def insert_byte_array(self, event_as_cbor):
        logger.debug('Inserting Element into the Table')
        try:
            self.__connector.start_database_connection()
            event = Event.from_cbor(event_as_cbor)
            seq_no = event.meta.seq_no
            feed_id = event.meta.feed_id.decode()
            self.__connector.insert_cbor_event(self.__tname, feed_id, seq_no, event_as_cbor)
            self.__connector.commit_changes()
            self.__connector.close_database_connection()
        except ConnectorNotOpenError:
            return False
        return True

    def is_init(self):
        return self.__initiated